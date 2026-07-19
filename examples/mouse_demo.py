# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""دموی MouseController - نمایش قابلیت‌های کنترل موس با هوش مصنوعی.

این دمو نشان می‌دهد:
- کنترل امن موس با Safety Validation
- رفتارهای انسانی (Bezier curves, Human timing)
- عملیات Vision-guided (کلیک روی متن/تصویر)
- آمارگیری و تحلیل عملکرد

استفاده:
    python examples/mouse_demo.py
"""

import time
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه به sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.mouse_control import MouseController, MouseButton, ClickPattern  # noqa: E402
from core.desktop_vision import DesktopVision  # noqa: E402


def demo_basic_operations():
    """دمو عملیات اساسی موس."""
    print("═" * 60)
    print("🖱️  MouseController Basic Operations Demo")
    print("═" * 60)
    
    # ساخت MouseController ساده
    mouse = MouseController(
        safety_enabled=True,
        human_behavior=False
    )
    
    print("\n1️⃣  Getting current mouse position...")
    x, y = mouse.get_position()
    print(f"   ✅ Position: ({x}, {y})")
    
    print("\n2️⃣  Testing safety validation...")
    safe_pos = (500, 300)
    unsafe_pos = (-10, -10)
    
    print(f"   Position {safe_pos}: {'✅ Safe' if mouse.is_safe_position(*safe_pos) else '❌ Unsafe'}")
    print(f"   Position {unsafe_pos}: {'✅ Safe' if mouse.is_safe_position(*unsafe_pos) else '❌ Unsafe'}")
    
    print("\n3️⃣  Moving mouse to safe position...")
    if mouse.move(500, 300, duration=1.0):
        print("   ✅ Move successful")
    
    print("\n4️⃣  Left click...")
    if mouse.click(500, 300):
        print("   ✅ Click successful")
    
    print("\n5️⃣  Double click...")
    if mouse.click(500, 300, clicks=2):
        print("   ✅ Double click successful")
    
    print("\n6️⃣  Right click...")
    if mouse.click(500, 300, button=MouseButton.RIGHT):
        print("   ✅ Right click successful")
    
    print("\n7️⃣  Scrolling...")
    if mouse.scroll(5):
        print("   ✅ Scroll up successful")
    
    # نمایش آمار
    print("\n📊 Operation Statistics:")
    stats = mouse.get_stats()
    for key, value in stats.items():
        if key != 'action_history':
            print(f"   {key}: {value}")
    
    print("\n✅ Basic operations demo completed")


def demo_human_behavior():
    """دمو رفتارهای انسانی."""
    print("\n" + "═" * 60)
    print("🤖 Human-Like Behavior Demo")
    print("═" * 60)
    
    # ساخت MouseController با رفتار انسانی
    mouse = MouseController(
        safety_enabled=True,
        human_behavior=True
    )
    
    print("\n1️⃣  Click with INSTANT speed...")
    start = time.time()
    mouse.click_human(500, 300, pattern=ClickPattern.INSTANT)
    duration1 = time.time() - start
    print(f"   ⚡ Time: {duration1:.3f}s")
    
    print("\n2️⃣  Click with HUMAN_FAST speed...")
    start = time.time()
    mouse.click_human(500, 300, pattern=ClickPattern.HUMAN_FAST)
    duration2 = time.time() - start
    print(f"   🏃 Time: {duration2:.3f}s")
    
    print("\n3️⃣  Click with HUMAN_NORMAL speed...")
    start = time.time()
    mouse.click_human(500, 300, pattern=ClickPattern.HUMAN_NORMAL)
    duration3 = time.time() - start
    print(f"   🚶 Time: {duration3:.3f}s")
    
    print("\n4️⃣  Click with HUMAN_SLOW speed...")
    start = time.time()
    mouse.click_human(500, 300, pattern=ClickPattern.HUMAN_SLOW)
    duration4 = time.time() - start
    print(f"   🐌 Time: {duration4:.3f}s")
    
    print("\n📈 Speed Comparison:")
    print(f"   INSTANT:      {duration1:.3f}s (baseline)")
    print(f"   HUMAN_FAST:   {duration2:.3f}s ({duration2/duration1:.1f}x slower)")
    print(f"   HUMAN_NORMAL: {duration3:.3f}s ({duration3/duration1:.1f}x slower)")
    print(f"   HUMAN_SLOW:   {duration4:.3f}s ({duration4/duration1:.1f}x slower)")
    
    print("\n5️⃣  Smooth movement with Bezier curve...")
    start = time.time()
    mouse.move(800, 400, duration=2.0, smooth=True)
    duration = time.time() - start
    print(f"   ✅ Smooth movement completed ({duration:.2f}s)")
    
    print("\n✅ Human behavior demo completed")


def demo_vision_guided():
    """دمو عملیات Vision-guided."""
    print("\n" + "═" * 60)
    print("👁️  Vision-Guided Operations Demo")
    print("═" * 60)
    
    print("\n⚠️  This demo requires DesktopVision")
    print("⚠️  For actual testing, OCR and template matching must be active")
    
    try:
        # ساخت Vision system
        DesktopVision()
        
        print("\n✅ MouseController + DesktopVision ready")
        print("\n📝 Usage examples:")
        print("   # Click on 'OK' button")
        print("   mouse.click_on_text('OK')")
        print()
        print("   # Click on close icon")
        print("   mouse.click_on_image('assets/close_button.png')")
        print()
        print("   # Search Persian text")
        print("   mouse.click_on_text('تایید', confidence=0.8)")
        
    except Exception as e:
        print(f"\n❌ Error creating Vision system: {e}")
        print("   (This is normal if Tesseract OCR is not installed)")
    
    print("\n✅ Vision-Guided demo completed")


def demo_safety_features():
    """دمو ویژگی‌های امنیتی."""
    print("\n" + "═" * 60)
    print("🛡️  Safety Features Demo")
    print("═" * 60)
    
    mouse = MouseController(safety_enabled=True)
    
    print("\n1️⃣  Testing safe positions...")
    test_positions = [
        (100, 100, "Screen center"),
        (10, 10, "Top left corner (unsafe)"),
        (-50, -50, "Outside screen (unsafe)"),
        (5000, 5000, "Too far (unsafe)"),
    ]
    
    for x, y, desc in test_positions:
        safe = mouse.is_safe_position(x, y)
        icon = "✅" if safe else "❌"
        print(f"   {icon} ({x}, {y}) - {desc}")
    
    print("\n2️⃣  Testing coordinate validation...")
    try:
        x, y = mouse.validate_coordinates(500, 300)
        print(f"   ✅ (500, 300) is valid → ({x}, {y})")
    except ValueError as e:
        print(f"   ❌ Error: {e}")
    
    try:
        x, y = mouse.validate_coordinates(-100, -100)
        print(f"   ✅ (-100, -100) is valid → ({x}, {y})")
    except ValueError as e:
        print(f"   ❌ (-100, -100) invalid: {str(e)[:50]}...")
    
    print("\n3️⃣  Disabling safety...")
    unsafe_mouse = MouseController(safety_enabled=False)
    print("   ⚠️  Safety disabled - all positions allowed")
    print(f"   (-100, -100) with safety_enabled=False: {'✅ Allowed' if unsafe_mouse.is_safe_position(-100, -100) else '❌ Blocked'}")
    
    print("\n✅ Safety demo completed")


def main():
    """تابع اصلی - اجرای تمام دموها."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  🖱️  Mouse Control Demo - Software-AI (Persian Version)  ".center(58) + "║")
    print("║" + "  Intelligent Mouse Control with AI  ".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")
    
    try:
        # دمو 1: عملیات اساسی
        demo_basic_operations()
        time.sleep(1)
        
        # دمو 2: رفتار انسانی
        demo_human_behavior()
        time.sleep(1)
        
        # دمو 3: Vision-guided
        demo_vision_guided()
        time.sleep(1)
        
        # دمو 4: امنیت
        demo_safety_features()
        
        # خلاصه
        print("\n" + "═" * 60)
        print("🎉 All demos completed successfully!")
        print("═" * 60)
        print("\n💡 Key Points:")
        print("   ✅ Safety Validation: Prevent dangerous clicks")
        print("   ✅ Human Behavior: Simulate human behavior with Bezier curves")
        print("   ✅ Vision Integration: Click on text/image with AI")
        print("   ✅ Stats & History: Complete tracking of all operations")
        print("\n📚 For more information:")
        print("   - Documentation: docs/MOUSE_CONTROL.md")
        print("   - Tests: tests/test_mouse_control.py")
        print("   - Source code: core/mouse_control.py")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
