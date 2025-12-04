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
    import os
    TESSERACT_AVAILABLE = True
    
    # تلاش برای تنظیم خودکار Tesseract path در Windows
    import platform
    if platform.system() == "Windows":
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"✅ Tesseract found at: {path}")
                break
        else:
            logger.warning("⚠️ Tesseract executable not found. Please install from: https://github.com/UB-Mannheim/tesseract/wiki")
except ImportError:
    logger.warning("pytesseract not available. Install with: pip install pytesseract")

try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    logger.warning("pygetwindow not available. Install with: pip install pygetwindow")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    logger.warning("OpenCV not available. Install with: pip install opencv-python")
    CV2_AVAILABLE = False


@dataclass
class WindowInfo:
    """اطلاعات پنجره باز."""
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
    
    @property
    def bounds(self) -> tuple[int, int, int, int]:
        """محدوده پنجره (x, y, width, height)."""
        return (self.x, self.y, self.width, self.height)


@dataclass
class TextBox:
    """باکس متنی شناسایی شده روی صفحه."""
    text: str
    x: int
    y: int
    width: int
    height: int
    confidence: float  # Tesseract confidence (0-100)
    
    @property
    def center(self) -> tuple[int, int]:
        """مرکز باکس متنی."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def top_left(self) -> tuple[int, int]:
        """گوشه بالا چپ."""
        return (self.x, self.y)
    
    @property
    def bottom_right(self) -> tuple[int, int]:
        """گوشه پایین راست."""
        return (self.x + self.width, self.y + self.height)


@dataclass
class ImageMatch:
    """نتیجه تطابق تصویر."""
    x: int
    y: int
    width: int
    height: int
    confidence: float
    
    @property
    def center(self) -> tuple[int, int]:
        """مرکز تصویر پیدا شده."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def top_left(self) -> tuple[int, int]:
        """گوشه بالا چپ."""
        return (self.x, self.y)
    
    @property
    def bottom_right(self) -> tuple[int, int]:
        """گوشه پایین راست."""
        return (self.x + self.width, self.y + self.height)


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
    
    def find_text(self, search_text: str, confidence_threshold: float = 60.0, confidence: Optional[float] = None) -> Optional[tuple[int, int]]:
        """پیدا کردن مختصات یک متن خاص روی صفحه.
        
        Args:
            search_text: متن مورد جستجو
            confidence_threshold: حداقل اطمینان OCR (0-100)
            confidence: Alias for confidence_threshold (for compatibility)
        
        Returns:
            (x, y) مرکز متن یافت شده یا None
        """
        # Use confidence parameter if provided (for backward compatibility)
        if confidence is not None:
            confidence_threshold = confidence
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
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # بخش 5: Template Matching - پیدا کردن تصویر
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def find_image(self, template_path: str, confidence: float = 0.8, 
                   region: Optional[tuple[int, int, int, int]] = None) -> Optional[ImageMatch]:
        """پیدا کردن تصویر template روی صفحه.
        
        Args:
            template_path: مسیر فایل template
            confidence: حداقل اطمینان (0-1)
            region: ناحیه جستجو (اختیاری)
        
        Returns:
            ImageMatch اگر پیدا شود، None در غیر این صورت
        
        Example:
            >>> vision = DesktopVision()
            >>> match = vision.find_image("button.png", confidence=0.9)
            >>> if match:
            ...     print(f"Found at {match.center}")
        """
        if not CV2_AVAILABLE:
            logger.error("OpenCV not available. Install with: pip install opencv-python")
            return None
        
        try:
            # خواندن template
            template = cv2.imread(template_path)
            if template is None:
                logger.error("Failed to load template: %s", template_path)
                return None
            
            # گرفتن screenshot
            screenshot = self.capture_screen(region=region)
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Template matching
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= confidence:
                h, w = template.shape[:2]
                x, y = max_loc
                
                # اگر region مشخص شده، offset اضافه کن
                if region:
                    x += region[0]
                    y += region[1]
                
                match = ImageMatch(
                    x=x,
                    y=y,
                    width=w,
                    height=h,
                    confidence=float(max_val)
                )
                
                logger.info("Found image at (%d, %d) with confidence %.2f", x, y, max_val)
                return match
            else:
                logger.debug("Image not found (max confidence: %.2f)", max_val)
                return None
        
        except Exception as e:
            logger.exception("Failed to find image: %s", e)
            return None
    
    def find_all_images(self, template_path: str, confidence: float = 0.8,
                        region: Optional[tuple[int, int, int, int]] = None,
                        max_results: int = 10) -> list[ImageMatch]:
        """پیدا کردن تمام نمونه‌های یک template روی صفحه.
        
        Args:
            template_path: مسیر فایل template
            confidence: حداقل اطمینان (0-1)
            region: ناحیه جستجو (اختیاری)
            max_results: حداکثر تعداد نتایج
        
        Returns:
            لیست ImageMatch
        """
        if not CV2_AVAILABLE:
            logger.error("OpenCV not available")
            return []
        
        try:
            # خواندن template
            template = cv2.imread(template_path)
            if template is None:
                logger.error("Failed to load template: %s", template_path)
                return []
            
            # گرفتن screenshot
            screenshot = self.capture_screen(region=region)
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Template matching
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            
            # پیدا کردن تمام موارد بالای threshold
            h, w = template.shape[:2]
            matches = []
            
            while len(matches) < max_results:
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val < confidence:
                    break
                
                x, y = max_loc
                
                # اگر region مشخص شده، offset اضافه کن
                if region:
                    x += region[0]
                    y += region[1]
                
                match = ImageMatch(
                    x=x,
                    y=y,
                    width=w,
                    height=h,
                    confidence=float(max_val)
                )
                matches.append(match)
                
                # Suppress این ناحیه برای پیدا کردن match بعدی
                x1, y1 = max_loc
                result[max(0, y1-h//2):min(result.shape[0], y1+h//2),
                       max(0, x1-w//2):min(result.shape[1], x1+w//2)] = 0
            
            logger.info("Found %d image matches", len(matches))
            return matches
        
        except Exception as e:
            logger.exception("Failed to find all images: %s", e)
            return []
    
    def wait_for_image(self, template_path: str, confidence: float = 0.8,
                      timeout: int = 30, check_interval: float = 0.5) -> Optional[ImageMatch]:
        """منتظر ماندن تا تصویر ظاهر شود.
        
        Args:
            template_path: مسیر فایل template
            confidence: حداقل اطمینان
            timeout: حداکثر زمان انتظار (ثانیه)
            check_interval: فاصله بررسی (ثانیه)
        
        Returns:
            ImageMatch اگر پیدا شود
        """
        logger.info("Waiting for image: %s (timeout: %ds)", template_path, timeout)
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            match = self.find_image(template_path, confidence=confidence)
            if match:
                logger.info("Image found after %.1fs", time.time() - start_time)
                return match
            time.sleep(check_interval)
        
        logger.warning("Image not found within timeout")
        return None
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # بخش 6: Color Detection - تشخیص رنگ
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def get_pixel_color(self, x: int, y: int) -> tuple[int, int, int]:
        """دریافت رنگ یک پیکسل مشخص.
        
        Args:
            x: مختصات X
            y: مختصات Y
        
        Returns:
            (R, G, B) رنگ پیکسل
        
        Example:
            >>> vision = DesktopVision()
            >>> color = vision.get_pixel_color(100, 200)
            >>> print(f"RGB: {color}")
        """
        try:
            screenshot = self.capture_screen()
            pixel = screenshot.getpixel((x, y))
            
            # getpixel ممکن است RGB یا RGBA برگرداند
            if len(pixel) == 4:
                r, g, b, _ = pixel
            else:
                r, g, b = pixel
            
            logger.debug("Pixel at (%d, %d): RGB(%d, %d, %d)", x, y, r, g, b)
            return (r, g, b)
        
        except Exception as e:
            logger.exception("Failed to get pixel color: %s", e)
            return (0, 0, 0)
    
    def find_color(self, target_color: tuple[int, int, int], tolerance: int = 10,
                   region: Optional[tuple[int, int, int, int]] = None) -> list[tuple[int, int]]:
        """پیدا کردن تمام پیکسل‌های با رنگ مشخص.
        
        Args:
            target_color: رنگ مورد نظر (R, G, B)
            tolerance: تلرانس رنگ (0-255)
            region: ناحیه جستجو (اختیاری)
        
        Returns:
            لیست مختصات (x, y)
        
        Example:
            >>> vision = DesktopVision()
            >>> red_pixels = vision.find_color((255, 0, 0), tolerance=20)
        """
        try:
            screenshot = self.capture_screen(region=region)
            screenshot_array = np.array(screenshot)
            
            # محاسبه فاصله رنگ
            target = np.array(target_color)
            distances = np.sqrt(np.sum((screenshot_array - target) ** 2, axis=2))
            
            # پیدا کردن پیکسل‌های در محدوده تلرانس
            matches = np.argwhere(distances <= tolerance)
            
            # تبدیل به لیست (x, y)
            positions = [(int(x), int(y)) for y, x in matches]
            
            # اگر region مشخص شده، offset اضافه کن
            if region:
                positions = [(x + region[0], y + region[1]) for x, y in positions]
            
            logger.debug("Found %d pixels matching color %s", len(positions), target_color)
            return positions
        
        except Exception as e:
            logger.exception("Failed to find color: %s", e)
            return []
    
    def wait_for_color(self, x: int, y: int, target_color: tuple[int, int, int],
                      tolerance: int = 10, timeout: int = 30,
                      check_interval: float = 0.5) -> bool:
        """منتظر ماندن تا پیکسل مشخص به رنگ خاص تبدیل شود.
        
        Args:
            x: مختصات X
            y: مختصات Y
            target_color: رنگ مورد نظر (R, G, B)
            tolerance: تلرانس رنگ
            timeout: حداکثر زمان انتظار (ثانیه)
            check_interval: فاصله بررسی (ثانیه)
        
        Returns:
            True اگر رنگ ظاهر شود
        """
        logger.info("Waiting for color %s at (%d, %d)", target_color, x, y)
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_color = self.get_pixel_color(x, y)
            
            # بررسی فاصله رنگ
            distance = np.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(current_color, target_color)))
            
            if distance <= tolerance:
                logger.info("Color matched after %.1fs", time.time() - start_time)
                return True
            
            time.sleep(check_interval)
        
        logger.warning("Color not matched within timeout")
        return False
    
    def get_dominant_colors(self, region: Optional[tuple[int, int, int, int]] = None,
                           num_colors: int = 5) -> list[tuple[int, int, int]]:
        """دریافت رنگ‌های غالب در ناحیه مشخص.
        
        Args:
            region: ناحیه برای آنالیز (اختیاری)
            num_colors: تعداد رنگ‌های غالب
        
        Returns:
            لیست رنگ‌های غالب (R, G, B)
        """
        try:
            screenshot = self.capture_screen(region=region)
            screenshot_array = np.array(screenshot)
            
            # Reshape به لیست پیکسل‌ها
            pixels = screenshot_array.reshape(-1, 3)
            
            # استفاده از K-Means برای پیدا کردن رنگ‌های غالب
            if not CV2_AVAILABLE:
                # بدون OpenCV، استفاده از روش ساده
                unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
                sorted_indices = np.argsort(counts)[::-1]
                dominant = unique_colors[sorted_indices[:num_colors]]
            else:
                # استفاده از K-Means
                pixels_float = np.float32(pixels)
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
                _, labels, centers = cv2.kmeans(pixels_float, num_colors, None, criteria, 10,
                                               cv2.KMEANS_PP_CENTERS)
                dominant = np.uint8(centers)
            
            colors = [tuple(map(int, color)) for color in dominant]
            logger.debug("Dominant colors: %s", colors)
            return colors
        
        except Exception as e:
            logger.exception("Failed to get dominant colors: %s", e)
            return []
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # بخش 7: UI Recognition - شناسایی المان‌های رابط کاربری
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def find_button(self, button_text: str, confidence: float = 0.7) -> Optional[tuple[int, int]]:
        """پیدا کردن دکمه با متن مشخص.
        
        Args:
            button_text: متن روی دکمه
            confidence: حداقل اطمینان OCR
        
        Returns:
            (x, y) مرکز دکمه یا None
        """
        text_boxes = self.get_all_text_boxes()
        
        for box in text_boxes:
            if box.confidence < confidence * 100:
                continue
            
            # جستجوی تطابق متن
            if button_text.lower() in box.text.lower():
                logger.info("Found button '%s' at (%d, %d)", button_text, *box.center)
                return box.center
        
        logger.debug("Button '%s' not found", button_text)
        return None
    
    def find_input_field(self, label_text: Optional[str] = None,
                        region: Optional[tuple[int, int, int, int]] = None) -> Optional[tuple[int, int]]:
        """پیدا کردن فیلد ورودی.
        
        اگر label_text مشخص شده باشد، فیلد نزدیک به آن label را پیدا می‌کند.
        
        Args:
            label_text: برچسب فیلد (اختیاری)
            region: ناحیه جستجو (اختیاری)
        
        Returns:
            (x, y) مرکز فیلد ورودی
        """
        if label_text:
            # پیدا کردن label
            label_pos = self.find_text(label_text)
            if label_pos:
                # فیلد معمولاً کمی پایین‌تر یا سمت راست label است
                # تخمین موقعیت
                x, y = label_pos
                return (x + 100, y)  # offset تقریبی
        
        # اگر label نباشد، نمی‌توانیم فیلد را پیدا کنیم
        logger.warning("Cannot find input field without label_text or template")
        return None
    
    def classify_element(self, region: tuple[int, int, int, int]) -> str:
        """طبقه‌بندی نوع المان UI در ناحیه مشخص.
        
        Args:
            region: ناحیه برای بررسی (x, y, width, height)
        
        Returns:
            نوع المان: "button", "text_field", "label", "unknown"
        """
        try:
            screenshot = self.capture_screen(region=region)
            screenshot_array = np.array(screenshot)
            
            # بررسی ویژگی‌های ساده
            # دکمه: معمولاً رنگ یکنواخت و border
            # فیلد متنی: معمولاً سفید با border
            # برچسب: فقط متن
            
            # محاسبه واریانس رنگ
            variance = np.var(screenshot_array)
            
            # بررسی وجود متن
            text = self.extract_text(screenshot)
            has_text = bool(text.strip())
            
            # تصمیم‌گیری ساده
            if variance < 100 and has_text:
                return "button"
            elif variance < 50:
                return "text_field"
            elif has_text:
                return "label"
            else:
                return "unknown"
        
        except Exception as e:
            logger.exception("Failed to classify element: %s", e)
            return "unknown"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # بخش 8: Visual Validation - تأیید بصری
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def verify_click_success(self, region: tuple[int, int, int, int],
                            timeout: float = 2.0) -> bool:
        """تأیید موفقیت کلیک با بررسی تغییر بصری.
        
        Args:
            region: ناحیه برای بررسی تغییر
            timeout: زمان انتظار برای تغییر (ثانیه)
        
        Returns:
            True اگر تغییر مشاهده شود
        """
        logger.info("Verifying click success in region %s", region)
        
        # گرفتن اسکرین‌شات قبل
        before = self.capture_screen(region=region)
        
        # صبر کردن برای تغییر
        start_time = time.time()
        while time.time() - start_time < timeout:
            time.sleep(0.1)
            after = self.capture_screen(region=region)
            
            if self.has_changed(before, after, threshold=0.05):
                logger.info("Click verified: visual change detected")
                return True
        
        logger.warning("Click not verified: no visual change detected")
        return False
    
    def verify_text_typed(self, expected_text: str, region: Optional[tuple[int, int, int, int]] = None,
                         timeout: float = 2.0, fuzzy: bool = True) -> bool:
        """تأیید تایپ شدن متن با OCR.
        
        Args:
            expected_text: متن مورد انتظار
            region: ناحیه برای بررسی (اختیاری)
            timeout: زمان انتظار (ثانیه)
            fuzzy: استفاده از تطابق تقریبی
        
        Returns:
            True اگر متن یافت شود
        """
        logger.info("Verifying typed text: '%s'", expected_text)
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if region:
                screenshot = self.capture_screen(region=region)
                text = self.extract_text(screenshot)
            else:
                text = self.extract_text()
            
            # بررسی تطابق
            if fuzzy:
                from difflib import SequenceMatcher
                similarity = SequenceMatcher(None, expected_text.lower(), text.lower()).ratio()
                if similarity >= 0.8:
                    logger.info("Text verified with %.0f%% similarity", similarity * 100)
                    return True
            else:
                if expected_text.lower() in text.lower():
                    logger.info("Text verified: exact match found")
                    return True
            
            time.sleep(0.2)
        
        logger.warning("Text not verified within timeout")
        return False
    
    def verify_element_visible(self, element_desc: str, 
                              method: str = "text",
                              confidence: float = 0.8,
                              timeout: float = 5.0) -> bool:
        """تأیید قابل مشاهده بودن المان.
        
        Args:
            element_desc: شرح المان (متن یا مسیر تصویر)
            method: روش جستجو ("text" یا "image")
            confidence: حداقل اطمینان
            timeout: زمان انتظار (ثانیه)
        
        Returns:
            True اگر المان قابل مشاهده باشد
        """
        logger.info("Verifying element visibility: %s (method: %s)", element_desc, method)
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if method == "text":
                if self.find_text(element_desc, confidence_threshold=confidence * 100):
                    logger.info("Element verified visible by text")
                    return True
            elif method == "image":
                if self.find_image(element_desc, confidence=confidence):
                    logger.info("Element verified visible by image")
                    return True
            
            time.sleep(0.3)
        
        logger.warning("Element not visible within timeout")
        return False
    
    def compare_screenshots(self, screenshot1: Image.Image, screenshot2: Image.Image,
                           threshold: float = 0.95) -> float:
        """مقایسه دو اسکرین‌شات و محاسبه شباهت.
        
        Args:
            screenshot1: تصویر اول
            screenshot2: تصویر دوم
            threshold: آستانه شباهت (0-1)
        
        Returns:
            درصد شباهت (0-1)
        """
        try:
            # تبدیل به numpy array
            array1 = np.array(screenshot1)
            array2 = np.array(screenshot2)
            
            # اگر سایز متفاوت باشد، resize کن
            if array1.shape != array2.shape:
                screenshot2_resized = screenshot2.resize(screenshot1.size)
                array2 = np.array(screenshot2_resized)
            
            # محاسبه شباهت (1 - normalized difference)
            diff = np.abs(array1.astype(float) - array2.astype(float))
            max_diff = 255.0 * array1.size
            similarity = 1.0 - (np.sum(diff) / max_diff)
            
            logger.debug("Screenshot similarity: %.2f%%", similarity * 100)
            return similarity
        
        except Exception as e:
            logger.exception("Failed to compare screenshots: %s", e)
            return 0.0


__all__ = ["DesktopVision", "TextBox", "WindowInfo", "ImageMatch"]
