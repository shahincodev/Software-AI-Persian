# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

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

from core.mouse_control import MouseController, MouseButton, ClickPattern
from core.desktop_vision import DesktopVision


def demo_basic_operations():
    """دمو عملیات اساسی موس."""
    print("═" * 60)
    print("🖱️  دموی عملیات اساسی MouseController")
    print("═" * 60)
    
    # ساخت MouseController ساده
    mouse = MouseController(
        safety_enabled=True,
        human_behavior=False
    )
    
    print("\n1️⃣  دریافت موقعیت فعلی موس...")
    x, y = mouse.get_position()
    print(f"   ✅ موقعیت: ({x}, {y})")
    
    print("\n2️⃣  تست اعتبارسنجی امنیتی...")
    safe_pos = (500, 300)
    unsafe_pos = (-10, -10)
    
    print(f"   موقعیت {safe_pos}: {'✅ امن' if mouse.is_safe_position(*safe_pos) else '❌ غیرامن'}")
    print(f"   موقعیت {unsafe_pos}: {'✅ امن' if mouse.is_safe_position(*unsafe_pos) else '❌ غیرامن'}")
    
    print("\n3️⃣  حرکت موس به موقعیت امن...")
    if mouse.move(500, 300, duration=1.0):
        print("   ✅ حرکت موفق")
    
    print("\n4️⃣  کلیک چپ...")
    if mouse.click(500, 300):
        print("   ✅ کلیک موفق")
    
    print("\n5️⃣  دوبل کلیک...")
    if mouse.click(500, 300, clicks=2):
        print("   ✅ دوبل کلیک موفق")
    
    print("\n6️⃣  کلیک راست...")
    if mouse.click(500, 300, button=MouseButton.RIGHT):
        print("   ✅ کلیک راست موفق")
    
    print("\n7️⃣  اسکرول...")
    if mouse.scroll(5):
        print("   ✅ اسکرول به بالا موفق")
    
    # نمایش آمار
    print("\n📊 آمار عملیات:")
    stats = mouse.get_stats()
    for key, value in stats.items():
        if key != 'action_history':
            print(f"   {key}: {value}")
    
    print("\n✅ دموی عملیات اساسی تکمیل شد")


def demo_human_behavior():
    """دمو رفتارهای انسانی."""
    print("\n" + "═" * 60)
    print("🤖 دموی رفتار انسانی (Human-Like Behavior)")
    print("═" * 60)
    
    # ساخت MouseController با رفتار انسانی
    mouse = MouseController(
        safety_enabled=True,
        human_behavior=True
    )
    
    print("\n1️⃣  کلیک با سرعت INSTANT...")
    start = time.time()
    mouse.click_human(500, 300, pattern=ClickPattern.INSTANT)
    duration1 = time.time() - start
    print(f"   ⚡ زمان: {duration1:.3f}s")
    
    print("\n2️⃣  کلیک با سرعت HUMAN_FAST...")
    start = time.time()
    mouse.click_human(500, 300, pattern=ClickPattern.HUMAN_FAST)
    duration2 = time.time() - start
    print(f"   🏃 زمان: {duration2:.3f}s")
    
    print("\n3️⃣  کلیک با سرعت HUMAN_NORMAL...")
    start = time.time()
    mouse.click_human(500, 300, pattern=ClickPattern.HUMAN_NORMAL)
    duration3 = time.time() - start
    print(f"   🚶 زمان: {duration3:.3f}s")
    
    print("\n4️⃣  کلیک با سرعت HUMAN_SLOW...")
    start = time.time()
    mouse.click_human(500, 300, pattern=ClickPattern.HUMAN_SLOW)
    duration4 = time.time() - start
    print(f"   🐌 زمان: {duration4:.3f}s")
    
    print("\n📈 مقایسه سرعت:")
    print(f"   INSTANT:      {duration1:.3f}s (پایه)")
    print(f"   HUMAN_FAST:   {duration2:.3f}s ({duration2/duration1:.1f}x کندتر)")
    print(f"   HUMAN_NORMAL: {duration3:.3f}s ({duration3/duration1:.1f}x کندتر)")
    print(f"   HUMAN_SLOW:   {duration4:.3f}s ({duration4/duration1:.1f}x کندتر)")
    
    print("\n5️⃣  حرکت هموار با Bezier curve...")
    start = time.time()
    mouse.move(800, 400, duration=2.0, smooth=True)
    duration = time.time() - start
    print(f"   ✅ حرکت هموار انجام شد ({duration:.2f}s)")
    
    print("\n✅ دموی رفتار انسانی تکمیل شد")


