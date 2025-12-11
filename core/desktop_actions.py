# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""تعریف اقدامات Desktop برای اتوماسیون رابط کاربری.

این ماژول شامل کلاس‌های Action برای تعامل با Desktop است:
- ClickAction: کلیک روی عناصر UI
- TypeAction: تایپ متن در فیلدها
- WaitAction: انتظار هوشمند
- DragDropAction: کشیدن و رها کردن
- HotkeyAction: فشردن ترکیب کلیدها
- ScrollAction: اسکرول صفحه
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Literal, Optional

from core.system_actions import ActionStatus, RiskLevel, SystemAction

logger = logging.getLogger(__name__)


# =============================================================================
# Click Actions
# =============================================================================

@dataclass
class ClickAction(SystemAction):
    """کلیک روی یک عنصر UI با استفاده از متن یا مختصات.
    
    Examples:
        >>> # کلیک روی متن
        >>> action = ClickAction(target="OK", button="left")
        >>> 
        >>> # کلیک روی مختصات
        >>> action = ClickAction(target=(100, 200), button="right")
    """
    
    target: str | tuple[int, int] | None = None
    """هدف کلیک: متن برای جستجو یا مختصات (x, y)"""
    
    button: Literal["left", "right", "middle"] = "left"
    """دکمه موس: left, right, middle"""
    
    clicks: int = 1
    """تعداد کلیک (1=single, 2=double)"""
    
    verify: bool = True
    """آیا بعد از کلیک نتیجه را تایید کنیم؟"""
    
    confidence: float = 0.8
    """حداقل اطمینان برای یافتن عنصر (0.0-1.0)"""
    
    timeout: int = 10
    """حداکثر زمان انتظار برای یافتن عنصر (ثانیه)"""
    
    def __post_init__(self):
        """بررسی target بعد از مقداردهی"""
        if self.target is None:
            raise ValueError("target الزامی است")
    
    def get_risk_level(self) -> RiskLevel:
        """کلیک معمولاً خطر کمی دارد."""
        # کلیک راست می‌تونه منوهای خطرناک باز کنه
        if self.button == "right":
            return RiskLevel.LOW
        
        # دابل کلیک می‌تونه برنامه باز کنه
        if self.clicks > 1:
            return RiskLevel.LOW
        
        return RiskLevel.SAFE
    
    def validate(self) -> tuple[bool, str]:
        """اعتبارسنجی پارامترهای کلیک."""
        # بررسی target
        if isinstance(self.target, tuple):
            x, y = self.target
            if not isinstance(x, int) or not isinstance(y, int):
                return False, "مختصات باید اعداد صحیح باشند"
            if x < 0 or y < 0:
                return False, "مختصات نمی‌توانند منفی باشند"
        elif isinstance(self.target, str):
            if not self.target.strip():
                return False, "متن هدف نمی‌تواند خالی باشد"
        else:
            return False, "target باید متن یا مختصات باشد"
        
        # بررسی button
        if self.button not in ["left", "right", "middle"]:
            return False, f"دکمه نامعتبر: {self.button}"
        
        # بررسی clicks
        if self.clicks < 1 or self.clicks > 3:
            return False, "تعداد کلیک باید بین 1 تا 3 باشد"
        
        # بررسی confidence
        if not 0.0 <= self.confidence <= 1.0:
            return False, "confidence باید بین 0.0 تا 1.0 باشد"
        
        # بررسی timeout
        if self.timeout < 1 or self.timeout > 60:
            return False, "timeout باید بین 1 تا 60 ثانیه باشد"
        
        return True, "معتبر است"
    
    def describe(self) -> str:
        """توضیح انسانی از اقدام."""
        target_desc = self.target if isinstance(self.target, str) else f"مختصات {self.target}"
        click_type = {1: "کلیک", 2: "دابل کلیک", 3: "تریپل کلیک"}[self.clicks]
        button_desc = {"left": "چپ", "right": "راست", "middle": "میانی"}[self.button]
        
        return f"{click_type} {button_desc} روی {target_desc}"


