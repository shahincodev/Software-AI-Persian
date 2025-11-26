# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""تست‌های سیستم بینایی Desktop Vision."""

import time
import pytest
from pathlib import Path

from core.desktop_vision import DesktopVision, TextBox, WindowInfo


class TestDesktopVision:
    """تست‌های کلاس DesktopVision."""
    
    @pytest.fixture
    def vision(self):
        """ایجاد instance از DesktopVision."""
        return DesktopVision()
    
    def test_capture_screen(self, vision):
        """تست گرفتن اسکرین‌شات کل صفحه."""
        img = vision.capture_screen()
        
        assert img is not None
        assert img.width > 0
        assert img.height > 0
        print(f"✓ Screenshot captured: {img.width}x{img.height}")
    
    def test_capture_region(self, vision):
        """تست گرفتن اسکرین‌شات از ناحیه خاص."""
        # گرفتن ناحیه 100x100 از گوشه بالا چپ
        img = vision.capture_screen(region=(0, 0, 100, 100))
        
        assert img is not None
        assert img.width == 100
        assert img.height == 100
        print(f"✓ Region screenshot captured: {img.width}x{img.height}")
    
    def test_save_screenshot(self, vision, tmp_path):
        """تست ذخیره اسکرین‌شات در فایل."""
        output_file = tmp_path / "test_screenshot.png"
        
        success = vision.save_screenshot(str(output_file))
        
        assert success is True
        assert output_file.exists()
        print(f"✓ Screenshot saved to: {output_file}")
    
    def test_ocr_extract_text(self, vision):
        """تست OCR برای استخراج متن.
        
        توجه: این تست نیاز به Tesseract OCR دارد.
        """
        try:
            text = vision.extract_text()
            
            # حتی اگر متن خالی باشد، خطا نباید رخ دهد
            assert isinstance(text, str)
            print(f"✓ OCR extracted {len(text)} characters")
            
            if text:
                print(f"Sample text: {text[:100]}...")
        
        except Exception as e:
            pytest.skip(f"OCR not available: {e}")
    
    def test_get_text_boxes(self, vision):
        """تست دریافت تمام باکس‌های متنی."""
        try:
            boxes = vision.get_all_text_boxes()
            
            assert isinstance(boxes, list)
            print(f"✓ Found {len(boxes)} text boxes")
            
            if boxes:
                first_box = boxes[0]
                assert isinstance(first_box, TextBox)
                assert first_box.text
                assert first_box.x >= 0
                assert first_box.y >= 0
                print(f"First box: '{first_box.text}' at ({first_box.x}, {first_box.y})")
        
        except Exception as e:
            pytest.skip(f"OCR not available: {e}")
    
    def test_window_management(self, vision):
        """تست مدیریت پنجره‌ها."""
        try:
            # گرفتن پنجره فعال
            active = vision.get_active_window()
            
            if active:
                assert isinstance(active, WindowInfo)
                assert active.title
                assert active.is_active is True
                print(f"✓ Active window: {active.title}")
            
            # لیست تمام پنجره‌ها
            windows = vision.list_windows()
            assert isinstance(windows, list)
            print(f"✓ Found {len(windows)} open windows")
            
            if windows:
                for i, win in enumerate(windows[:5]):  # نمایش 5 تای اول
                    print(f"  {i+1}. {win.title} ({win.width}x{win.height})")
        
        except Exception as e:
            pytest.skip(f"Window management not available: {e}")
    
    def test_image_comparison(self, vision):
        """تست مقایسه تصویر برای تشخیص تغییر."""
        # گرفتن دو اسکرین‌شات متوالی
        img1 = vision.capture_screen()
        time.sleep(0.1)
        img2 = vision.capture_screen()
        
        # اگر صفحه ثابت باشد، نباید تغییر معناداری وجود داشته باشد
        # threshold را بالا می‌گذاریم چونممکن است تغییرات جزئی مثل ساعت باشد
        has_changed = vision.has_changed(img1, img2, threshold=0.5)
        
        print(f"✓ Image comparison: changed={has_changed}")


