# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""تست‌های Enhanced Desktop Vision - قابلیت‌های پیشرفته.

این تست‌ها قابلیت‌های جدید Week 2 Day 3 را بررسی می‌کنند:
- Template Matching
- Color Detection
- UI Recognition
- Visual Validation
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from PIL import Image
import numpy as np

from core.desktop_vision import (
    DesktopVision,
    ImageMatch,
    TextBox
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Fixtures
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@pytest.fixture
def mock_vision():
    """DesktopVision با dependencies مانع شده."""
    with patch('core.desktop_vision.PIL_AVAILABLE', True):
        with patch('core.desktop_vision.CV2_AVAILABLE', True):
            vision = DesktopVision()
            return vision


@pytest.fixture
def sample_image():
    """تصویر نمونه برای تست."""
    return Image.new('RGB', (800, 600), color='white')


@pytest.fixture
def sample_template():
    """تصویر template نمونه."""
    return Image.new('RGB', (50, 30), color='blue')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# بخش 1: Template Matching Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_image_match_dataclass():
    """تست ImageMatch data class."""
    match = ImageMatch(x=100, y=200, width=50, height=30, confidence=0.95)
    
    assert match.x == 100
    assert match.y == 200
    assert match.width == 50
    assert match.height == 30
    assert match.confidence == 0.95
    assert match.center == (125, 215)  # x + w//2, y + h//2
    assert match.top_left == (100, 200)
    assert match.bottom_right == (150, 230)


@patch('core.desktop_vision.cv2')
def test_find_image_success(mock_cv2, mock_vision, tmp_path):
    """تست پیدا کردن تصویر موفق."""
    # ایجاد تصویر موقت
    template_path = tmp_path / "button.png"
    template = Image.new('RGB', (50, 30), color='blue')
    template.save(str(template_path))
    
    # Mock cv2
    mock_cv2.imread.return_value = np.zeros((30, 50, 3), dtype=np.uint8)
    mock_cv2.cvtColor.return_value = np.zeros((600, 800, 3), dtype=np.uint8)
    mock_cv2.matchTemplate.return_value = np.zeros((570, 750))
    mock_cv2.minMaxLoc.return_value = (0, 0.95, (0, 0), (100, 200))
    mock_cv2.TM_CCOEFF_NORMED = 5
    
    # Mock capture_screen
    mock_vision.capture_screen = Mock(return_value=Image.new('RGB', (800, 600)))
    
    # تست
    match = mock_vision.find_image(str(template_path), confidence=0.8)
    
    assert match is not None
    assert match.x == 100
    assert match.y == 200
    assert match.width == 50
    assert match.height == 30
    assert match.confidence == 0.95


@patch('core.desktop_vision.cv2')
def test_find_image_not_found(mock_cv2, mock_vision, tmp_path):
    """تست عدم پیدا کردن تصویر."""
    template_path = tmp_path / "button.png"
    template = Image.new('RGB', (50, 30), color='blue')
    template.save(str(template_path))
    
    # Mock cv2 - confidence پایین
    mock_cv2.imread.return_value = np.zeros((30, 50, 3), dtype=np.uint8)
    mock_cv2.cvtColor.return_value = np.zeros((600, 800, 3), dtype=np.uint8)
    mock_cv2.matchTemplate.return_value = np.zeros((570, 750))
    mock_cv2.minMaxLoc.return_value = (0, 0.5, (0, 0), (100, 200))  # کمتر از threshold
    mock_cv2.TM_CCOEFF_NORMED = 5
    
    mock_vision.capture_screen = Mock(return_value=Image.new('RGB', (800, 600)))
    
    match = mock_vision.find_image(str(template_path), confidence=0.8)
    
    assert match is None


@patch('core.desktop_vision.cv2')
def test_find_all_images(mock_cv2, mock_vision, tmp_path):
    """تست پیدا کردن تمام نمونه‌های تصویر."""
    template_path = tmp_path / "icon.png"
    template = Image.new('RGB', (20, 20), color='red')
    template.save(str(template_path))
    
    # Mock cv2 - چند match
    mock_cv2.imread.return_value = np.zeros((20, 20, 3), dtype=np.uint8)
    mock_cv2.cvtColor.return_value = np.zeros((600, 800, 3), dtype=np.uint8)
    
    # Mock matchTemplate برگرداندن آرایه
    mock_result = np.zeros((580, 780))
    mock_cv2.matchTemplate.return_value = mock_result
    mock_cv2.TM_CCOEFF_NORMED = 5
    
    # Mock minMaxLoc برای برگرداندن چند match
    mock_cv2.minMaxLoc.side_effect = [
        (0, 0.95, (0, 0), (100, 100)),
        (0, 0.92, (0, 0), (200, 150)),
        (0, 0.88, (0, 0), (300, 200)),
        (0, 0.7, (0, 0), (400, 250))  # کمتر از threshold
    ]
    
    mock_vision.capture_screen = Mock(return_value=Image.new('RGB', (800, 600)))
    
    matches = mock_vision.find_all_images(str(template_path), confidence=0.8, max_results=5)
    
    assert len(matches) == 3  # سه مورد بالای 0.8
    assert all(isinstance(m, ImageMatch) for m in matches)


@patch('core.desktop_vision.cv2')
def test_wait_for_image(mock_cv2, mock_vision, tmp_path):
    """تست انتظار برای ظاهر شدن تصویر."""
    template_path = tmp_path / "loading.png"
    template = Image.new('RGB', (40, 40), color='green')
    template.save(str(template_path))
    
    # Mock find_image برای برگرداندن match در تلاش دوم
    mock_vision.find_image = Mock(side_effect=[
        None,  # تلاش اول
        ImageMatch(x=150, y=250, width=40, height=40, confidence=0.9)  # تلاش دوم
    ])
    
    match = mock_vision.wait_for_image(str(template_path), timeout=5, check_interval=0.1)
    
    assert match is not None
    assert match.confidence == 0.9


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# بخش 2: Color Detection Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_get_pixel_color(mock_vision):
    """تست دریافت رنگ پیکسل."""
    # Mock screenshot با رنگ قرمز در (100, 200)
    mock_img = Image.new('RGB', (800, 600), color='white')
    mock_img.putpixel((100, 200), (255, 0, 0))
    mock_vision.capture_screen = Mock(return_value=mock_img)
    
    color = mock_vision.get_pixel_color(100, 200)
    
    assert color == (255, 0, 0)


def test_get_pixel_color_rgba(mock_vision):
    """تست دریافت رنگ از تصویر RGBA."""
    # تصویر با alpha channel
    mock_img = Image.new('RGBA', (800, 600), color=(100, 150, 200, 255))
    mock_vision.capture_screen = Mock(return_value=mock_img)
    
    color = mock_vision.get_pixel_color(100, 100)
    
    assert color == (100, 150, 200)  # باید alpha را نادیده بگیرد


def test_find_color(mock_vision):
    """تست پیدا کردن پیکسل‌های با رنگ خاص."""
    # ایجاد تصویر با چند پیکسل قرمز
    mock_img = Image.new('RGB', (100, 100), color='white')
    for x in [10, 20, 30]:
        for y in [40, 50]:
            mock_img.putpixel((x, y), (255, 0, 0))
    
    mock_vision.capture_screen = Mock(return_value=mock_img)
    
    positions = mock_vision.find_color((255, 0, 0), tolerance=10)
    
    assert len(positions) == 6  # 3x2 پیکسل
    assert (10, 40) in positions
    assert (30, 50) in positions


def test_find_color_with_tolerance(mock_vision):
    """تست پیدا کردن رنگ با تلرانس."""
    mock_img = Image.new('RGB', (50, 50), color='white')
    # رنگ‌های نزدیک به قرمز
    mock_img.putpixel((10, 10), (255, 0, 0))    # دقیق
    mock_img.putpixel((20, 20), (250, 5, 5))    # نزدیک
    mock_img.putpixel((30, 30), (200, 50, 50))  # دور
    
    mock_vision.capture_screen = Mock(return_value=mock_img)
    
    # tolerance کم
    positions = mock_vision.find_color((255, 0, 0), tolerance=10)
    assert len(positions) >= 2  # باید هر دو اولی را پیدا کند


def test_wait_for_color(mock_vision):
    """تست انتظار برای تغییر رنگ پیکسل."""
    # Mock get_pixel_color برای برگرداندن رنگ متفاوت در تلاش‌های مختلف
    mock_vision.get_pixel_color = Mock(side_effect=[
        (255, 255, 255),  # سفید
        (200, 200, 200),  # خاکستری
        (0, 255, 0)       # سبز (target)
    ])
    
    result = mock_vision.wait_for_color(100, 200, (0, 255, 0), tolerance=10, timeout=5, check_interval=0.1)
    
    assert result is True


def test_get_dominant_colors(mock_vision):
    """تست دریافت رنگ‌های غالب."""
    # تصویر با چند رنگ غالب
    mock_img = Image.new('RGB', (100, 100), color='white')
    
    # پر کردن بخش‌هایی با رنگ‌های مختلف
    for x in range(50):
        for y in range(50):
            mock_img.putpixel((x, y), (255, 0, 0))  # قرمز
    
    for x in range(50, 100):
        for y in range(50):
            mock_img.putpixel((x, y), (0, 0, 255))  # آبی
    
    mock_vision.capture_screen = Mock(return_value=mock_img)
    
    colors = mock_vision.get_dominant_colors(num_colors=3)
    
    assert len(colors) <= 3
    assert all(isinstance(c, tuple) and len(c) == 3 for c in colors)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# بخش 3: UI Recognition Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_find_button(mock_vision):
    """تست پیدا کردن دکمه."""
    # Mock get_all_text_boxes
    mock_boxes = [
        TextBox("Cancel", 100, 100, 60, 30, 85.0),
        TextBox("OK", 200, 100, 40, 30, 90.0),
        TextBox("Apply", 300, 100, 50, 30, 80.0)
    ]
    mock_vision.get_all_text_boxes = Mock(return_value=mock_boxes)
    
    pos = mock_vision.find_button("OK", confidence=0.7)
    
    assert pos is not None
    assert pos == (220, 115)  # center of OK button


def test_find_button_not_found(mock_vision):
    """تست عدم پیدا کردن دکمه."""
    mock_vision.get_all_text_boxes = Mock(return_value=[
        TextBox("Cancel", 100, 100, 60, 30, 85.0)
    ])
    
    pos = mock_vision.find_button("Submit")
    
    assert pos is None


def test_find_input_field_with_label(mock_vision):
    """تست پیدا کردن فیلد ورودی با label."""
    mock_vision.find_text = Mock(return_value=(150, 200))
    
    pos = mock_vision.find_input_field(label_text="Email:")
    
    assert pos is not None
    assert pos == (250, 200)  # offset شده از label


def test_find_input_field_without_label(mock_vision):
    """تست پیدا کردن فیلد بدون label."""
    pos = mock_vision.find_input_field()
    
    assert pos is None  # نمی‌تواند بدون label پیدا کند


def test_classify_element(mock_vision):
    """تست طبقه‌بندی نوع المان."""
    # Mock capture_screen و extract_text
    mock_img = Image.new('RGB', (100, 50), color=(200, 200, 200))
    mock_vision.capture_screen = Mock(return_value=mock_img)
    mock_vision.extract_text = Mock(return_value="Button Text")
    
    element_type = mock_vision.classify_element((100, 100, 100, 50))
    
    assert element_type in ["button", "text_field", "label", "unknown"]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# بخش 4: Visual Validation Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_verify_click_success(mock_vision):
    """تست تأیید موفقیت کلیک."""
    # تصاویر قبل و بعد
    before_img = Image.new('RGB', (100, 100), color='white')
    after_img = Image.new('RGB', (100, 100), color='gray')
    
    mock_vision.capture_screen = Mock(side_effect=[before_img, after_img])
    mock_vision.has_changed = Mock(return_value=True)
    
    result = mock_vision.verify_click_success((100, 100, 100, 100), timeout=1.0)
    
    assert result is True


def test_verify_click_failed(mock_vision):
    """تست شکست تأیید کلیک."""
    same_img = Image.new('RGB', (100, 100), color='white')
    
    mock_vision.capture_screen = Mock(return_value=same_img)
    mock_vision.has_changed = Mock(return_value=False)
    
    result = mock_vision.verify_click_success((100, 100, 100, 100), timeout=0.5)
    
    assert result is False


def test_verify_text_typed_exact(mock_vision):
    """تست تأیید تایپ متن (exact match)."""
    mock_vision.extract_text = Mock(return_value="Hello World")
    
    result = mock_vision.verify_text_typed("Hello World", fuzzy=False, timeout=1.0)
    
    assert result is True


def test_verify_text_typed_fuzzy(mock_vision):
    """تست تأیید تایپ متن (fuzzy match)."""
    # OCR ممکن است با خطا بخواند
    mock_vision.extract_text = Mock(return_value="Hel1o Wor1d")  # 1 به جای l
    
    result = mock_vision.verify_text_typed("Hello World", fuzzy=True, timeout=1.0)
    
    assert result is True  # fuzzy matching باید بپذیرد


def test_verify_text_typed_not_found(mock_vision):
    """تست عدم یافتن متن."""
    mock_vision.extract_text = Mock(return_value="Different Text")
    
    result = mock_vision.verify_text_typed("Expected Text", timeout=0.5)
    
    assert result is False


def test_verify_element_visible_by_text(mock_vision):
    """تست تأیید visibility المان با متن."""
    mock_vision.find_text = Mock(return_value=(200, 300))
    
    result = mock_vision.verify_element_visible("Submit", method="text", timeout=1.0)
    
    assert result is True


@patch('core.desktop_vision.cv2')
def test_verify_element_visible_by_image(mock_cv2, mock_vision):
    """تست تأیید visibility المان با تصویر."""
    mock_match = ImageMatch(x=100, y=200, width=50, height=30, confidence=0.9)
    mock_vision.find_image = Mock(return_value=mock_match)
    
    result = mock_vision.verify_element_visible("button.png", method="image", timeout=1.0)
    
    assert result is True


def test_compare_screenshots(mock_vision):
    """تست مقایسه دو اسکرین‌شات."""
    img1 = Image.new('RGB', (100, 100), color='white')
    img2 = Image.new('RGB', (100, 100), color='white')
    
    similarity = mock_vision.compare_screenshots(img1, img2)
    
    assert similarity > 0.99  # باید تقریباً یکسان باشند


def test_compare_screenshots_different(mock_vision):
    """تست مقایسه دو اسکرین‌شات متفاوت."""
    img1 = Image.new('RGB', (100, 100), color='white')
    img2 = Image.new('RGB', (100, 100), color='black')
    
    similarity = mock_vision.compare_screenshots(img1, img2)
    
    assert similarity < 0.5  # باید خیلی متفاوت باشند


def test_compare_screenshots_different_sizes(mock_vision):
    """تست مقایسه تصاویر با سایز متفاوت."""
    img1 = Image.new('RGB', (100, 100), color='white')
    img2 = Image.new('RGB', (200, 150), color='white')
    
    similarity = mock_vision.compare_screenshots(img1, img2)
    
    assert 0 <= similarity <= 1  # باید resize و مقایسه کند


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Integration Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_enhanced_vision_integration(mock_vision):
    """تست یکپارچگی قابلیت‌های enhanced vision."""
    # Scenario: پیدا کردن دکمه و کلیک
    
    # 1. پیدا کردن دکمه با تصویر
    mock_match = ImageMatch(x=300, y=400, width=80, height=40, confidence=0.92)
    mock_vision.find_image = Mock(return_value=mock_match)
    
    button = mock_vision.find_image("submit_button.png", confidence=0.9)
    assert button is not None
    
    # 2. بررسی رنگ قبل از کلیک
    mock_vision.get_pixel_color = Mock(return_value=(200, 200, 200))  # خاکستری
    color_before = mock_vision.get_pixel_color(*button.center)
    assert color_before == (200, 200, 200)
    
    # 3. شبیه‌سازی کلیک (در تست واقعی از MouseController استفاده می‌شود)
    # ...click...
    
    # 4. تأیید تغییر بصری
    before_img = Image.new('RGB', (800, 600), color='white')
    after_img = Image.new('RGB', (800, 600), color='lightgray')
    mock_vision.capture_screen = Mock(side_effect=[before_img, after_img])
    mock_vision.has_changed = Mock(return_value=True)
    
    click_verified = mock_vision.verify_click_success((300, 400, 80, 40))
    assert click_verified is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