# =============================================================================
# Type Actions
# =============================================================================

@dataclass
class TypeAction(SystemAction):
    """تایپ متن در یک فیلد ورودی.
    
    Examples:
        >>> # تایپ در فیلد فعال
        >>> action = TypeAction(text="سلام دنیا")
        >>> 
        >>> # تایپ در فیلد خاص
        >>> action = TypeAction(text="example@email.com", target="Email")
    """
    
    text: str | None = None
    """متن برای تایپ"""
    
    target: Optional[str] = None
    """فیلد هدف (اگر None باشد، در فیلد فعال تایپ می‌شود)"""
    
    clear_first: bool = False
    """آیا ابتدا محتوای فیلد پاک شود؟"""
    
    interval: float = 0.05
    """تاخیر بین هر کاراکتر (ثانیه)"""
    
    verify: bool = True
    """آیا بعد از تایپ محتوا را تایید کنیم؟"""
    
    use_clipboard: bool = False
    """استفاده از clipboard برای سرعت بیشتر"""
    
    def __post_init__(self):
        """بررسی text بعد از مقداردهی"""
        if self.text is None:
            raise ValueError("text الزامی است")
    
    def get_risk_level(self) -> RiskLevel:
        """تایپ متن بسته به محتوا خطرناک می‌تواند باشد."""
        if self.text is None:
            return RiskLevel.LOW
        
        # بررسی محتوای مخرب
        dangerous_patterns = [
            r'rm\s+-rf',  # حذف فایل‌ها
            r'del\s+/[fqs]',  # حذف در ویندوز
            r'format\s+[a-z]:',  # فرمت دیسک
            r'shutdown',  # خاموش کردن
            r'reboot',  # ریستارت
        ]
        
        text_lower = self.text.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return RiskLevel.HIGH
        
        # محتوای حساس
        if any(keyword in text_lower for keyword in ['password', 'credit card', 'ssn']):
            return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def validate(self) -> tuple[bool, str]:
        """اعتبارسنجی پارامترهای تایپ."""
        # بررسی text
        if not isinstance(self.text, str):
            return False, "text باید رشته متنی باشد"
        
        if len(self.text) > 10000:
            return False, "متن بیش از حد طولانی است (حداکثر 10000 کاراکتر)"
        
        # بررسی target
        if self.target is not None:
            if not isinstance(self.target, str) or not self.target.strip():
                return False, "target باید رشته غیرخالی باشد"
        
        # بررسی interval
        if self.interval < 0 or self.interval > 1:
            return False, "interval باید بین 0 تا 1 ثانیه باشد"
        
        return True, "معتبر است"
    
    def describe(self) -> str:
        """توضیح انسانی از اقدام."""
        target_desc = f" در {self.target}" if self.target else ""
        text = self.text or ""
        text_preview = text[:50] + "..." if len(text) > 50 else text
        
        return f"تایپ '{text_preview}'{target_desc}"


# =============================================================================
# Wait Actions
# =============================================================================

