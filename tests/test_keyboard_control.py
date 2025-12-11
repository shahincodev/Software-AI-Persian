# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""تست‌های جامع برای KeyboardController.

این فایل شامل تست‌های کامل برای تمام قابلیت‌های کنترل کیبورد است.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from core.keyboard_control import (
    KeyboardController,
    Language,
    TypingSpeed,
    KeyAction,
    Hotkeys,
    is_persian_text,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Fixtures
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@pytest.fixture
def kb_basic():
    """KeyboardController پایه."""
    return KeyboardController(safety_enabled=True, human_behavior=False)


@pytest.fixture
def kb_human():
    """KeyboardController با رفتار انسانی."""
    return KeyboardController(safety_enabled=True, human_behavior=True)


@pytest.fixture
def kb_unsafe():
    """KeyboardController بدون امنیت."""
    return KeyboardController(safety_enabled=False, human_behavior=False)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Language Detection Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestLanguageDetection:
    """تست‌های تشخیص زبان."""
    
    def test_detect_english(self, kb_basic):
        """تست تشخیص انگلیسی."""
        assert kb_basic.detect_language("Hello World") == Language.ENGLISH
        assert kb_basic.detect_language("Python is great") == Language.ENGLISH
        assert kb_basic.detect_language("123 abc def") == Language.ENGLISH
    
    def test_detect_persian(self, kb_basic):
        """تست تشخیص فارسی."""
        assert kb_basic.detect_language("سلام دنیا") == Language.PERSIAN
        assert kb_basic.detect_language("پایتون عالی است") == Language.PERSIAN
        assert kb_basic.detect_language("۱۲۳ سلام") == Language.PERSIAN
    
    def test_detect_mixed(self, kb_basic):
        """تست تشخیص مختلط."""
        result = kb_basic.detect_language("Hello سلام")
        assert result in [Language.MIXED, Language.PERSIAN, Language.ENGLISH]
        
        result = kb_basic.detect_language("Python و پایتون")
        assert result in [Language.MIXED, Language.PERSIAN, Language.ENGLISH]
    
    def test_detect_empty(self, kb_basic):
        """تست متن خالی."""
        assert kb_basic.detect_language("") == Language.UNKNOWN
        assert kb_basic.detect_language("   ") == Language.UNKNOWN
        assert kb_basic.detect_language("123") == Language.UNKNOWN
    
    def test_helper_function(self):
        """تست تابع کمکی is_persian_text."""
        assert is_persian_text("سلام") == True
        assert is_persian_text("Hello") == False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Safety Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestSafety:
    """تست‌های امنیتی."""
    
    def test_safe_text(self, kb_basic):
        """تست متن امن."""
        assert kb_basic.is_safe_text("Hello World") == True
        assert kb_basic.is_safe_text("سلام دنیا") == True
        assert kb_basic.is_safe_text("Python code") == True
    
    def test_unsafe_patterns(self, kb_basic):
        """تست الگوهای خطرناک."""
        assert kb_basic.is_safe_text("rm -rf /") == False
        assert kb_basic.is_safe_text("del /f *.*") == False
        assert kb_basic.is_safe_text("DROP TABLE users") == False
        assert kb_basic.is_safe_text("format c:") == False
    
    def test_long_text(self, kb_basic):
        """تست متن خیلی طولانی."""
        long_text = "a" * 10001
        assert kb_basic.is_safe_text(long_text) == False
        
        ok_text = "a" * 9999
        assert kb_basic.is_safe_text(ok_text) == True
    
    def test_validate_text_raises(self, kb_basic):
        """تست ValueError برای متن خطرناک."""
        with pytest.raises(ValueError):
            kb_basic.validate_text("rm -rf /")
    
    def test_safety_disabled(self, kb_unsafe):
        """تست غیرفعال بودن امنیت."""
        # همه چیز باید مجاز باشد
        assert kb_unsafe.is_safe_text("rm -rf /") == True
        assert kb_unsafe.is_safe_text("DROP TABLE users") == True


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Human Behavior Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestHumanBehavior:
    """تست‌های رفتار انسانی."""
    
    def test_typing_interval_instant(self, kb_basic):
        """تست حالت INSTANT."""
        kb_basic.default_speed = TypingSpeed.INSTANT
        interval = kb_basic._get_typing_interval()
        assert interval == 0.0
    
    def test_typing_interval_normal(self, kb_human):
        """تست حالت NORMAL با نویز."""
        kb_human.default_speed = TypingSpeed.NORMAL
        
        # باید مقداری نزدیک 0.05 باشد
        intervals = [kb_human._get_typing_interval() for _ in range(10)]
        avg = sum(intervals) / len(intervals)
        
        # باید در محدوده 0.035 تا 0.065 باشد (±30%)
        assert 0.03 < avg < 0.07
    
    def test_typing_interval_special_chars(self, kb_human):
        """تست کاراکترهای خاص (طولانی‌تر)."""
        normal_interval = kb_human._get_typing_interval(char='a')
        space_interval = kb_human._get_typing_interval(char=' ')
        punct_interval = kb_human._get_typing_interval(char='.')
        
        # فضا و نقطه باید بیشتر طول بکشند
        assert space_interval >= normal_interval
        assert punct_interval >= normal_interval
    
    def test_simulate_typo(self, kb_human):
        """تست شبیه‌سازی خطا."""
        # فعلاً فقط لاگ می‌کند، نباید تغییری بدهد
        result = kb_human._simulate_typo("test")
        assert result == "test"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Core Typing Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestTyping:
    """تست‌های تایپ متن."""
    
    @patch('pyautogui.write')
    def test_type_text_basic(self, mock_write, kb_basic):
        """تست تایپ ساده."""
        result = kb_basic.type_text("Hello")
        
        assert result == True
        assert mock_write.call_count == 5  # 5 chars
        assert kb_basic.stats['total_text_typed'] == 5
        assert kb_basic.stats['total_keystrokes'] == 5
    
    @patch('pyautogui.write')
    def test_type_text_persian(self, mock_write, kb_basic):
        """تست تایپ فارسی."""
        result = kb_basic.type_text("سلام")
        
        assert result == True
        assert mock_write.call_count == 4  # 4 chars
    
    @patch('pyautogui.write')
    def test_type_text_unsafe(self, mock_write, kb_basic):
        """تست تایپ متن خطرناک."""
        result = kb_basic.type_text("rm -rf /", validate=True)
        
        assert result == False
        assert kb_basic.stats['failed_actions'] == 1
        assert mock_write.call_count == 0  # نباید صدا زده شود
    
    @patch('pyautogui.write')
    @patch('time.sleep')
    def test_type_text_with_speed(self, mock_sleep, mock_write, kb_human):
        """تست تایپ با سرعت."""
        kb_human.type_text("Hi", speed=TypingSpeed.SLOW)
        
        # باید sleep صدا زده شود (رفتار انسانی)
        assert mock_sleep.call_count > 0
    
    @patch('pyautogui.write')
    def test_type_text_empty(self, mock_write, kb_basic):
        """تست تایپ متن خالی."""
        result = kb_basic.type_text("")
        
        assert result == True
        assert mock_write.call_count == 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Key Press Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestKeyPress:
    """تست‌های فشردن کلید."""
    
    @patch('pyautogui.press')
    def test_press_key_single(self, mock_press, kb_basic):
        """تست فشردن یک بار."""
        result = kb_basic.press_key('enter')
        
        assert result == True
        mock_press.assert_called_once_with('enter')
        assert kb_basic.stats['total_special_keys'] == 1
    
    @patch('pyautogui.press')
    @patch('time.sleep')
    def test_press_key_multiple(self, mock_sleep, mock_press, kb_basic):
        """تست فشردن چند بار."""
        result = kb_basic.press_key('tab', presses=3, interval=0.1)
        
        assert result == True
        assert mock_press.call_count == 3
        assert kb_basic.stats['total_special_keys'] == 3
    
    @patch('pyautogui.press')
    def test_press_key_failure(self, mock_press, kb_basic):
        """تست خطا در فشردن کلید."""
        mock_press.side_effect = Exception("Test error")
        
        result = kb_basic.press_key('invalid')
        
        assert result == False
        assert kb_basic.stats['failed_actions'] == 1


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Hotkey Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestHotkeys:
    """تست‌های Hotkey."""
    
    @patch('pyautogui.hotkey')
    def test_hotkey_simple(self, mock_hotkey, kb_basic):
        """تست Hotkey ساده."""
        result = kb_basic.hotkey('ctrl', 'c')
        
        assert result == True
        mock_hotkey.assert_called_once_with('ctrl', 'c')
        assert kb_basic.stats['total_hotkeys'] == 1
    
    @patch('pyautogui.hotkey')
    def test_hotkey_complex(self, mock_hotkey, kb_basic):
        """تست Hotkey پیچیده."""
        result = kb_basic.hotkey('ctrl', 'shift', 's')
        
        assert result == True
        mock_hotkey.assert_called_once_with('ctrl', 'shift', 's')
    
    @patch('pyautogui.hotkey')
    def test_hotkey_predefined(self, mock_hotkey, kb_basic):
        """تست Hotkey های از پیش تعریف شده."""
        kb_basic.hotkey(*Hotkeys.COPY)
        mock_hotkey.assert_called_with('ctrl', 'c')
        
        kb_basic.hotkey(*Hotkeys.SAVE)
        mock_hotkey.assert_called_with('ctrl', 's')
    
    @patch('pyautogui.hotkey')
    def test_hotkey_failure(self, mock_hotkey, kb_basic):
        """تست خطا در Hotkey."""
        mock_hotkey.side_effect = Exception("Test error")
        
        result = kb_basic.hotkey('ctrl', 'x')
        
        assert result == False
        assert kb_basic.stats['failed_actions'] == 1


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Hold Key Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestHoldKey:
    """تست‌های نگه داشتن کلید."""
    
    @patch('pyautogui.keyUp')
    @patch('pyautogui.keyDown')
    @patch('time.sleep')
    def test_hold_key_basic(self, mock_sleep, mock_down, mock_up, kb_basic):
        """تست نگه داشتن کلید."""
        result = kb_basic.hold_key('shift', duration=1.0)
        
        assert result == True
        mock_down.assert_called_once_with('shift')
        mock_up.assert_called_once_with('shift')
        mock_sleep.assert_called_once_with(1.0)
        assert kb_basic.stats['total_special_keys'] == 1
    
    @patch('pyautogui.keyUp')
    @patch('pyautogui.keyDown')
    @patch('time.sleep')
    def test_hold_key_failure(self, mock_sleep, mock_down, mock_up, kb_basic):
        """تست خطا در نگه داشتن کلید."""
        mock_down.side_effect = Exception("Test error")
        
        result = kb_basic.hold_key('ctrl', duration=0.5)
        
        assert result == False
        assert kb_basic.stats['failed_actions'] == 1


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Clipboard Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestClipboard:
    """تست‌های Clipboard."""
    
    @patch('core.keyboard_control.pyperclip')
    @patch('pyautogui.hotkey')
    @patch('time.sleep')
    def test_paste_text(self, mock_sleep, mock_hotkey, mock_pyperclip, kb_basic):
        """تست paste کردن متن."""
        mock_pyperclip.copy = Mock()
        
        result = kb_basic.paste_text("Test text")
        
        assert result == True
        mock_pyperclip.copy.assert_called_once_with("Test text")
        mock_hotkey.assert_called_once_with('ctrl', 'v')
    
    @patch('core.keyboard_control.pyperclip', None)
    @patch('pyautogui.write')
    def test_paste_text_fallback(self, mock_write, kb_basic):
        """تست fallback به type_text."""
        result = kb_basic.paste_text("Test")
        
        # باید به type_text برگردد
        assert mock_write.call_count == 4  # 4 chars
    
    @patch('core.keyboard_control.pyperclip')
    def test_get_clipboard(self, mock_pyperclip, kb_basic):
        """تست دریافت clipboard."""
        mock_pyperclip.paste = Mock(return_value="Clipboard content")
        
        result = kb_basic.get_clipboard()
        
        assert result == "Clipboard content"
        mock_pyperclip.paste.assert_called_once()
    
    @patch('core.keyboard_control.pyperclip', None)
    def test_get_clipboard_unavailable(self, kb_basic):
        """تست clipboard در دسترس نیست."""
        result = kb_basic.get_clipboard()
        assert result is None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Stats Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestStats:
    """تست‌های آمار."""
    
    @patch('pyautogui.write')
    @patch('pyautogui.press')
    @patch('pyautogui.hotkey')
    def test_stats_tracking(self, mock_hotkey, mock_press, mock_write, kb_basic):
        """تست ردیابی آمار."""
        # تایپ متن
        kb_basic.type_text("Hi")
        
        # فشردن کلید
        kb_basic.press_key('enter')
        
        # Hotkey
        kb_basic.hotkey('ctrl', 'c')
        
        stats = kb_basic.get_stats()
        
        assert stats['total_text_typed'] == 2  # "Hi"
        assert stats['total_keystrokes'] == 2
        assert stats['total_special_keys'] == 1  # enter
        assert stats['total_hotkeys'] == 1  # ctrl+c
        assert stats['total_actions'] == 3
        assert stats['failed_actions'] == 0
        assert '100.00%' in stats['success_rate']
    
    @patch('pyautogui.write')
    def test_stats_failure_tracking(self, mock_write, kb_basic):
        """تست ردیابی خطاها."""
        mock_write.side_effect = Exception("Error")
        
        kb_basic.type_text("Test")
        
        stats = kb_basic.get_stats()
        assert stats['failed_actions'] == 1
        assert '0.00%' in stats['success_rate']
    
    def test_reset_stats(self, kb_basic):
        """تست بازنشانی آمار."""
        kb_basic.stats['total_keystrokes'] = 100
        kb_basic.action_history.append(Mock())
        
        kb_basic.reset_stats()
        
        assert kb_basic.stats['total_keystrokes'] == 0
        assert len(kb_basic.action_history) == 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Action History Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestActionHistory:
    """تست‌های تاریخچه اقدامات."""
    
    @patch('pyautogui.write')
    def test_action_history_records(self, mock_write, kb_basic):
        """تست ثبت اقدامات."""
        kb_basic.type_text("Test")
        
        assert len(kb_basic.action_history) == 1
        action = kb_basic.action_history[0]
        
        assert action.action_type == "type"
        assert action.text == "Test"
        assert action.success == True
        assert action.duration > 0
    
    @patch('pyautogui.write')
    def test_action_history_limit(self, mock_write, kb_basic):
        """تست محدودیت تعداد اقدامات."""
        kb_basic.max_history = 5
        
        # اضافه کردن 10 اقدام
        for i in range(10):
            kb_basic.type_text(f"Test{i}")
        
        # باید فقط 5 تا باشد
        assert len(kb_basic.action_history) == 5
        
        # جدیدترین‌ها باید باشند
        assert kb_basic.action_history[-1].text == "Test9"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Integration Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestIntegration:
    """تست‌های یکپارچگی."""
    
    @patch('pyautogui.write')
    @patch('pyautogui.hotkey')
    @patch('pyautogui.press')
    def test_complete_workflow(self, mock_press, mock_hotkey, mock_write, kb_basic):
        """تست یک کار کامل."""
        # تایپ متن
        kb_basic.type_text("Hello")
        
        # انتخاب همه
        kb_basic.hotkey(*Hotkeys.SELECT_ALL)
        
        # کپی
        kb_basic.hotkey(*Hotkeys.COPY)
        
        # Enter
        kb_basic.press_key('enter')
        
        # Paste
        kb_basic.hotkey(*Hotkeys.PASTE)
        
        stats = kb_basic.get_stats()
        assert stats['total_actions'] == 5
        assert stats['failed_actions'] == 0
    
    @patch('pyautogui.write')
    def test_multilanguage_typing(self, mock_write, kb_basic):
        """تست تایپ چند زبانه."""
        # انگلیسی
        kb_basic.type_text("Hello")
        assert mock_write.call_count == 5
        
        # فارسی
        kb_basic.type_text("سلام")
        assert mock_write.call_count == 9  # 5 + 4
        
        # مختلط
        kb_basic.type_text("Hello سلام")
        assert mock_write.call_count > 9


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Edge Cases
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestEdgeCases:
    """تست‌های موارد خاص."""
    
    @patch('pyautogui.write')
    def test_special_characters(self, mock_write, kb_basic):
        """تست کاراکترهای خاص."""
        special = "!@#$%^&*()_+-={}[]|\\:;\"'<>,.?/"
        result = kb_basic.type_text(special)
        
        assert result == True
        assert mock_write.call_count == len(special)
    
    @patch('pyautogui.write')
    def test_unicode_characters(self, mock_write, kb_basic):
        """تست کاراکترهای Unicode."""
        unicode_text = "🎉 مرحبا 你好 こんにちは"
        result = kb_basic.type_text(unicode_text)
        
        assert result == True
    
    @patch('pyautogui.write')
    def test_whitespace(self, mock_write, kb_basic):
        """تست فضاهای خالی."""
        text = "Hello\nWorld\t!"
        result = kb_basic.type_text(text)
        
        assert result == True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
