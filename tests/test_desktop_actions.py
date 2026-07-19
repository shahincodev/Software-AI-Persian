# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""تست‌های واحد برای desktop_actions.

این ماژول شامل تست‌های جامع برای تمام کلاس‌های Action است.
"""

import pytest

from core.desktop_actions import (
    ClickAction,
    DragDropAction,
    HotkeyAction,
    ScrollAction,
    TypeAction,
    WaitAction,
    create_action_from_dict,
    serialize_action,
)
from core.system_actions import RiskLevel


# =============================================================================
# ClickAction Tests
# =============================================================================

class TestClickAction:
    """تست‌های کلاس ClickAction"""
    
    def test_click_with_text_target(self):
        """تست کلیک با هدف متنی"""
        action = ClickAction(target="OK")
        
        assert action.target == "OK"
        assert action.button == "left"
        assert action.clicks == 1
        
        is_valid, msg = action.validate()
        assert is_valid
        assert "OK" in action.describe()
    
    def test_click_with_coordinates(self):
        """تست کلیک با مختصات"""
        action = ClickAction(target=(100, 200))
        
        assert action.target == (100, 200)
        is_valid, msg = action.validate()
        assert is_valid
        assert "مختصات" in action.describe()
    
    def test_double_click(self):
        """تست دابل کلیک"""
        action = ClickAction(target="File", clicks=2)
        
        assert action.clicks == 2
        is_valid, msg = action.validate()
        assert is_valid
        assert "دابل" in action.describe()
    
    def test_right_click(self):
        """تست کلیک راست"""
        action = ClickAction(target="Desktop", button="right")
        
        assert action.button == "right"
        assert action.get_risk_level() == RiskLevel.LOW  # کلیک راست خطر بیشتری داره
        assert "راست" in action.describe()
    
    def test_invalid_coordinates_negative(self):
        """تست مختصات منفی نامعتبر"""
        action = ClickAction(target=(-10, 20))
        
        is_valid, msg = action.validate()
        assert not is_valid
        assert "منفی" in msg
    
    def test_invalid_coordinates_type(self):
        """تست نوع مختصات نامعتبر"""
        action = ClickAction(target=(10.5, 20.3))
        
        is_valid, msg = action.validate()
        assert not is_valid
        assert "صحیح" in msg
    
    def test_invalid_empty_text(self):
        """تست متن خالی نامعتبر"""
        action = ClickAction(target="   ")
        
        is_valid, msg = action.validate()
        assert not is_valid
        assert "خالی" in msg
    
    def test_invalid_button(self):
        """تست دکمه نامعتبر"""
        action = ClickAction(target="OK", button="invalid")
        
        is_valid, msg = action.validate()
        assert not is_valid
        assert "نامعتبر" in msg
    
    def test_invalid_clicks_count(self):
        """تست تعداد کلیک نامعتبر"""
        action = ClickAction(target="OK", clicks=5)
        
        is_valid, msg = action.validate()
        assert not is_valid
    
    def test_invalid_confidence(self):
        """تست confidence نامعتبر"""
        action = ClickAction(target="OK", confidence=1.5)
        
        is_valid, msg = action.validate()
        assert not is_valid
    
    def test_invalid_timeout(self):
        """تست timeout نامعتبر"""
        action = ClickAction(target="OK", timeout=100)
        
        is_valid, msg = action.validate()
        assert not is_valid


# =============================================================================
# TypeAction Tests
# =============================================================================

class TestTypeAction:
    """تست‌های کلاس TypeAction"""
    
    def test_type_simple_text(self):
        """تست تایپ متن ساده"""
        action = TypeAction(text="Hello World")
        
        assert action.text == "Hello World"
        is_valid, msg = action.validate()
        assert is_valid
        assert "Hello" in action.describe()
    
    def test_type_persian_text(self):
        """تست تایپ متن فارسی"""
        action = TypeAction(text="سلام دنیا")
        
        assert action.text == "سلام دنیا"
        is_valid, msg = action.validate()
        assert is_valid
    
    def test_type_with_target(self):
        """تست تایپ در فیلد خاص"""
        action = TypeAction(text="test@example.com", target="Email")
        
        assert action.target == "Email"
        is_valid, msg = action.validate()
        assert is_valid
        assert "Email" in action.describe()
    
    def test_type_with_clear_first(self):
        """تست پاک کردن قبل از تایپ"""
        action = TypeAction(text="New Text", clear_first=True)
        
        assert action.clear_first is True
        is_valid, msg = action.validate()
        assert is_valid
    
    def test_type_with_clipboard(self):
        """تست استفاده از clipboard"""
        action = TypeAction(text="Long text...", use_clipboard=True)
        
        assert action.use_clipboard is True
        is_valid, msg = action.validate()
        assert is_valid
    
    def test_type_dangerous_command(self):
        """تست دستور خطرناک"""
        action = TypeAction(text="rm -rf /")
        
        risk = action.get_risk_level()
        assert risk == RiskLevel.HIGH  # دستور خطرناک
    
    def test_type_sensitive_content(self):
        """تست محتوای حساس"""
        action = TypeAction(text="password: 123456")
        
        risk = action.get_risk_level()
        assert risk == RiskLevel.MEDIUM  # محتوای حساس
    
    def test_invalid_text_type(self):
        """تست نوع متن نامعتبر"""
        action = TypeAction(text=12345)
        
        is_valid, msg = action.validate()
        assert not is_valid
    
    def test_invalid_text_too_long(self):
        """تست متن بیش از حد طولانی"""
        action = TypeAction(text="a" * 20000)
        
        is_valid, msg = action.validate()
        assert not is_valid
        assert "طولانی" in msg
    
    def test_invalid_target_empty(self):
        """تست target خالی"""
        action = TypeAction(text="test", target="   ")
        
        is_valid, msg = action.validate()
        assert not is_valid
    
    def test_invalid_interval(self):
        """تست interval نامعتبر"""
        action = TypeAction(text="test", interval=5)
        
        is_valid, msg = action.validate()
        assert not is_valid


# =============================================================================
# WaitAction Tests
# =============================================================================

class TestWaitAction:
    """تست‌های کلاس WaitAction"""
    
    def test_wait_for_element(self):
        """تست انتظار برای عنصر"""
        action = WaitAction(wait_type="element", target="Submit")
        
        assert action.wait_type == "element"
        assert action.target == "Submit"
        is_valid, msg = action.validate()
        assert is_valid
        assert "عنصر" in action.describe()
    
    def test_wait_for_window(self):
        """تست انتظار برای پنجره"""
        action = WaitAction(wait_type="window", target="Notepad")
        
        assert action.wait_type == "window"
        is_valid, msg = action.validate()
        assert is_valid
        assert "پنجره" in action.describe()
    
    def test_wait_for_time(self):
        """تست انتظار زمانی"""
        action = WaitAction(wait_type="time", target=5)
        
        assert action.wait_type == "time"
        assert action.target == 5
        is_valid, msg = action.validate()
        assert is_valid
        assert "5" in action.describe()
    
    def test_wait_for_change(self):
        """تست انتظار برای تغییر"""
        action = WaitAction(wait_type="change", target=(0, 0, 100, 100))
        
        assert action.wait_type == "change"
        is_valid, msg = action.validate()
        assert is_valid
    
    def test_wait_inverse(self):
        """تست انتظار برای ناپدید شدن"""
        action = WaitAction(wait_type="element", target="Loading", inverse=True)
        
        assert action.inverse is True
        assert "ناپدید" in action.describe()
    
    def test_wait_safe_risk_level(self):
        """تست سطح خطر انتظار"""
        action = WaitAction(wait_type="element", target="OK")
        
        assert action.get_risk_level() == RiskLevel.SAFE
    
    def test_invalid_wait_type(self):
        """تست نوع انتظار نامعتبر"""
        action = WaitAction(wait_type="invalid", target="test")
        
        is_valid, msg = action.validate()
        assert not is_valid
    
    def test_invalid_missing_target(self):
        """تست target گم شده"""
        action = WaitAction(wait_type="element", target=None)
        
        is_valid, msg = action.validate()
        assert not is_valid
        assert "الزامی" in msg
    
    def test_invalid_timeout(self):
        """تست timeout نامعتبر"""
        action = WaitAction(wait_type="element", target="OK", timeout=500)
        
        is_valid, msg = action.validate()
        assert not is_valid
    
    def test_invalid_check_interval(self):
        """تست check_interval نامعتبر"""
        action = WaitAction(wait_type="element", target="OK", check_interval=20)
        
        is_valid, msg = action.validate()
        assert not is_valid


# =============================================================================
# DragDropAction Tests
# =============================================================================

class TestDragDropAction:
    """تست‌های کلاس DragDropAction"""
    
    def test_drag_drop_with_text(self):
        """تست drag & drop با متن"""
        action = DragDropAction(source="file.txt", target="Documents")
        
        assert action.source == "file.txt"
        assert action.target == "Documents"
        is_valid, msg = action.validate()
        assert is_valid
        assert "file.txt" in action.describe()
        assert "Documents" in action.describe()
    
    def test_drag_drop_with_coordinates(self):
        """تست drag & drop با مختصات"""
        action = DragDropAction(source=(100, 100), target=(500, 500))
        
        assert action.source == (100, 100)
        assert action.target == (500, 500)
        is_valid, msg = action.validate()
        assert is_valid
        assert "مختصات" in action.describe()
    
    def test_drag_drop_mixed(self):
        """تست drag & drop ترکیبی"""
        action = DragDropAction(source="Icon", target=(800, 600))
        
        is_valid, msg = action.validate()
        assert is_valid
    
    def test_drag_drop_medium_risk(self):
        """تست سطح خطر drag & drop"""
        action = DragDropAction(source="file", target="trash")
        
        assert action.get_risk_level() == RiskLevel.MEDIUM
    
    def test_invalid_source_negative(self):
        """تست source منفی"""
        action = DragDropAction(source=(-10, 20), target="Desktop")
        
        is_valid, msg = action.validate()
        assert not is_valid
    
    def test_invalid_target_empty(self):
        """تست target خالی"""
        action = DragDropAction(source="file", target="")
        
        is_valid, msg = action.validate()
        assert not is_valid
    
    def test_invalid_duration(self):
        """تست duration نامعتبر"""
        action = DragDropAction(source="A", target="B", duration=10)
        
        is_valid, msg = action.validate()
        assert not is_valid


# =============================================================================
# HotkeyAction Tests
# =============================================================================

class TestHotkeyAction:
    """تست‌های کلاس HotkeyAction"""
    
    def test_hotkey_copy(self):
        """تست میانبر کپی"""
        action = HotkeyAction(keys=["ctrl", "c"])
        
        assert action.keys == ["ctrl", "c"]
        is_valid, msg = action.validate()
        assert is_valid
        assert "ctrl + c" in action.describe().lower()
    
    def test_hotkey_paste(self):
        """تست میانبر paste"""
        action = HotkeyAction(keys=["ctrl", "v"])
        
        is_valid, msg = action.validate()
        assert is_valid
    
    def test_hotkey_alt_tab(self):
        """تست تعویض پنجره"""
        action = HotkeyAction(keys=["alt", "tab"])
        
        is_valid, msg = action.validate()
        assert is_valid
    
    def test_hotkey_dangerous_combo(self):
        """تست میانبر خطرناک"""
        action = HotkeyAction(keys=["alt", "f4"])
        
        risk = action.get_risk_level()
        assert risk == RiskLevel.MEDIUM
    
    def test_hotkey_three_keys(self):
        """تست سه کلید"""
        action = HotkeyAction(keys=["ctrl", "shift", "esc"])
        
        is_valid, msg = action.validate()
        assert is_valid
    
    def test_invalid_empty_keys(self):
        """تست لیست خالی"""
        action = HotkeyAction(keys=[])
        
        is_valid, msg = action.validate()
        assert not is_valid
    
    def test_invalid_too_many_keys(self):
        """تست تعداد کلید زیاد"""
        action = HotkeyAction(keys=["a", "b", "c", "d", "e"])
        
        is_valid, msg = action.validate()
        assert not is_valid
    
    def test_invalid_empty_key(self):
        """تست کلید خالی"""
        action = HotkeyAction(keys=["ctrl", ""])
        
        is_valid, msg = action.validate()
        assert not is_valid


# =============================================================================
# ScrollAction Tests
# =============================================================================

class TestScrollAction:
    """تست‌های کلاس ScrollAction"""
    
    def test_scroll_down(self):
        """تست اسکرول به پایین"""
        action = ScrollAction(direction="down", clicks=5)
        
        assert action.direction == "down"
        assert action.clicks == 5
        is_valid, msg = action.validate()
        assert is_valid
        assert "پایین" in action.describe()
    
    def test_scroll_up(self):
        """تست اسکرول به بالا"""
        action = ScrollAction(direction="up", clicks=3)
        
        assert action.direction == "up"
        is_valid, msg = action.validate()
        assert is_valid
        assert "بالا" in action.describe()
    
    def test_scroll_with_target_text(self):
        """تست اسکرول در عنصر"""
        action = ScrollAction(direction="down", clicks=2, target="ListView")
        
        assert action.target == "ListView"
        is_valid, msg = action.validate()
        assert is_valid
        assert "ListView" in action.describe()
    
    def test_scroll_with_coordinates(self):
        """تست اسکرول در مختصات"""
        action = ScrollAction(direction="left", clicks=1, target=(400, 300))
        
        is_valid, msg = action.validate()
        assert is_valid
    
    def test_scroll_smooth(self):
        """تست اسکرول نرم"""
        action = ScrollAction(direction="down", clicks=5, smooth=True)
        
        assert action.smooth is True
        is_valid, msg = action.validate()
        assert is_valid
    
    def test_scroll_safe_risk(self):
        """تست سطح خطر اسکرول"""
        action = ScrollAction(direction="down", clicks=3)
        
        assert action.get_risk_level() == RiskLevel.SAFE
    
    def test_invalid_direction(self):
        """تست جهت نامعتبر"""
        action = ScrollAction(direction="diagonal", clicks=3)
        
        is_valid, msg = action.validate()
        assert not is_valid
    
    def test_invalid_clicks(self):
        """تست تعداد کلیک نامعتبر"""
        action = ScrollAction(direction="down", clicks=50)
        
        is_valid, msg = action.validate()
        assert not is_valid


# =============================================================================
# Serialization Tests
# =============================================================================

class TestSerialization:
    """تست‌های Serialization و Deserialization"""
    
    def test_serialize_click_action(self):
        """تست serialize کردن ClickAction"""
        action = ClickAction(target="OK", button="left")
        data = serialize_action(action)
        
        assert data["type"] == "click"
        assert data["target"] == "OK"
        assert data["button"] == "left"
    
    def test_deserialize_click_action(self):
        """تست deserialize کردن ClickAction"""
        data = {"type": "click", "target": "Cancel", "button": "right"}
        action = create_action_from_dict(data)
        
        assert isinstance(action, ClickAction)
        assert action.target == "Cancel"
        assert action.button == "right"
    
    def test_serialize_type_action(self):
        """تست serialize کردن TypeAction"""
        action = TypeAction(text="Hello", target="TextBox")
        data = serialize_action(action)
        
        assert data["type"] == "type"
        assert data["text"] == "Hello"
        assert data["target"] == "TextBox"
    
    def test_deserialize_type_action(self):
        """تست deserialize کردن TypeAction"""
        data = {"type": "type", "text": "سلام", "target": None}
        action = create_action_from_dict(data)
        
        assert isinstance(action, TypeAction)
        assert action.text == "سلام"
    
    def test_serialize_wait_action(self):
        """تست serialize کردن WaitAction"""
        action = WaitAction(wait_type="element", target="Submit")
        data = serialize_action(action)
        
        assert data["type"] == "wait"
        assert data["wait_type"] == "element"
    
    def test_deserialize_hotkey_action(self):
        """تست deserialize کردن HotkeyAction"""
        data = {"type": "hotkey", "keys": ["ctrl", "c"]}
        action = create_action_from_dict(data)
        
        assert isinstance(action, HotkeyAction)
        assert action.keys == ["ctrl", "c"]
    
    def test_roundtrip_serialization(self):
        """تست serialize و deserialize کامل"""
        original = DragDropAction(source="file.txt", target="Documents")
        data = serialize_action(original)
        restored = create_action_from_dict(data)
        
        assert isinstance(restored, DragDropAction)
        assert restored.source == original.source
        assert restored.target == original.target
    
    def test_invalid_action_type(self):
        """تست نوع Action نامعتبر"""
        data = {"type": "invalid_type", "param": "value"}
        
        with pytest.raises(ValueError):
            create_action_from_dict(data)


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """تست‌های یکپارچگی"""
    
    def test_all_actions_have_risk_level(self):
        """تست اینکه همه Action ها risk level دارند"""
        actions = [
            ClickAction(target="OK"),
            TypeAction(text="test"),
            WaitAction(wait_type="element", target="OK"),
            DragDropAction(source="A", target="B"),
            HotkeyAction(keys=["ctrl", "c"]),
            ScrollAction(direction="down", clicks=3),
        ]
        
        for action in actions:
            risk = action.get_risk_level()
            assert isinstance(risk, RiskLevel)
    
    def test_all_actions_can_validate(self):
        """تست اینکه همه Action ها قابل اعتبارسنجی هستند"""
        actions = [
            ClickAction(target="OK"),
            TypeAction(text="test"),
            WaitAction(wait_type="element", target="OK"),
            DragDropAction(source="A", target="B"),
            HotkeyAction(keys=["ctrl", "c"]),
            ScrollAction(direction="down", clicks=3),
        ]
        
        for action in actions:
            is_valid, msg = action.validate()
            assert is_valid
            assert isinstance(msg, str)
    
    def test_all_actions_can_describe(self):
        """تست اینکه همه Action ها قابل توضیح هستند"""
        actions = [
            ClickAction(target="OK"),
            TypeAction(text="test"),
            WaitAction(wait_type="element", target="OK"),
            DragDropAction(source="A", target="B"),
            HotkeyAction(keys=["ctrl", "c"]),
            ScrollAction(direction="down", clicks=3),
        ]
        
        for action in actions:
            desc = action.describe()
            assert isinstance(desc, str)
            assert len(desc) > 0
    
    def test_all_actions_serializable(self):
        """تست اینکه همه Action ها قابل serialize هستند"""
        actions = [
            ClickAction(target="OK"),
            TypeAction(text="test"),
            WaitAction(wait_type="element", target="OK"),
            DragDropAction(source="A", target="B"),
            HotkeyAction(keys=["ctrl", "c"]),
            ScrollAction(direction="down", clicks=3),
        ]
        
        for action in actions:
            data = serialize_action(action)
            assert "type" in data
            
            # بازیابی
            restored = create_action_from_dict(data)
            assert type(restored) is type(action)