@dataclass
class WaitAction(SystemAction):
    """انتظار هوشمند برای شرایط مختلف.
    
    Examples:
        >>> # انتظار برای ظاهر شدن عنصر
        >>> action = WaitAction(wait_type="element", target="Save Button")
        >>> 
        >>> # انتظار زمان‌دار
        >>> action = WaitAction(wait_type="time", duration=5.0)
    """
    
    wait_type: Literal["element", "change", "window", "process", "time"] | None = None
    """نوع انتظار: element, change, window, process, time"""
    
    target: Optional[str | int | tuple] = None
    """هدف انتظار (بسته به نوع)"""
    
    timeout: int = 30
    """حداکثر زمان انتظار (ثانیه)"""
    
    check_interval: float = 0.5
    """فاصله بررسی (ثانیه)"""
    
    inverse: bool = False
    """انتظار برای ناپدید شدن به جای ظاهر شدن"""
    
    def __post_init__(self):
        """بررسی wait_type بعد از مقداردهی"""
        if self.wait_type is None:
            raise ValueError("wait_type الزامی است")
    
    def get_risk_level(self) -> RiskLevel:
        """انتظار کردن خطری ندارد."""
        return RiskLevel.SAFE
    
    def validate(self) -> tuple[bool, str]:
        """اعتبارسنجی پارامترهای انتظار."""
        # بررسی wait_type
        valid_types = ["element", "change", "window", "process", "time"]
        if self.wait_type not in valid_types:
            return False, f"wait_type باید یکی از {valid_types} باشد"
        
        # بررسی target
        if self.wait_type == "time":
            if self.target is not None and not isinstance(self.target, (int, float)):
                return False, "target برای wait_type='time' باید عدد باشد"
        elif self.wait_type == "change":
            if self.target is not None and not isinstance(self.target, tuple):
                return False, "target برای wait_type='change' باید مختصات ناحیه باشد"
        else:
            if not self.target:
                return False, f"target برای wait_type='{self.wait_type}' الزامی است"
        
        # بررسی timeout
        if self.timeout < 1 or self.timeout > 300:
            return False, "timeout باید بین 1 تا 300 ثانیه باشد"
        
        # بررسی check_interval
        if self.check_interval < 0.1 or self.check_interval > 10:
            return False, "check_interval باید بین 0.1 تا 10 ثانیه باشد"
        
        return True, "معتبر است"
    
    def describe(self) -> str:
        """توضیح انسانی از اقدام."""
        if self.wait_type is None:
            return "انتظار (نامشخص)"
        
        type_desc = {
            "element": "عنصر",
            "change": "تغییر",
            "window": "پنجره",
            "process": "فرآیند",
            "time": "زمان"
        }[self.wait_type]
        
        action_verb = "ناپدید شدن" if self.inverse else "ظاهر شدن"
        
        if self.wait_type == "time":
            return f"انتظار {self.target} ثانیه"
        else:
            return f"انتظار برای {action_verb} {type_desc}: {self.target}"


# =============================================================================
# Drag & Drop Actions
# =============================================================================

@dataclass
class DragDropAction(SystemAction):
    """کشیدن و رها کردن یک عنصر.
    
    Examples:
        >>> # کشیدن فایل به پوشه
        >>> action = DragDropAction(source="file.txt", target="Documents")
        >>> 
        >>> # کشیدن با مختصات
        >>> action = DragDropAction(source=(100, 100), target=(500, 500))
    """
    
    source: str | tuple[int, int] | None = None
    """مبدا: متن یا مختصات"""
    
    target: str | tuple[int, int] | None = None
    """مقصد: متن یا مختصات"""
    
    duration: float = 0.5
    """مدت زمان حرکت (ثانیه)"""
    
    verify: bool = True
    """آیا نتیجه را تایید کنیم؟"""
    
    button: Literal["left", "right", "middle"] = "left"
    """دکمه موس برای کشیدن"""
    
    def __post_init__(self):
        """بررسی source و target بعد از مقداردهی"""
        if self.source is None:
            raise ValueError("source الزامی است")
        if self.target is None:
            raise ValueError("target الزامی است")
    
    def get_risk_level(self) -> RiskLevel:
        """Drag & Drop می‌تواند خطرناک باشد (مثلاً انتقال فایل)."""
        return RiskLevel.MEDIUM
    
    def validate(self) -> tuple[bool, str]:
        """اعتبارسنجی پارامترهای drag & drop."""
        # بررسی source
        if isinstance(self.source, tuple):
            x, y = self.source
            if not isinstance(x, int) or not isinstance(y, int):
                return False, "مختصات source باید اعداد صحیح باشند"
            if x < 0 or y < 0:
                return False, "مختصات source نمی‌توانند منفی باشند"
        elif isinstance(self.source, str):
            if not self.source.strip():
                return False, "متن source نمی‌تواند خالی باشد"
        else:
            return False, "source باید متن یا مختصات باشد"
        
        # بررسی target
        if isinstance(self.target, tuple):
            x, y = self.target
            if not isinstance(x, int) or not isinstance(y, int):
                return False, "مختصات target باید اعداد صحیح باشند"
            if x < 0 or y < 0:
                return False, "مختصات target نمی‌توانند منفی باشند"
        elif isinstance(self.target, str):
            if not self.target.strip():
                return False, "متن target نمی‌تواند خالی باشد"
        else:
            return False, "target باید متن یا مختصات باشد"
        
        # بررسی duration
        if self.duration < 0.1 or self.duration > 5:
            return False, "duration باید بین 0.1 تا 5 ثانیه باشد"
        
        # بررسی button
        if self.button not in ["left", "right", "middle"]:
            return False, f"دکمه نامعتبر: {self.button}"
        
        return True, "معتبر است"
    
    def describe(self) -> str:
        """توضیح انسانی از اقدام."""
        source_desc = self.source if isinstance(self.source, str) else f"مختصات {self.source}"
        target_desc = self.target if isinstance(self.target, str) else f"مختصات {self.target}"
        
        return f"کشیدن {source_desc} به {target_desc}"


