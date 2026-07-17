# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""کنترل هوشمند کیبورد با پشتیبانی کامل از فارسی و انگلیسی.

این ماژول یک سیستم پیشرفته برای کنترل کیبورد فراهم می‌کند که شامل:
- تایپ متن با تشخیص خودکار زبان (فارسی/انگلیسی)
- فشردن کلیدها و ترکیبات میانبر (Hotkeys)
- یکپارچگی با Clipboard
- اعتبارسنجی امنیتی
- شبیه‌سازی رفتار انسانی
- آمارگیری و Audit Trail

مثال:
    >>> from core.keyboard_control import KeyboardController
    >>> kb = KeyboardController()
    >>> kb.type_text("سلام دنیا")
    >>> kb.hotkey('ctrl', 'c')
"""

import time
import random
import logging
import unicodedata
from collections import deque
from enum import Enum
from typing import Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime

# Try importing required libraries
try:
    import pyautogui
except ImportError:
    raise ImportError(
        "pyautogui is required for keyboard control. "
        "Install with: pip install pyautogui"
    )

try:
    from pynput import keyboard as pynput_keyboard
except ImportError:
    pynput_keyboard = None
    logging.warning("pynput not available. Some features may be limited.")

try:
    import pyperclip
except ImportError:
    pyperclip = None
    logging.warning("pyperclip not available. Clipboard features disabled.")


logger = logging.getLogger(__name__)


__all__ = [
    "Language",
    "TypingSpeed",
    "KeyAction",
    "KeyboardAction",
    "KeyboardController",
    "is_persian_text",
    "Hotkeys",
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Enums
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Language(Enum):
    """زبان‌های پشتیبانی شده."""
    ENGLISH = "en"
    PERSIAN = "fa"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class TypingSpeed(Enum):
    """سرعت تایپ."""
    INSTANT = 0.0          # بدون تاخیر
    VERY_FAST = 0.01       # 100 کلمه در دقیقه
    FAST = 0.02            # 60 کلمه در دقیقه
    NORMAL = 0.05          # 40 کلمه در دقیقه
    SLOW = 0.1             # 20 کلمه در دقیقه
    VERY_SLOW = 0.2        # 10 کلمه در دقیقه


class KeyAction(Enum):
    """نوع اقدام کلید."""
    PRESS = "press"         # فشردن کوتاه
    HOLD = "hold"           # نگه داشتن
    RELEASE = "release"     # رها کردن
    TYPE = "type"           # تایپ متن
    HOTKEY = "hotkey"       # ترکیب کلیدها


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Data Classes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class KeyboardAction:
    """اطلاعات یک اقدام کیبورد برای Audit Trail."""
    action_type: str
    text: Optional[str] = None
    key: Optional[str] = None
    keys: Optional[List[str]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float = 0.0
    success: bool = False
    language: Optional[str] = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Main Controller
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class KeyboardController:
    """کنترلر هوشمند کیبورد با پشتیبانی AI.
    
    این کلاس قابلیت‌های پیشرفته برای کنترل کیبورد فراهم می‌کند:
    - تایپ متن با تشخیص زبان
    - فشردن کلیدها و Hotkeys
    - یکپارچگی Clipboard
    - رفتار انسانی
    - اعتبارسنجی امنیتی
    
    Args:
        safety_enabled: فعال‌سازی بررسی‌های امنیتی
        human_behavior: تقلید از رفتار انسانی (تاخیر، خطا)
        default_speed: سرعت پیش‌فرض تایپ
        
    Example:
        >>> kb = KeyboardController(human_behavior=True)
        >>> kb.type_text("سلام دنیا")
        >>> kb.hotkey('ctrl', 'c')
        >>> kb.press_key('enter')
    """
    
    def __init__(
        self,
        safety_enabled: bool = True,
        human_behavior: bool = True,
        default_speed: TypingSpeed = TypingSpeed.NORMAL,
    ):
        """مقداردهی اولیه KeyboardController."""
        self.safety_enabled = safety_enabled
        self.human_behavior = human_behavior
        self.default_speed = default_speed
        
        # آمار
        self.stats = {
            'total_keystrokes': 0,
            'total_text_typed': 0,
            'total_hotkeys': 0,
            'total_special_keys': 0,
            'failed_actions': 0,
            'total_actions': 0,
        }
        
        # Audit trail
        self.action_history: deque[KeyboardAction] = deque(maxlen=100)
        
        # Persian character mapping
        self.persian_chars = set(
            'ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'
            'ءآأؤإئًٌٍَُِّْٰ'
        )
        
        # Unsafe text patterns (برای امنیت)
        self.unsafe_patterns = [
            'rm -rf',
            'del /f',
            'format ',
            'DROP TABLE',
            'DROP DATABASE',
        ] if safety_enabled else []
        
        logger.info(
            "KeyboardController initialized: safety=%s, human=%s, speed=%s",
            safety_enabled, human_behavior, default_speed.name,
        )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Language Detection
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def detect_language(self, text: str) -> Language:
        """تشخیص زبان متن.
        
        Args:
            text: متن برای تحلیل
            
        Returns:
            Language enum
            
        Example:
            >>> kb.detect_language("Hello")
            Language.ENGLISH
            >>> kb.detect_language("سلام")
            Language.PERSIAN
            >>> kb.detect_language("Hello سلام")
            Language.MIXED
        """
        if not text:
            return Language.UNKNOWN
        
        # حذف فضاهای خالی و کاراکترهای خاص
        text_clean = ''.join(c for c in text if c.isalnum())
        
        if not text_clean:
            return Language.UNKNOWN
        
        # شمارش کاراکترهای فارسی و انگلیسی
        persian_count = sum(1 for c in text_clean if c in self.persian_chars)
        english_count = sum(1 for c in text_clean if c.isascii() and c.isalpha())
        
        total = persian_count + english_count
        if total == 0:
            return Language.UNKNOWN
        
        # محاسبه درصد
        persian_ratio = persian_count / total
        english_ratio = english_count / total
        
        # تصمیم‌گیری
        if persian_ratio > 0.7:
            return Language.PERSIAN
        elif english_ratio > 0.7:
            return Language.ENGLISH
        elif persian_ratio > 0.1 and english_ratio > 0.1:
            return Language.MIXED
        else:
            return Language.UNKNOWN
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Safety & Validation
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def is_safe_text(self, text: str) -> bool:
        """بررسی امن بودن متن.
        
        Args:
            text: متن برای بررسی
            
        Returns:
            True اگر متن امن باشد
        """
        if not self.safety_enabled:
            return True
        
        text_lower = text.lower()
        
        # بررسی الگوهای خطرناک
        for pattern in self.unsafe_patterns:
            if pattern.lower() in text_lower:
                logger.warning("Unsafe pattern detected: %s", pattern)
                return False
        
        # بررسی طول (جلوگیری از متن خیلی طولانی)
        if len(text) > 10000:
            logger.warning("Text too long: %d chars", len(text))
            return False
        
        return True
    
    def validate_text(self, text: str) -> str:
        """اعتبارسنجی و تصحیح متن.
        
        Args:
            text: متن ورودی
            
        Returns:
            متن تصحیح شده
            
        Raises:
            ValueError: اگر متن نامعتبر باشد
        """
        if not self.is_safe_text(text):
            raise ValueError(f"Unsafe text detected: {text[:50]}...")
        
        return text
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Human Behavior Simulation
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _get_typing_interval(
        self,
        speed: Optional[TypingSpeed] = None,
        char: str = ''
    ) -> float:
        """محاسبه فاصله زمانی بین کاراکترها.
        
        Args:
            speed: سرعت تایپ (None = default)
            char: کاراکتر فعلی (برای تنظیم دقیق‌تر)
            
        Returns:
            فاصله زمانی به ثانیه
        """
        if not self.human_behavior:
            return 0.0
        
        base_interval = (speed or self.default_speed).value
        
        if base_interval == 0.0:
            return 0.0
        
        # کاراکترهای خاص کمی بیشتر طول می‌کشند
        if char in [' ', '\n', '\t']:
            base_interval *= 1.5
        elif char in ['،', '.', '!', '?', '؛', '؟']:
            base_interval *= 2.0
        
        # نویز تصادفی ±30%
        variation = random.uniform(-0.3, 0.3)
        interval = base_interval * (1 + variation)
        
        return max(0.0, interval)
    
    def _simulate_typo(self, text: str) -> str:
        """شبیه‌سازی خطای تایپ (اختیاری).
        
        Args:
            text: متن اصلی
            
        Returns:
            متن با احتمال خطا
        """
        if not self.human_behavior:
            return text
        
        # 2% احتمال خطا
        if random.random() > 0.02:
            return text
        
        # انتخاب یک کاراکتر تصادفی برای تغییر
        if len(text) < 3:
            return text
        
        # برای سادگی، فقط لاگ می‌کنیم
        logger.debug("Typo simulation triggered (not implemented)")
        return text
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Core Typing Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def type_text(
        self,
        text: str,
        speed: Optional[TypingSpeed] = None,
        validate: bool = True,
        interval: Optional[float] = None,
    ) -> bool:
        """تایپ متن با تشخیص خودکار زبان.
        
        For ASCII text, types character-by-character with human-like timing.
        For Persian/Unicode text, uses clipboard paste (pyautogui.write cannot
        handle non-ASCII characters).
        
        Args:
            text: متن برای تایپ
            speed: سرعت تایپ (None = default)
            validate: فعال‌سازی اعتبارسنجی
            interval: فاصله زمانی بین کاراکترها (برای سازگاری)
            
        Returns:
            True اگر موفق باشد
            
        Example:
            >>> kb.type_text("Hello World")
            True
            >>> kb.type_text("سلام دنیا", speed=TypingSpeed.SLOW)
            True
        """
        start_time = time.time()
        action = KeyboardAction(
            action_type=KeyAction.TYPE.value,
            text=text
        )
        
        try:
            # اعتبارسنجی
            if validate:
                text = self.validate_text(text)
            
            # تشخیص زبان
            language = self.detect_language(text)
            action.language = language.value
            
            logger.debug("Typing text: '%s...' (lang=%s)", text[:50], language.name)
            
            # Use clipboard paste for non-ASCII text (Persian, etc.)
            # pyautogui.write() only supports ASCII characters
            has_non_ascii = any(ord(c) > 127 for c in text)
            
            if has_non_ascii:
                success = self.paste_text(text)
                if success:
                    self.stats['total_text_typed'] += len(text)
                    self.stats['total_actions'] += 1
                    self.stats['total_keystrokes'] += len(text)
                    action.success = True
                    logger.info("Typed %d chars via clipboard in %.2fs", len(text), time.time() - start_time)
                    return True
                else:
                    logger.warning("Clipboard paste failed, falling back to character-by-character")
            
            # Character-by-character typing for ASCII or clipboard fallback
            for char in text:
                char_interval = self._get_typing_interval(speed, char)
                
                if char_interval > 0:
                    time.sleep(char_interval)
                
                pyautogui.write(char, interval=0)
                self.stats['total_keystrokes'] += 1
            
            # به‌روزرسانی آمار
            self.stats['total_text_typed'] += len(text)
            self.stats['total_actions'] += 1
            action.success = True
            
            logger.info(
                "Typed %d chars in %.2fs",
                len(text), time.time() - start_time,
            )
            return True
            
        except Exception as e:
            logger.error("Failed to type text: %s", e)
            self.stats['failed_actions'] += 1
            self.stats['total_actions'] += 1
            action.success = False
            return False
            
        finally:
            action.duration = time.time() - start_time
            self._add_to_history(action)
    
    def press_key(
        self,
        key: str,
        presses: int = 1,
        interval: float = 0.1
    ) -> bool:
        """فشردن کلید.
        
        Args:
            key: نام کلید (مثل 'enter', 'space', 'esc')
            presses: تعداد فشردن
            interval: فاصله بین فشردن‌ها
            
        Returns:
            True اگر موفق باشد
            
        Example:
            >>> kb.press_key('enter')
            True
            >>> kb.press_key('tab', presses=3)
            True
        """
        start_time = time.time()
        action = KeyboardAction(
            action_type=KeyAction.PRESS.value,
            key=key
        )
        
        try:
            logger.debug("Pressing key: %s (x%d)", key, presses)
            
            for _ in range(presses):
                pyautogui.press(key)
                self.stats['total_special_keys'] += 1
                
                if presses > 1 and interval > 0:
                    time.sleep(interval)
            
            self.stats['total_actions'] += 1
            action.success = True
            return True
            
        except Exception as e:
            logger.error("Failed to press key '%s': %s", key, e)
            self.stats['failed_actions'] += 1
            self.stats['total_actions'] += 1
            action.success = False
            return False
            
        finally:
            action.duration = time.time() - start_time
            self._add_to_history(action)
    
    def hotkey(self, *keys: str) -> bool:
        """فشردن ترکیب کلیدها (Hotkey).
        
        Args:
            *keys: کلیدها به ترتیب (مثل 'ctrl', 'c')
            
        Returns:
            True اگر موفق باشد
            
        Example:
            >>> kb.hotkey('ctrl', 'c')  # کپی
            True
            >>> kb.hotkey('ctrl', 'shift', 's')  # ذخیره با نام
            True
            >>> kb.hotkey('alt', 'tab')  # تعویض پنجره
            True
        """
        start_time = time.time()
        action = KeyboardAction(
            action_type=KeyAction.HOTKEY.value,
            keys=list(keys)
        )
        
        try:
            keys_str = '+'.join(keys)
            logger.debug("Pressing hotkey: %s", keys_str)
            
            pyautogui.hotkey(*keys)
            
            self.stats['total_hotkeys'] += 1
            self.stats['total_actions'] += 1
            action.success = True
            return True
            
        except Exception as e:
            logger.error("Failed to press hotkey %s: %s", keys, e)
            self.stats['failed_actions'] += 1
            self.stats['total_actions'] += 1
            action.success = False
            return False
            
        finally:
            action.duration = time.time() - start_time
            self._add_to_history(action)
    
    def hold_key(self, key: str, duration: float = 1.0) -> bool:
        """نگه داشتن کلید.
        
        Args:
            key: نام کلید
            duration: مدت زمان نگه داشتن (ثانیه)
            
        Returns:
            True اگر موفق باشد
            
        Example:
            >>> kb.hold_key('shift', duration=2.0)
            True
        """
        start_time = time.time()
        action = KeyboardAction(
            action_type=KeyAction.HOLD.value,
            key=key
        )
        
        try:
            logger.debug("Holding key: %s for %.1fs", key, duration)
            
            pyautogui.keyDown(key)
            time.sleep(duration)
            pyautogui.keyUp(key)
            
            self.stats['total_special_keys'] += 1
            self.stats['total_actions'] += 1
            action.success = True
            return True
            
        except Exception as e:
            logger.error("Failed to hold key '%s': %s", key, e)
            self.stats['failed_actions'] += 1
            self.stats['total_actions'] += 1
            action.success = False
            return False
            
        finally:
            action.duration = time.time() - start_time
            self._add_to_history(action)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Clipboard Integration
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def paste_text(self, text: str) -> bool:
        """کپی متن به clipboard و paste کردن.
        
        This is the primary method for typing Persian/Unicode text since
        pyautogui.write() only supports ASCII characters.
        
        Args:
            text: متن برای paste
            
        Returns:
            True اگر موفق باشد
            
        Example:
            >>> kb.paste_text("متن طولانی...")
            True
        """
        if pyperclip is None:
            logger.warning("pyperclip not available, cannot paste non-ASCII text")
            return False
        
        try:
            # کپی به clipboard
            pyperclip.copy(text)
            
            # Paste با Ctrl+V
            time.sleep(0.1)
            return self.hotkey('ctrl', 'v')
            
        except Exception as e:
            logger.error("Failed to paste text: %s", e)
            return False
    
    def get_clipboard(self) -> Optional[str]:
        """دریافت محتوای clipboard.
        
        Returns:
            محتوای clipboard یا None
            
        Example:
            >>> text = kb.get_clipboard()
            >>> print(text)
        """
        if pyperclip is None:
            logger.warning("pyperclip not available")
            return None
        
        try:
            return pyperclip.paste()
        except Exception as e:
            logger.error("Failed to get clipboard: %s", e)
            return None
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Utility Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _add_to_history(self, action: KeyboardAction):
        """اضافه کردن اقدام به history."""
        self.action_history.append(action)
    
    def get_stats(self) -> dict:
        """دریافت آمار استفاده.
        
        Returns:
            دیکشنری آمار
            
        Example:
            >>> stats = kb.get_stats()
            >>> print(stats['total_keystrokes'])
        """
        stats = self.stats.copy()
        
        # محاسبه success rate
        total = stats['total_actions']
        if total > 0:
            failed = stats['failed_actions']
            success_rate = ((total - failed) / total) * 100
            stats['success_rate'] = f"{success_rate:.2f}%"
        else:
            stats['success_rate'] = "N/A"
        
        stats['recent_actions'] = len(self.action_history)
        
        return stats
    
    def reset_stats(self):
        """بازنشانی آمار.
        
        Example:
            >>> kb.reset_stats()
        """
        self.stats = {
            'total_keystrokes': 0,
            'total_text_typed': 0,
            'total_hotkeys': 0,
            'total_special_keys': 0,
            'failed_actions': 0,
            'total_actions': 0,
        }
        self.action_history.clear()
        logger.info("Stats reset")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helper Functions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def is_persian_text(text: str) -> bool:
    """بررسی سریع فارسی بودن متن.
    
    Args:
        text: متن برای بررسی
        
    Returns:
        True اگر متن فارسی باشد
        
    Example:
        >>> is_persian_text("سلام")
        True
        >>> is_persian_text("Hello")
        False
    """
    kb = KeyboardController()
    lang = kb.detect_language(text)
    return lang == Language.PERSIAN


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Common Hotkeys (برای راحتی)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Hotkeys:
    """کلاسی برای Hotkey های رایج."""
    
    # Editing
    COPY = ('ctrl', 'c')
    CUT = ('ctrl', 'x')
    PASTE = ('ctrl', 'v')
    UNDO = ('ctrl', 'z')
    REDO = ('ctrl', 'y')
    SELECT_ALL = ('ctrl', 'a')
    
    # File Operations
    SAVE = ('ctrl', 's')
    SAVE_AS = ('ctrl', 'shift', 's')
    OPEN = ('ctrl', 'o')
    NEW = ('ctrl', 'n')
    CLOSE = ('ctrl', 'w')
    QUIT = ('alt', 'f4')
    
    # Navigation
    FIND = ('ctrl', 'f')
    REPLACE = ('ctrl', 'h')
    NEXT = ('ctrl', 'g')
    PREVIOUS = ('ctrl', 'shift', 'g')
    
    # Window Management
    SWITCH_WINDOW = ('alt', 'tab')
    CLOSE_WINDOW = ('alt', 'f4')
    MINIMIZE = ('win', 'down')
    MAXIMIZE = ('win', 'up')
    
    # System
    TASK_MANAGER = ('ctrl', 'shift', 'esc')
    RUN = ('win', 'r')
    DESKTOP = ('win', 'd')


if __name__ == "__main__":
    # مثال سریع
    print("Testing KeyboardController...")
    
    kb = KeyboardController(human_behavior=True)
    
    # تست تشخیص زبان
    print(f"English: {kb.detect_language('Hello World')}")
    print(f"Persian: {kb.detect_language('سلام دنیا')}")
    print(f"Mixed: {kb.detect_language('Hello سلام')}")
    
    # نمایش آمار
    stats = kb.get_stats()
    print(f"\nStats: {stats}")