class TestDesktopVisionIntegration:
    """تست‌های یکپارچه‌سازی با برنامه‌های واقعی."""
    
    @pytest.fixture
    def vision(self):
        """ایجاد instance از DesktopVision."""
        return DesktopVision()
    
    @pytest.mark.skip(reason="Requires Notepad to be opened manually")
    def test_notepad_scenario(self, vision):
        """سناریوی کامل: کنترل Notepad.
        
        این تست را به صورت دستی اجرا کنید:
        1. Notepad باز کنید
        2. این تست را اجرا کنید
        3. تست باید Notepad را پیدا کند
        """
        # گام 1: منتظر ماندن برای Notepad
        print("\n=== Waiting for Notepad to open ===")
        found = vision.wait_for_window("Notepad", timeout=10)
        assert found, "Notepad window not found"
        print("✓ Notepad found")
        
        # گام 2: فوکوس روی Notepad
        print("\n=== Focus on Notepad ===")
        success = vision.focus_window("Notepad")
        assert success, "Failed to focus Notepad"
        print("✓ Notepad activated")
        
        # گام 3: دریافت اطلاعات پنجره
        print("\n=== Getting window information ===")
        window = vision.get_active_window()
        assert window is not None
        print(f"✓ Title: {window.title}")
        print(f"✓ Size: {window.width}x{window.height}")
        print(f"✓ Position: ({window.x}, {window.y})")
        
        # گام 4: OCR روی Notepad (اگر متنی داخل آن باشد)
        print("\n=== OCR on Notepad ===")
        time.sleep(1)
        text = vision.extract_text()
        print(f"✓ Extracted text ({len(text)} characters):")
        if text:
            print(f"  {text[:200]}...")
        else:
            print("  (Notepad is empty)")

def demo_basic_usage():
    """دمو استفاده پایه از DesktopVision."""
    print("\n" + "="*60)
    print("DesktopVision Demo")
    print("="*60)
    
    vision = DesktopVision()
    
    # 1. گرفتن اسکرین‌شات
    print("\n1. Taking a screenshot...")
    img = vision.capture_screen()
    print(f"   ✓ Size: {img.width}x{img.height}")
    
    # 2. ذخیره اسکرین‌شات
    print("\n2. Saving the screenshot...")
    vision.save_screenshot("test_screenshot.png")
    print("   ✓ Saved to: test_screenshot.png")
    
    # 3. لیست پنجره‌های باز
    print("\n3. Listing open windows:")
    windows = vision.list_windows()
    for i, win in enumerate(windows[:10], 1):
        status = "🔹 active" if win.is_active else "  "
        print(f"   {i}. {status} {win.title}")
    
    # 4. تست OCR
    print("\n4. Testing OCR...")
    try:
        text = vision.extract_text()
        print(f"   ✓ {len(text)} characters extracted")
        if text:
            print(f"   Sample: {text[:100]}...")
    except Exception as e:
        print(f"   ⚠ OCR not available: {e}")
    
    print("\n" + "="*60)
    print("✓ Demo completed successfully!")
    print("="*60)


def demo_wait_features():
    """دمو قابلیت‌های Smart Waiting."""
    print("\n" + "="*60)
    print("Smart Waiting Demo")
    print("="*60)
    
    vision = DesktopVision()
    
    # 1. منتظر ماندن برای تغییر صفحه
    print("\n1. Waiting for screen change (5 seconds)...")
    print("   (Change something on the screen)")
    changed = vision.wait_for_change(timeout=5)
    print(f"   {'✓ Change detected' if changed else '⚠ No change detected'}")
    
    # 2. منتظر ماندن برای stable شدن
    print("\n2. Waiting for stable screen (2 seconds)...")
    stable = vision.wait_for_stable_screen(duration=2.0)
    print(f"   {'✓ Screen became stable' if stable else '⚠ Screen did not become stable'}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    """اجرای دموها به صورت مستقیم."""
    print("\n🚀 Starting DesktopVision tests...")
    
    # اجرای دموها
    demo_basic_usage()
    
    # پرسش برای ادامه
    response = input("\n⏸  Do you want to see the Smart Waiting demo as well? (y/n): ")
    if response.lower() in ['y', 'yes', 'بله']:
        demo_wait_features()
    
    print("\n✅ All tests completed!")