# =============================================================================
# Hotkey Actions
# =============================================================================

@dataclass
class HotkeyAction(SystemAction):
    """فشردن ترکیب کلیدها (میانبر).
    
    Examples:
        >>> # کپی
        >>> action = HotkeyAction(keys=["ctrl", "c"])
        >>> 
        >>> # تعویض پنجره
        >>> action = HotkeyAction(keys=["alt", "tab"])
    """
    
    keys: list[str] | None = None
    """لیست کلیدها به ترتیب (مثل ["ctrl", "c"])"""
    
    interval: float = 0.1
    """تاخیر بین فشردن کلیدها (ثانیه)"""
    
    hold_duration: float = 0.0
    """مدت نگه داشتن (ثانیه)"""
    
    def __post_init__(self):
        """بررسی keys بعد از مقداردهی"""
        if self.keys is None:
            raise ValueError("keys الزامی است")
    
    def get_risk_level(self) -> RiskLevel:
        """برخی میانبرها خطرناک هستند."""
        if self.keys is None:
            return RiskLevel.LOW
        
        # میانبرهای خطرناک
        dangerous_combos = [
            ["alt", "f4"],  # بستن برنامه
            ["ctrl", "alt", "delete"],  # Task Manager
            ["win", "l"],  # قفل کردن
            ["win", "r"],  # Run dialog
        ]
        
        keys_lower = [k.lower() for k in self.keys]
        for combo in dangerous_combos:
            if keys_lower == combo:
                return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def validate(self) -> tuple[bool, str]:
        """اعتبارسنجی پارامترهای hotkey."""
        # بررسی keys
        if not self.keys or len(self.keys) < 1:
            return False, "حداقل یک کلید لازم است"
        
        if len(self.keys) > 4:
            return False, "حداکثر 4 کلید مجاز است"
        
        for key in self.keys:
            if not isinstance(key, str) or not key.strip():
                return False, "هر کلید باید رشته غیرخالی باشد"
        
        # بررسی interval
        if self.interval < 0 or self.interval > 1:
            return False, "interval باید بین 0 تا 1 ثانیه باشد"
        
        # بررسی hold_duration
        if self.hold_duration < 0 or self.hold_duration > 10:
            return False, "hold_duration باید بین 0 تا 10 ثانیه باشد"
        
        return True, "معتبر است"
    
    def describe(self) -> str:
        """توضیح انسانی از اقدام."""
        keys = self.keys or []
        keys_display = " + ".join(keys)
        return f"فشردن {keys_display}"


# =============================================================================
# Scroll Actions
# =============================================================================

