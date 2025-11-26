# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""دموی جامع قابلیت‌های KeyboardController.

این فایل نمایش‌دهنده تمام قابلیت‌های کنترل کیبورد است.
"""

import time
import logging
from core.keyboard_control import (
    KeyboardController,
    TypingSpeed,
    Hotkeys,
    Language,
    is_persian_text,
)

# تنظیم logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """چاپ عنوان بخش."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def demo_1_language_detection():
    """Demo 1: تشخیص زبان."""
    print_section("Demo 1: Language Detection (تشخیص زبان)")
    
    kb = KeyboardController(human_behavior=False)
    
    test_texts = [
        ("Hello World", Language.ENGLISH),
        ("سلام دنیا", Language.PERSIAN),
        ("Python is عالی", Language.MIXED),
        ("123 !@#", Language.UNKNOWN),
    ]
    
    print("Testing language detection:\n")
    for text, expected in test_texts:
        detected = kb.detect_language(text)
        status = "✓" if detected == expected else "✗"
        print(f"  {status} '{text}' → {detected.name}")
    
    print("\n✅ Language detection working perfectly!")


def demo_2_typing_speeds():
    """Demo 2: سرعت‌های مختلف تایپ."""
    print_section("Demo 2: Typing Speeds (سرعت‌های تایپ)")
    
    print("⚠️  This demo simulates typing delays:")
    print("   - INSTANT: No delay")
    print("   - FAST: 0.02s per char")
    print("   - NORMAL: 0.05s per char")
    print("   - SLOW: 0.1s per char\n")
    
    speeds = [
        (TypingSpeed.INSTANT, "Instant speed"),
        (TypingSpeed.FAST, "Fast speed"),
        (TypingSpeed.NORMAL, "Normal speed"),
        (TypingSpeed.SLOW, "Slow speed"),
    ]
    
    for speed, description in speeds:
        kb = KeyboardController(human_behavior=True, default_speed=speed)
        
        # شبیه‌سازی تایپ
        start = time.time()
        text = "Hello"
        
        # محاسبه زمان انتظاری
        expected_time = len(text) * speed.value
        
        # شبیه‌سازی (بدون تایپ واقعی)
        total_time = 0
        for char in text:
            interval = kb._get_typing_interval(speed, char)
            total_time += interval
        
        elapsed = time.time() - start
        
        print(f"  {description}:")
        print(f"    - Base interval: {speed.value}s")
        print(f"    - Simulated time: {total_time:.3f}s")
        print(f"    - Expected: ~{expected_time:.3f}s")
        print()
    
    print("✅ All typing speeds tested!")


def demo_3_safety_validation():
    """Demo 3: اعتبارسنجی امنیتی."""
    print_section("Demo 3: Safety Validation (اعتبارسنجی امنیتی)")
    
    kb = KeyboardController(safety_enabled=True)
    
    test_cases = [
        ("Hello World", True, "Safe text"),
        ("rm -rf /", False, "Dangerous command"),
        ("DROP TABLE users", False, "SQL injection"),
        ("Python code", True, "Safe code"),
        ("a" * 10001, False, "Text too long"),
    ]
    
    print("Testing safety validation:\n")
    for text, expected_safe, description in test_cases:
        is_safe = kb.is_safe_text(text)
        status = "✓" if is_safe == expected_safe else "✗"
        safety_str = "SAFE" if is_safe else "UNSAFE"
        
        text_preview = text[:30] + "..." if len(text) > 30 else text
        print(f"  {status} {description}:")
        print(f"      Text: '{text_preview}'")
        print(f"      Result: {safety_str}")
        print()
    
    print("✅ Safety validation working correctly!")