def demo_vision_guided():
    """دمو عملیات Vision-guided."""
    print("\n" + "═" * 60)
    print("👁️  دموی Vision-Guided Operations")
    print("═" * 60)
    
    print("\n⚠️  این دمو نیاز به DesktopVision دارد")
    print("⚠️  برای تست واقعی باید OCR و template matching فعال باشد")
    
    try:
        # ساخت Vision system
        vision = DesktopVision()
        
        # ساخت MouseController با Vision
        mouse = MouseController(
            vision_system=vision,
            safety_enabled=True,
            human_behavior=True
        )
        
        print("\n✅ MouseController + DesktopVision آماده است")
        print("\n📝 مثال‌های استفاده:")
        print("   # کلیک روی دکمه 'OK'")
        print("   mouse.click_on_text('OK')")
        print()
        print("   # کلیک روی آیکن بستن")
        print("   mouse.click_on_image('assets/close_button.png')")
        print()
        print("   # جستجوی متن فارسی")
        print("   mouse.click_on_text('تایید', confidence=0.8)")
        
    except Exception as e:
        print(f"\n❌ خطا در ساخت Vision system: {e}")
        print("   (این طبیعی است اگر Tesseract OCR نصب نباشد)")
    
    print("\n✅ دموی Vision-Guided تکمیل شد")


def demo_safety_features():
    """دمو ویژگی‌های امنیتی."""
    print("\n" + "═" * 60)
    print("🛡️  دموی ویژگی‌های امنیتی")
    print("═" * 60)
    
    mouse = MouseController(safety_enabled=True)
    
    print("\n1️⃣  تست موقعیت‌های امن...")
    test_positions = [
        (100, 100, "وسط صفحه"),
        (10, 10, "گوشه بالا چپ (unsafe)"),
        (-50, -50, "خارج از صفحه (unsafe)"),
        (5000, 5000, "خیلی دور (unsafe)"),
    ]
    
    for x, y, desc in test_positions:
        safe = mouse.is_safe_position(x, y)
        icon = "✅" if safe else "❌"
        print(f"   {icon} ({x}, {y}) - {desc}")
    
    print("\n2️⃣  تست اعتبارسنجی مختصات...")
    try:
        x, y = mouse.validate_coordinates(500, 300)
        print(f"   ✅ (500, 300) معتبر است → ({x}, {y})")
    except ValueError as e:
        print(f"   ❌ خطا: {e}")
    
    try:
        x, y = mouse.validate_coordinates(-100, -100)
        print(f"   ✅ (-100, -100) معتبر است → ({x}, {y})")
    except ValueError as e:
        print(f"   ❌ (-100, -100) نامعتبر: {str(e)[:50]}...")
    
    print("\n3️⃣  غیرفعال کردن امنیت...")
    unsafe_mouse = MouseController(safety_enabled=False)
    print("   ⚠️  امنیت غیرفعال شد - تمام موقعیت‌ها مجاز هستند")
    print(f"   (-100, -100) با safety_enabled=False: {'✅ مجاز' if unsafe_mouse.is_safe_position(-100, -100) else '❌ ممنوع'}")
    
    print("\n✅ دموی امنیتی تکمیل شد")


def main():
    """تابع اصلی - اجرای تمام دموها."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  🖱️  Mouse Control Demo - Software-AI (Persian Version)  ".center(58) + "║")
    print("║" + "  نمایش کنترل هوشمند موس با هوش مصنوعی  ".center(58) + "║")
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
        print("🎉 تمام دموها با موفقیت اجرا شدند!")
        print("═" * 60)
        print("\n💡 نکات کلیدی:")
        print("   ✅ Safety Validation: جلوگیری از کلیک‌های خطرناک")
        print("   ✅ Human Behavior: شبیه‌سازی رفتار انسانی با Bezier curves")
        print("   ✅ Vision Integration: کلیک روی متن/تصویر با AI")
        print("   ✅ Stats & History: ردیابی کامل تمام عملیات")
        print("\n📚 برای اطلاعات بیشتر:")
        print("   - مستندات: docs/MOUSE_CONTROL.md")
        print("   - تست‌ها: tests/test_mouse_control.py")
        print("   - کد منبع: core/mouse_control.py")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  دمو توسط کاربر متوقف شد")
    except Exception as e:
        print(f"\n\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