@dataclass
class ScrollAction(SystemAction):
    """اسکرول صفحه یا عنصر.
    
    Examples:
        >>> # اسکرول به پایین
        >>> action = ScrollAction(direction="down", clicks=5)
        >>> 
        >>> # اسکرول در عنصر خاص
        >>> action = ScrollAction(direction="up", clicks=3, target="List")
    """
    
    direction: Literal["up", "down", "left", "right"] | None = None
    """جهت اسکرول"""
    
    clicks: int = 3
    """تعداد کلیک اسکرول (شدت)"""
    
    target: Optional[str | tuple[int, int]] = None
    """عنصر یا مختصات هدف (None = موقعیت فعلی موس)"""
    
    smooth: bool = False
    """اسکرول نرم و تدریجی"""
    
    def __post_init__(self):
        """بررسی direction بعد از مقداردهی"""
        if self.direction is None:
            raise ValueError("direction الزامی است")
    
    def get_risk_level(self) -> RiskLevel:
        """اسکرول خطری ندارد."""
        return RiskLevel.SAFE
    
    def validate(self) -> tuple[bool, str]:
        """اعتبارسنجی پارامترهای اسکرول."""
        # بررسی direction
        if self.direction not in ["up", "down", "left", "right"]:
            return False, f"جهت نامعتبر: {self.direction}"
        
        # بررسی clicks
        if self.clicks < 1 or self.clicks > 20:
            return False, "clicks باید بین 1 تا 20 باشد"
        
        # بررسی target
        if self.target is not None:
            if isinstance(self.target, tuple):
                x, y = self.target
                if not isinstance(x, int) or not isinstance(y, int):
                    return False, "مختصات target باید اعداد صحیح باشند"
                if x < 0 or y < 0:
                    return False, "مختصات target نمی‌توانند منفی باشند"
            elif isinstance(self.target, str):
                if not self.target.strip():
                    return False, "متن target نمی‌تواند خالی باشد"
            else:
                return False, "target باید None، متن یا مختصات باشد"
        
        return True, "معتبر است"
    
    def describe(self) -> str:
        """توضیح انسانی از اقدام."""
        if self.direction is None:
            return "اسکرول (نامشخص)"
        
        direction_fa = {
            "up": "بالا",
            "down": "پایین",
            "left": "چپ",
            "right": "راست"
        }[self.direction]
        
        target_desc = ""
        if self.target:
            if isinstance(self.target, str):
                target_desc = f" در {self.target}"
            else:
                target_desc = f" در مختصات {self.target}"
        
        return f"اسکرول {direction_fa} ({self.clicks} کلیک){target_desc}"


# =============================================================================
# Utility Functions
# =============================================================================

def create_action_from_dict(data: dict[str, Any]) -> SystemAction:
    """ایجاد Action از دیکشنری.
    
    Args:
        data: دیکشنری شامل type و سایر پارامترها
        
    Returns:
        نمونه‌ای از کلاس Action مناسب
        
    Raises:
        ValueError: اگر type نامعتبر باشد
    """
    action_map = {
        "click": ClickAction,
        "type": TypeAction,
        "wait": WaitAction,
        "drag_drop": DragDropAction,
        "hotkey": HotkeyAction,
        "scroll": ScrollAction,
    }
    
    action_type = data.pop("type", None)
    if action_type not in action_map:
        raise ValueError(f"نوع Action نامعتبر: {action_type}")
    
    return action_map[action_type](**data)


def serialize_action(action: SystemAction) -> dict[str, Any]:
    """تبدیل Action به دیکشنری.
    
    Args:
        action: نمونه Action
        
    Returns:
        دیکشنری شامل type و تمام فیلدها
    """
    # نقشه معکوس
    type_map = {
        ClickAction: "click",
        TypeAction: "type",
        WaitAction: "wait",
        DragDropAction: "drag_drop",
        HotkeyAction: "hotkey",
        ScrollAction: "scroll",
    }
    
    action_type = type_map.get(type(action))
    if not action_type:
        raise ValueError(f"نوع Action ناشناخته: {type(action)}")
    
    # تبدیل به دیکشنری
    result = {"type": action_type}
    result.update(action.__dict__)
    
    return result