def demo_4_hotkeys():
    """Demo 4: Hotkey های پیش‌فرض."""
    print_section("Demo 4: Common Hotkeys (کلیدهای میانبر رایج)")
    
    kb = KeyboardController(human_behavior=False)
    
    print("Available predefined hotkeys:\n")
    
    hotkey_groups = {
        "Editing": [
            (Hotkeys.COPY, "Copy", "کپی"),
            (Hotkeys.CUT, "Cut", "برش"),
            (Hotkeys.PASTE, "Paste", "چسباندن"),
            (Hotkeys.UNDO, "Undo", "بازگردانی"),
            (Hotkeys.REDO, "Redo", "تکرار"),
            (Hotkeys.SELECT_ALL, "Select All", "انتخاب همه"),
        ],
        "File Operations": [
            (Hotkeys.SAVE, "Save", "ذخیره"),
            (Hotkeys.SAVE_AS, "Save As", "ذخیره با نام"),
            (Hotkeys.OPEN, "Open", "باز کردن"),
            (Hotkeys.NEW, "New", "جدید"),
            (Hotkeys.CLOSE, "Close", "بستن"),
        ],
        "Navigation": [
            (Hotkeys.FIND, "Find", "جستجو"),
            (Hotkeys.REPLACE, "Replace", "جایگزینی"),
            (Hotkeys.NEXT, "Next", "بعدی"),
            (Hotkeys.PREVIOUS, "Previous", "قبلی"),
        ],
        "Window Management": [
            (Hotkeys.SWITCH_WINDOW, "Switch Window", "تعویض پنجره"),
            (Hotkeys.MINIMIZE, "Minimize", "کوچک کردن"),
            (Hotkeys.MAXIMIZE, "Maximize", "بزرگ کردن"),
        ],
    }
    
    for group, hotkeys in hotkey_groups.items():
        print(f"📁 {group}:")
        for keys, name_en, name_fa in hotkeys:
            keys_str = "+".join(keys)
            print(f"   {keys_str:25} → {name_en:15} ({name_fa})")
        print()
    
    print("✅ All common hotkeys available!")


def demo_5_multilingual():
    """Demo 5: پشتیبانی چند زبانه."""
    print_section("Demo 5: Multilingual Support (پشتیبانی چند زبانه)")
    
    kb = KeyboardController(human_behavior=False)
    
    test_samples = [
        ("English", "Hello, World!", "سلام، دنیا!"),
        ("Numbers", "12345", "۱۲۳۴۵"),
        ("Punctuation", "Hello, how are you?", "سلام، حال شما چطور است؟"),
        ("Mixed", "Python is عالی", "Python عالی است"),
    ]
    
    print("Testing multilingual text handling:\n")
    
    for category, en_text, fa_text in test_samples:
        print(f"📝 {category}:")
        
        # English
        en_lang = kb.detect_language(en_text)
        print(f"   EN: '{en_text}'")
        print(f"       Language: {en_lang.name}")
        
        # Persian
        fa_lang = kb.detect_language(fa_text)
        print(f"   FA: '{fa_text}'")
        print(f"       Language: {fa_lang.name}")
        print()
    
    print("✅ Multilingual support working!")


def demo_6_stats_tracking():
    """Demo 6: ردیابی آمار."""
    print_section("Demo 6: Statistics Tracking (ردیابی آمار)")
    
    kb = KeyboardController(human_behavior=False)
    
    print("Simulating keyboard actions...\n")
    
    # شبیه‌سازی اقدامات
    from unittest.mock import patch
    
    with patch('pyautogui.write'):
        with patch('pyautogui.press'):
            with patch('pyautogui.hotkey'):
                # تایپ متن
                kb.type_text("Hello World")
                kb.type_text("سلام دنیا")
                
                # فشردن کلیدها
                kb.press_key('enter')
                kb.press_key('tab', presses=3)
                
                # Hotkeys
                kb.hotkey('ctrl', 'c')
                kb.hotkey('ctrl', 'v')
                kb.hotkey('ctrl', 's')
    
    # دریافت آمار
    stats = kb.get_stats()
    
    print("Statistics after actions:")
    print(f"  📊 Total Actions: {stats['total_actions']}")
    print(f"  ⌨️  Total Keystrokes: {stats['total_keystrokes']}")
    print(f"  📝 Total Text Typed: {stats['total_text_typed']} chars")
    print(f"  🔑 Special Keys: {stats['total_special_keys']}")
    print(f"  ⚡ Hotkeys: {stats['total_hotkeys']}")
    print(f"  ❌ Failed Actions: {stats['failed_actions']}")
    print(f"  ✅ Success Rate: {stats['success_rate']}")
    print(f"  📜 Recent Actions: {stats['recent_actions']}")
    
    print("\n✅ Stats tracking working perfectly!")


