# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""سیستم بینایی رایانه برای اتوماسیون Desktop ویندوز.

این ماژول قابلیت "دیدن" صفحه را به سیستم می‌دهد تا بتواند:
- اسکرین‌شات بگیرد
- متن روی صفحه را بخواند (OCR)
- پنجره‌ها را مدیریت کند
- عناصر UI را پیدا کند
- تغییرات را تشخیص دهد
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# Lazy imports for optional dependencies
PIL_AVAILABLE = False
TESSERACT_AVAILABLE = False
PYGETWINDOW_AVAILABLE = False

try:
    from PIL import Image, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    logger.warning("PIL not available. Install with: pip install pillow")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    logger.warning("pytesseract not available. Install with: pip install pytesseract")

try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    logger.warning("pygetwindow not available. Install with: pip install pygetwindow")


@dataclass
class TextBox:
    """باکس متنی شناسایی شده روی صفحه."""
    text: str
    x: int
    y: int
    width: int
    height: int
    confidence: float = 0.0
    
    @property
    def center(self) -> tuple[int, int]:
        """مرکز باکس متنی."""
        return (self.x + self.width // 2, self.y + self.height // 2)


@dataclass
class WindowInfo:
    """اطلاعات یک پنجره."""
    title: str
    x: int
    y: int
    width: int
    height: int
    is_active: bool = False
    
    @property
    def center(self) -> tuple[int, int]:
        """مرکز پنجره."""
        return (self.x + self.width // 2, self.y + self.height // 2)


class DesktopVision:
    """سیستم بینایی رایانه برای Desktop."""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Args:
            tesseract_cmd: مسیر اجرایی Tesseract (اختیاری)
                          اگر None باشد، از مسیر پیش‌فرض استفاده می‌شود
        """
        if not PIL_AVAILABLE:
            raise ImportError("PIL is required. Install with: pip install pillow")
        
        if tesseract_cmd and TESSERACT_AVAILABLE:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        self._last_screenshot: Optional[Image.Image] = None
        self._cache_enabled = True
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # بخش 1: Screenshot & Capture
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def capture_screen(self, region: Optional[tuple[int, int, int, int]] = None) -> Image.Image:
        """گرفتن اسکرین‌شات از صفحه.
        
        Args:
            region: ناحیه مشخص به صورت (x, y, width, height)
                   اگر None باشد، کل صفحه capture می‌شود
        
        Returns:
            تصویر PIL Image
        
        Example:
            >>> vision = DesktopVision()
            >>> img = vision.capture_screen()
            >>> img.size
            (1920, 1080)
        """
        try:
            if region:
                # تبدیل (x, y, w, h) به (left, top, right, bottom)
                x, y, w, h = region
                bbox = (x, y, x + w, y + h)
                screenshot = ImageGrab.grab(bbox=bbox)
            else:
                screenshot = ImageGrab.grab()
            
            if self._cache_enabled:
                self._last_screenshot = screenshot
            
            logger.debug("Screenshot captured: %dx%d", screenshot.width, screenshot.height)
            return screenshot
        
        except Exception as e:
            logger.exception("Failed to capture screenshot: %s", e)
            raise
    
    def save_screenshot(self, path: str, region: Optional[tuple] = None) -> bool:
        """ذخیره اسکرین‌شات در فایل.
        
        Args:
            path: مسیر فایل برای ذخیره
            region: ناحیه مشخص (اختیاری)
        
        Returns:
            True اگر موفق باشد
        """
        try:
            screenshot = self.capture_screen(region=region)
            screenshot.save(path)
            logger.info("Screenshot saved to: %s", path)
            return True
        except Exception as e:
            logger.exception("Failed to save screenshot: %s", e)
            return False
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # بخش 2: OCR - خواندن متن
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def extract_text(self, image: Optional[Image.Image] = None) -> str:
        """استخراج تمام متن از تصویر با OCR.
        
        Args:
            image: تصویر PIL (اگر None باشد، از آخرین screenshot استفاده می‌شود)
        
        Returns:
            متن استخراج شده
        """
        if not TESSERACT_AVAILABLE:
            logger.error("Tesseract OCR not available")
            return ""
        
        try:
            if image is None:
                image = self.capture_screen()
            
            text = pytesseract.image_to_string(image, lang='eng')
            logger.debug("Extracted text: %d characters", len(text))
            return text.strip()
        
        except Exception as e:
            logger.exception("OCR failed: %s", e)
            return ""
    
    def get_all_text_boxes(self, image: Optional[Image.Image] = None) -> list[TextBox]:
        """استخراج تمام باکس‌های متنی با موقعیت.
        
        Returns:
            لیستی از TextBox
        """
        if not TESSERACT_AVAILABLE:
            logger.error("Tesseract OCR not available")
            return []
        
        try:
            if image is None:
                image = self.capture_screen()
            
            # استفاده از image_to_data برای گرفتن موقعیت‌ها
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            text_boxes = []
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if not text:  # رد کردن باکس‌های خالی
                    continue
                
                confidence = float(data['conf'][i])
                if confidence < 0:  # رد کردن موارد با اطمینان پایین
                    continue
                
                text_box = TextBox(
                    text=text,
                    x=int(data['left'][i]),
                    y=int(data['top'][i]),
                    width=int(data['width'][i]),
                    height=int(data['height'][i]),
                    confidence=confidence
                )
                text_boxes.append(text_box)
            
            logger.debug("Found %d text boxes", len(text_boxes))
            return text_boxes
        
        except Exception as e:
            logger.exception("Failed to get text boxes: %s", e)
            return []
    
    def find_text(self, search_text: str, confidence_threshold: float = 60.0) -> Optional[tuple[int, int]]:
        """پیدا کردن مختصات یک متن خاص روی صفحه.
        
        Args:
            search_text: متن مورد جستجو
            confidence_threshold: حداقل اطمینان OCR (0-100)
        
        Returns:
            (x, y) مرکز متن یافت شده یا None
        """
        text_boxes = self.get_all_text_boxes()
        
        for box in text_boxes:
            if box.confidence < confidence_threshold:
                continue
            
            # جستجوی case-insensitive
            if search_text.lower() in box.text.lower():
                logger.info("Found '%s' at (%d, %d)", search_text, *box.center)
                return box.center
        
        logger.debug("Text '%s' not found", search_text)
        return None
    
    def find_text_fuzzy(self, search_text: str, threshold: float = 0.8) -> Optional[tuple[int, int]]:
        """پیدا کردن متن با تطابق تقریبی (fuzzy matching).
        
        مفید برای زمانی که OCR ممکن است اشتباه بخواند.
        
        Args:
            search_text: متن مورد جستجو
            threshold: حداقل شباهت (0-1)
        """
        try:
            from difflib import SequenceMatcher
        except ImportError:
            logger.warning("difflib not available for fuzzy matching")
            return self.find_text(search_text)
        
        text_boxes = self.get_all_text_boxes()
        best_match = None
        best_similarity = 0.0
        
        for box in text_boxes:
            similarity = SequenceMatcher(None, search_text.lower(), box.text.lower()).ratio()
            
            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_match = box.center
        
        if best_match:
            logger.info("Found fuzzy match for '%s' (similarity: %.2f)", search_text, best_similarity)
        else:
            logger.debug("No fuzzy match found for '%s'", search_text)
        
        return best_match
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # بخش 3: Window Management
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def get_active_window(self) -> Optional[WindowInfo]:
        """دریافت اطلاعات پنجره فعال فعلی.
        
        Returns:
            WindowInfo یا None اگر خطا رخ دهد
        """
        if not PYGETWINDOW_AVAILABLE:
            logger.error("pygetwindow not available")
            return None
        
        try:
            active = gw.getActiveWindow()
            if not active:
                return None
            
            return WindowInfo(
                title=active.title,
                x=active.left,
                y=active.top,
                width=active.width,
                height=active.height,
                is_active=True
            )
        except Exception as e:
            logger.exception("Failed to get active window: %s", e)
            return None
    
    def list_windows(self, filter_title: Optional[str] = None) -> list[WindowInfo]:
        """لیست تمام پنجره‌های باز.
        
        Args:
            filter_title: فیلتر بر اساس عنوان (اختیاری)
        
        Returns:
            لیست WindowInfo
        """
        if not PYGETWINDOW_AVAILABLE:
            logger.error("pygetwindow not available")
            return []
        
        try:
            windows = []
            active_title = None
            
            try:
                active = gw.getActiveWindow()
                if active:
                    active_title = active.title
            except Exception:
                pass
            
            for window in gw.getAllWindows():
                if not window.title:  # رد کردن پنجره‌های بدون عنوان
                    continue
                
                if filter_title and filter_title.lower() not in window.title.lower():
                    continue
                
                win_info = WindowInfo(
                    title=window.title,
                    x=window.left,
                    y=window.top,
                    width=window.width,
                    height=window.height,
                    is_active=(window.title == active_title)
                )
                windows.append(win_info)
            
            logger.debug("Found %d windows", len(windows))
            return windows
        
        except Exception as e:
            logger.exception("Failed to list windows: %s", e)
            return []
    
    def focus_window(self, title: str) -> bool:
        """فوکوس کردن روی پنجره با عنوان مشخص.
        
        Args:
            title: عنوان پنجره (یا بخشی از آن)
        
        Returns:
            True اگر موفق باشد
        """
        if not PYGETWINDOW_AVAILABLE:
            logger.error("pygetwindow not available")
            return False
        
        try:
            windows = gw.getWindowsWithTitle(title)
            if not windows:
                logger.warning("No window found with title: %s", title)
                return False
            
            window = windows[0]
            window.activate()
            time.sleep(0.3)  # کمی صبر برای فوکوس
            
            logger.info("Focused window: %s", window.title)
            return True
        
        except Exception as e:
            logger.exception("Failed to focus window '%s': %s", title, e)
            return False
    
    def wait_for_window(self, title: str, timeout: int = 30, check_interval: float = 0.5) -> bool:
        """منتظر ماندن تا پنجره‌ای با عنوان مشخص باز شود.
        
        Args:
            title: عنوان پنجره
            timeout: حداکثر زمان انتظار (ثانیه)
            check_interval: فاصله بررسی (ثانیه)
        
        Returns:
            True اگر پنجره باز شد
        """
        if not PYGETWINDOW_AVAILABLE:
            logger.error("pygetwindow not available")
            return False
        
        logger.info("Waiting for window: %s (timeout: %ds)", title, timeout)
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                windows = gw.getWindowsWithTitle(title)
                if windows:
                    logger.info("Window found: %s", title)
                    return True
            except Exception:
                pass
            
            time.sleep(check_interval)
        
        logger.warning("Window '%s' not found within timeout", title)
        return False
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # بخش 4: Change Detection
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def has_changed(self, baseline_image: Image.Image, current_image: Optional[Image.Image] = None, 
                    threshold: float = 0.1) -> bool:
        """بررسی تغییر بین دو تصویر.
        
        Args:
            baseline_image: تصویر مرجع
            current_image: تصویر فعلی (اگر None باشد، screenshot جدید می‌گیرد)
            threshold: حداقل درصد تفاوت برای تشخیص تغییر (0-1)
        
        Returns:
            True اگر تغییر معنادار وجود داشته باشد
        """
        try:
            if current_image is None:
                current_image = self.capture_screen()
            
            # تبدیل به numpy array برای مقایسه
            baseline_array = np.array(baseline_image)
            current_array = np.array(current_image)
            
            # resize اگر سایزها متفاوت باشند
            if baseline_array.shape != current_array.shape:
                from PIL import Image as PILImage
                current_image = current_image.resize(baseline_image.size)
                current_array = np.array(current_image)
            
            # محاسبه تفاوت
            diff = np.abs(baseline_array.astype(float) - current_array.astype(float))
            diff_ratio = np.mean(diff) / 255.0
            
            has_changed = diff_ratio > threshold
            logger.debug("Image diff ratio: %.3f (threshold: %.3f) → Changed: %s", 
                        diff_ratio, threshold, has_changed)
            
            return has_changed
        
        except Exception as e:
            logger.exception("Failed to compare images: %s", e)
            return False
    
    def wait_for_change(self, timeout: int = 30, region: Optional[tuple] = None, 
                       threshold: float = 0.1) -> bool:
        """منتظر ماندن تا صفحه تغییر کند.
        
        Args:
            timeout: حداکثر زمان انتظار (ثانیه)
            region: ناحیه خاص برای بررسی (اختیاری)
            threshold: حداقل تفاوت برای تشخیص تغییر
        
        Returns:
            True اگر تغییر رخ دهد
        """
        logger.info("Waiting for screen change (timeout: %ds)", timeout)
        baseline = self.capture_screen(region=region)
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            time.sleep(0.5)
            current = self.capture_screen(region=region)
            
            if self.has_changed(baseline, current, threshold=threshold):
                logger.info("Screen changed detected")
                return True
        
        logger.warning("No screen change detected within timeout")
        return False
    
    def wait_until_text_appears(self, text: str, timeout: int = 30) -> bool:
        """منتظر ماندن تا متن خاصی روی صفحه ظاهر شود.
        
        Args:
            text: متن مورد انتظار
            timeout: حداکثر زمان انتظار (ثانیه)
        
        Returns:
            True اگر متن ظاهر شود
        """
        logger.info("Waiting for text to appear: '%s' (timeout: %ds)", text, timeout)
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.find_text(text):
                logger.info("Text appeared: '%s'", text)
                return True
            time.sleep(1)
        
        logger.warning("Text '%s' did not appear within timeout", text)
        return False
    
    def wait_until_text_disappears(self, text: str, timeout: int = 30) -> bool:
        """منتظر ماندن تا متن خاصی از روی صفحه ناپدید شود.
        
        مفید برای انتظار پایان "Loading..." و مانند آن.
        
        Args:
            text: متن مورد انتظار برای ناپدید شدن
            timeout: حداکثر زمان انتظار (ثانیه)
        
        Returns:
            True اگر متن ناپدید شود
        """
        logger.info("Waiting for text to disappear: '%s' (timeout: %ds)", text, timeout)
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not self.find_text(text):
                logger.info("Text disappeared: '%s'", text)
                return True
            time.sleep(1)
        
        logger.warning("Text '%s' did not disappear within timeout", text)
        return False
    
    def wait_for_stable_screen(self, duration: float = 2.0, check_interval: float = 0.5) -> bool:
        """منتظر ماندن تا صفحه stable شود (بدون تغییر).
        
        مفید برای انتظار پایان انیمیشن‌ها.
        
        Args:
            duration: مدت زمان stable بودن مورد نیاز (ثانیه)
            check_interval: فاصله بررسی (ثانیه)
        
        Returns:
            True اگر صفحه stable شود
        """
        logger.info("Waiting for stable screen (duration: %.1fs)", duration)
        stable_start = None
        baseline = self.capture_screen()
        
        while True:
            time.sleep(check_interval)
            current = self.capture_screen()
            
            if not self.has_changed(baseline, current, threshold=0.05):
                # صفحه stable است
                if stable_start is None:
                    stable_start = time.time()
                elif time.time() - stable_start >= duration:
                    logger.info("Screen is stable")
                    return True
            else:
                # صفحه تغییر کرد، ریست کردن timer
                stable_start = None
                baseline = current


__all__ = ["DesktopVision", "TextBox", "WindowInfo"]