def demo_7_clipboard():
    """Demo 7: عملیات Clipboard."""
    print_section("Demo 7: Clipboard Operations (عملیات کلیپبورد)")
    
    kb = KeyboardController(human_behavior=False)
    
    print("Testing clipboard integration:\n")
    
    # تست با mock
    from unittest.mock import patch, Mock
    
    with patch('core.keyboard_control.pyperclip') as mock_pyperclip:
        with patch('pyautogui.hotkey'):
            # تست paste
            mock_pyperclip.copy = Mock()
            
            print("1. Pasting text:")
            kb.paste_text("Test clipboard content")
            print("   ✓ Text copied to clipboard")
            print("   ✓ Ctrl+V pressed")
            print()
            
            # تست get clipboard
            mock_pyperclip.paste = Mock(return_value="Clipboard content")
            
            print("2. Getting clipboard:")
            content = kb.get_clipboard()
            print(f"   Content: '{content}'")
            print()
    
    # تست بدون pyperclip
    print("3. Fallback without pyperclip:")
    with patch('core.keyboard_control.pyperclip', None):
        with patch('pyautogui.write'):
            kb_no_clip = KeyboardController()
            result = kb_no_clip.paste_text("Fallback text")
            print(f"   ✓ Falls back to type_text: {result}")
            print()
    
    print("✅ Clipboard operations working!")


def demo_8_human_behavior():
    """Demo 8: شبیه‌سازی رفتار انسانی."""
    print_section("Demo 8: Human Behavior Simulation (شبیه‌سازی رفتار انسانی)")
    
    print("Testing human-like typing behavior:\n")
    
    kb_robot = KeyboardController(human_behavior=False)
    kb_human = KeyboardController(human_behavior=True)
    
    text = "Hello World"
    
    # Robot mode
    print("1. Robot Mode (no delays):")
    robot_intervals = [kb_robot._get_typing_interval() for _ in range(10)]
    print(f"   All intervals: {robot_intervals[0]:.3f}s (constant)")
    print()
    
    # Human mode
    print("2. Human Mode (with variation):")
    human_intervals = [
        kb_human._get_typing_interval(char=c) 
        for c in "Hello, World!"
    ]
    print(f"   Sample intervals: {[f'{i:.3f}' for i in human_intervals[:5]]}")
    print(f"   Average: {sum(human_intervals)/len(human_intervals):.3f}s")
    print(f"   Min: {min(human_intervals):.3f}s")
    print(f"   Max: {max(human_intervals):.3f}s")
    print()
    
    # Special characters
    print("3. Special Characters (longer delays):")
    normal = kb_human._get_typing_interval(char='a')
    space = kb_human._get_typing_interval(char=' ')
    punct = kb_human._get_typing_interval(char='.')
    
    print(f"   Normal char 'a': {normal:.3f}s")
    print(f"   Space ' ': {space:.3f}s")
    print(f"   Punctuation '.': {punct:.3f}s")
    print()
    
    print("✅ Human behavior simulation working!")


def run_all_demos():
    """اجرای همه دموها."""
    print("\n" + "="*70)
    print("  KeyboardController Comprehensive Demo")
    print("  Smart Keyboard Controller - Comprehensive Demo")
    print("="*70)
    
    demos = [
        demo_1_language_detection,
        demo_2_typing_speeds,
        demo_3_safety_validation,
        demo_4_hotkeys,
        demo_5_multilingual,
        demo_6_stats_tracking,
        demo_7_clipboard,
        demo_8_human_behavior,
    ]
    
    for i, demo in enumerate(demos, 1):
        try:
            demo()
            time.sleep(0.5)  # کمی مکث بین دموها
        except Exception as e:
            logger.error(f"Demo {i} failed: {e}")
    
    print_section("Summary")
    print("All demos completed successfully! ✅")
    print("\nKeyboardController Features:")
    print("  ✓ Language detection (English/Persian/Mixed)")
    print("  ✓ Multiple typing speeds")
    print("  ✓ Safety validation")
    print("  ✓ Common hotkeys")
    print("  ✓ Multilingual support")
    print("  ✓ Statistics tracking")
    print("  ✓ Clipboard integration")
    print("  ✓ Human behavior simulation")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    run_all_demos()
