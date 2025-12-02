# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""سیستم انتظار هوشمند برای خودکارسازی Desktop.

این ماژول استراتژی‌های مختلف انتظار را فراهم می‌کند:
- انتظار برای ظاهر شدن عنصر
- انتظار برای تغییر صفحه
- انتظار برای پنجره
- انتظار برای پروسه
- Retry با Backoff
- Polling شرط
"""

from __future__ import annotations

import time
import logging
import psutil
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Callable, Any, List
from core.desktop_vision import DesktopVision

logger = logging.getLogger(__name__)


class WaitStrategy(Enum):
    """استراتژی‌های انتظار."""
    ELEMENT = "element"           # انتظار برای عنصر
    CHANGE = "change"             # انتظار برای تغییر
    WINDOW = "window"             # انتظار برای پنجره
    PROCESS = "process"           # انتظار برای پروسه
    IDLE = "idle"                 # انتظار برای Idle CPU
    COLOR = "color"               # انتظار برای رنگ خاص
    CONDITION = "condition"       # انتظار برای شرط


class RetryStrategy(Enum):
    """استراتژی‌های Retry."""
    LINEAR = "linear"             # فاصله ثابت
    EXPONENTIAL = "exponential"   # فاصله نمایی
    FIBONACCI = "fibonacci"       # فاصله فیبوناچی


@dataclass
class WaitResult:
    """نتیجه یک عملیات انتظار."""
    success: bool
    strategy: str
    duration: float
    attempts: int
    result: Optional[Any] = None
    error: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class SmartWaiter:
    """سیستم انتظار هوشمند.
    
    این کلاس استراتژی‌های مختلف انتظار را فراهم می‌کند تا
    برنامه بتواند به طور هوشمند منتظر بماند تا شرایط خاصی
    برقرار شود.
    
    Example:
        >>> from core.smart_wait import SmartWaiter
        >>> waiter = SmartWaiter()
        >>> 
        >>> # انتظار برای ظاهر شدن متن
        >>> result = waiter.wait_for_element("Submit", timeout=10)
        >>> 
        >>> # انتظار برای پنجره
        >>> result = waiter.wait_for_window("Notepad", timeout=5)
        >>> 
        >>> # Retry با Backoff
        >>> result = waiter.retry_with_backoff(
        >>>     lambda: some_action(),
        >>>     max_retries=3
        >>> )
    """
    
    def __init__(
        self,
        vision_system: Optional[DesktopVision] = None,
        vision: Optional[DesktopVision] = None,  # Backward compatibility
        default_timeout: float = 30.0,
        default_interval: float = 0.5,
    ):
        """مقداردهی اولیه SmartWaiter.
        
        Args:
            vision_system: سیستم بینایی برای تشخیص عناصر
            vision: Alias for vision_system (backward compatibility)
            default_timeout: زمان انتظار پیش‌فرض (ثانیه)
            default_interval: فاصله بررسی پیش‌فرض (ثانیه)
        """
        # Backward compatibility: support both vision and vision_system
        self.vision = vision or vision_system or DesktopVision()
        self.default_timeout = default_timeout
        self.default_interval = default_interval
        
        # آمار
        self.stats = {
            'total_waits': 0,
            'successful_waits': 0,
            'timeout_waits': 0,
            'total_wait_time': 0.0,
        }
        
        # History
        self.wait_history: List[WaitResult] = []
        self.max_history = 100
        
        logger.info(
            f"SmartWaiter initialized: "
            f"timeout={default_timeout}s, interval={default_interval}s"
        )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Element Waiting
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def wait_for_element(
        self,
        target: str,
        timeout: Optional[float] = None,
        check_interval: Optional[float] = None,
        confidence: float = 0.8,
    ) -> WaitResult:
        """انتظار برای ظاهر شدن عنصر (متن).
        
        Args:
            target: متن هدف برای جستجو
            timeout: حداکثر زمان انتظار (None = default)
            check_interval: فاصله بررسی (None = default)
            confidence: آستانه اطمینان OCR
        
        Returns:
            WaitResult با نتیجه
        
        Example:
            >>> result = waiter.wait_for_element("Submit", timeout=10)
            >>> if result.success:
            >>>     print(f"Found at: {result.result}")
        """
        timeout = timeout or self.default_timeout
        check_interval = check_interval or self.default_interval
        
        start_time = time.time()
        attempts = 0
        
        logger.info(f"Waiting for element: '{target}' (timeout={timeout}s)")
        
        while (time.time() - start_time) < timeout:
            attempts += 1
            
            # جستجوی متن (رفع API mismatch - استفاده از confidence_threshold)
            location = self.vision.find_text(target, confidence_threshold=confidence)
            
            if location:
                duration = time.time() - start_time
                logger.info(
                    f"Element found after {duration:.2f}s ({attempts} attempts)"
                )
                
                result = WaitResult(
                    success=True,
                    strategy=WaitStrategy.ELEMENT.value,
                    duration=duration,
                    attempts=attempts,
                    result=location,
                )
                
                self._record_wait(result)
                return result
            
            time.sleep(check_interval)
        
        # Timeout
        duration = time.time() - start_time
        logger.warning(f"Element not found: '{target}' after {duration:.2f}s")
        
        result = WaitResult(
            success=False,
            strategy=WaitStrategy.ELEMENT.value,
            duration=duration,
            attempts=attempts,
            error=f"Element '{target}' not found within {timeout}s",
        )
        
        self._record_wait(result)
        return result
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Change Detection Waiting
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def wait_for_change(
        self,
        region: Optional[tuple[int, int, int, int]] = None,
        threshold: float = 0.1,
        timeout: Optional[float] = None,
        check_interval: Optional[float] = None,
    ) -> WaitResult:
        """انتظار برای تغییر در صفحه.
        
        Args:
            region: ناحیه برای بررسی (x, y, w, h) - None = کل صفحه
            threshold: آستانه تغییر (0-1)
            timeout: حداکثر زمان انتظار
            check_interval: فاصله بررسی
        
        Returns:
            WaitResult با نتیجه
        
        Example:
            >>> # انتظار برای تغییر در ناحیه
            >>> result = waiter.wait_for_change(
            >>>     region=(100, 100, 500, 500),
            >>>     threshold=0.1,
            >>>     timeout=10
            >>> )
        """
        timeout = timeout or self.default_timeout
        check_interval = check_interval or self.default_interval
        
        start_time = time.time()
        attempts = 0
        
        logger.info(f"Waiting for change (threshold={threshold})")
        
        # گرفتن اسکرین‌شات اولیه
        initial_screenshot = self.vision.take_screenshot(region=region)
        if initial_screenshot is None:
            return WaitResult(
                success=False,
                strategy=WaitStrategy.CHANGE.value,
                duration=0.0,
                attempts=0,
                error="Failed to take initial screenshot",
            )
        
        while (time.time() - start_time) < timeout:
            attempts += 1
            time.sleep(check_interval)
            
            # گرفتن اسکرین‌شات جدید
            current_screenshot = self.vision.take_screenshot(region=region)
            if current_screenshot is None:
                continue
            
            # بررسی تغییر
            changed = self.vision.has_changed(
                initial_screenshot,
                current_screenshot,
                threshold=threshold
            )
            
            if changed:
                duration = time.time() - start_time
                logger.info(f"Change detected after {duration:.2f}s")
                
                result = WaitResult(
                    success=True,
                    strategy=WaitStrategy.CHANGE.value,
                    duration=duration,
                    attempts=attempts,
                    result=True,
                )
                
                self._record_wait(result)
                return result
        
        # Timeout
        duration = time.time() - start_time
        logger.warning(f"No change detected after {duration:.2f}s")
        
        result = WaitResult(
            success=False,
            strategy=WaitStrategy.CHANGE.value,
            duration=duration,
            attempts=attempts,
            error=f"No change detected within {timeout}s",
        )
        
        self._record_wait(result)
        return result
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Window Waiting
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def wait_for_window(
        self,
        title: str,
        timeout: Optional[float] = None,
        check_interval: Optional[float] = None,
        partial_match: bool = True,
    ) -> WaitResult:
        """انتظار برای باز شدن پنجره.
        
        Args:
            title: عنوان پنجره
            timeout: حداکثر زمان انتظار
            check_interval: فاصله بررسی
            partial_match: مطابقت جزئی یا کامل
        
        Returns:
            WaitResult با نتیجه
        
        Example:
            >>> result = waiter.wait_for_window("Notepad", timeout=5)
            >>> if result.success:
            >>>     print("Window found!")
        """
        timeout = timeout or self.default_timeout
        check_interval = check_interval or self.default_interval
        
        start_time = time.time()
        attempts = 0
        
        logger.info(f"Waiting for window: '{title}' (timeout={timeout}s)")
        
        while (time.time() - start_time) < timeout:
            attempts += 1
            
            # جستجوی پنجره
            windows = self.vision.list_windows()
            
            for window in windows:
                window_title = window.get('title', '')
                
                if partial_match:
                    if title.lower() in window_title.lower():
                        duration = time.time() - start_time
                        logger.info(f"Window found: '{window_title}' after {duration:.2f}s")
                        
                        result = WaitResult(
                            success=True,
                            strategy=WaitStrategy.WINDOW.value,
                            duration=duration,
                            attempts=attempts,
                            result=window,
                        )
                        
                        self._record_wait(result)
                        return result
                else:
                    if title == window_title:
                        duration = time.time() - start_time
                        logger.info(f"Window found: '{window_title}' after {duration:.2f}s")
                        
                        result = WaitResult(
                            success=True,
                            strategy=WaitStrategy.WINDOW.value,
                            duration=duration,
                            attempts=attempts,
                            result=window,
                        )
                        
                        self._record_wait(result)
                        return result
            
            time.sleep(check_interval)
        
        # Timeout
        duration = time.time() - start_time
        logger.warning(f"Window not found: '{title}' after {duration:.2f}s")
        
        result = WaitResult(
            success=False,
            strategy=WaitStrategy.WINDOW.value,
            duration=duration,
            attempts=attempts,
            error=f"Window '{title}' not found within {timeout}s",
        )
        
        self._record_wait(result)
        return result
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Process Waiting
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def wait_for_process(
        self,
        name: str,
        timeout: Optional[float] = None,
        check_interval: Optional[float] = None,
        wait_for_exit: bool = False,
    ) -> WaitResult:
        """انتظار برای شروع یا پایان پروسه.
        
        Args:
            name: نام پروسه
            timeout: حداکثر زمان انتظار
            check_interval: فاصله بررسی
            wait_for_exit: منتظر خروج پروسه باشد (نه شروع)
        
        Returns:
            WaitResult با نتیجه
        
        Example:
            >>> # انتظار برای شروع Chrome
            >>> result = waiter.wait_for_process("chrome.exe", timeout=10)
            >>> 
            >>> # انتظار برای بسته شدن Notepad
            >>> result = waiter.wait_for_process(
            >>>     "notepad.exe",
            >>>     wait_for_exit=True
            >>> )
        """
        timeout = timeout or self.default_timeout
        check_interval = check_interval or self.default_interval
        
        start_time = time.time()
        attempts = 0
        
        action = "exit" if wait_for_exit else "start"
        logger.info(f"Waiting for process {action}: '{name}' (timeout={timeout}s)")
        
        while (time.time() - start_time) < timeout:
            attempts += 1
            
            # بررسی پروسه
            process_running = self._is_process_running(name)
            
            # اگر منتظر شروع هستیم و پروسه در حال اجرا است
            if not wait_for_exit and process_running:
                duration = time.time() - start_time
                logger.info(f"Process started: '{name}' after {duration:.2f}s")
                
                result = WaitResult(
                    success=True,
                    strategy=WaitStrategy.PROCESS.value,
                    duration=duration,
                    attempts=attempts,
                    result=True,
                )
                
                self._record_wait(result)
                return result
            
            # اگر منتظر خروج هستیم و پروسه در حال اجرا نیست
            if wait_for_exit and not process_running:
                duration = time.time() - start_time
                logger.info(f"Process exited: '{name}' after {duration:.2f}s")
                
                result = WaitResult(
                    success=True,
                    strategy=WaitStrategy.PROCESS.value,
                    duration=duration,
                    attempts=attempts,
                    result=True,
                )
                
                self._record_wait(result)
                return result
            
            time.sleep(check_interval)
        
        # Timeout
        duration = time.time() - start_time
        logger.warning(f"Process {action} timeout: '{name}' after {duration:.2f}s")
        
        result = WaitResult(
            success=False,
            strategy=WaitStrategy.PROCESS.value,
            duration=duration,
            attempts=attempts,
            error=f"Process '{name}' did not {action} within {timeout}s",
        )
        
        self._record_wait(result)
        return result
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CPU Idle Waiting
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def wait_for_idle(
        self,
        cpu_threshold: float = 10.0,
        duration: float = 2.0,
        timeout: Optional[float] = None,
        check_interval: float = 0.5,
    ) -> WaitResult:
        """انتظار برای Idle شدن CPU.
        
        Args:
            cpu_threshold: آستانه CPU (درصد)
            duration: مدت زمان Idle مورد نیاز (ثانیه)
            timeout: حداکثر زمان انتظار
            check_interval: فاصله بررسی
        
        Returns:
            WaitResult با نتیجه
        
        Example:
            >>> # انتظار تا CPU زیر 10% برای 2 ثانیه
            >>> result = waiter.wait_for_idle(
            >>>     cpu_threshold=10.0,
            >>>     duration=2.0,
            >>>     timeout=30
            >>> )
        """
        timeout = timeout or self.default_timeout
        
        start_time = time.time()
        idle_start = None
        attempts = 0
        
        logger.info(
            f"Waiting for CPU idle: <{cpu_threshold}% for {duration}s "
            f"(timeout={timeout}s)"
        )
        
        while (time.time() - start_time) < timeout:
            attempts += 1
            
            # بررسی CPU
            cpu_percent = psutil.cpu_percent(interval=check_interval)
            
            if cpu_percent < cpu_threshold:
                # CPU Idle است
                if idle_start is None:
                    idle_start = time.time()
                
                idle_duration = time.time() - idle_start
                
                if idle_duration >= duration:
                    total_duration = time.time() - start_time
                    logger.info(f"CPU idle achieved after {total_duration:.2f}s")
                    
                    result = WaitResult(
                        success=True,
                        strategy=WaitStrategy.IDLE.value,
                        duration=total_duration,
                        attempts=attempts,
                        result={'cpu_percent': cpu_percent},
                    )
                    
                    self._record_wait(result)
                    return result
            else:
                # CPU مشغول است - ریست کردن شمارنده
                idle_start = None
        
        # Timeout
        total_duration = time.time() - start_time
        logger.warning(f"CPU idle timeout after {total_duration:.2f}s")
        
        result = WaitResult(
            success=False,
            strategy=WaitStrategy.IDLE.value,
            duration=total_duration,
            attempts=attempts,
            error=f"CPU did not become idle within {timeout}s",
        )
        
        self._record_wait(result)
        return result
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Color Waiting
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def wait_for_color(
        self,
        x: int,
        y: int,
        color: tuple[int, int, int],
        timeout: Optional[float] = None,
        check_interval: Optional[float] = None,
        tolerance: int = 10,
    ) -> WaitResult:
        """انتظار برای ظاهر شدن رنگ خاص.
        
        Args:
            x: موقعیت X
            y: موقعیت Y
            color: رنگ هدف (R, G, B)
            timeout: حداکثر زمان انتظار
            check_interval: فاصله بررسی
            tolerance: تلرانس رنگ (0-255)
        
        Returns:
            WaitResult با نتیجه
        
        Example:
            >>> # انتظار برای رنگ سبز در موقعیت خاص
            >>> result = waiter.wait_for_color(
            >>>     x=500,
            >>>     y=300,
            >>>     color=(0, 255, 0),  # سبز
            >>>     timeout=10
            >>> )
        """
        timeout = timeout or self.default_timeout
        check_interval = check_interval or self.default_interval
        
        start_time = time.time()
        attempts = 0
        
        logger.info(f"Waiting for color {color} at ({x}, {y})")
        
        while (time.time() - start_time) < timeout:
            attempts += 1
            
            # گرفتن رنگ پیکسل
            screenshot = self.vision.take_screenshot()
            if screenshot is None:
                time.sleep(check_interval)
                continue
            
            # بررسی موقعیت
            if x < 0 or y < 0 or x >= screenshot.width or y >= screenshot.height:
                return WaitResult(
                    success=False,
                    strategy=WaitStrategy.COLOR.value,
                    duration=0.0,
                    attempts=0,
                    error=f"Position ({x}, {y}) out of bounds",
                )
            
            # گرفتن رنگ
            current_color = screenshot.getpixel((x, y))
            
            # بررسی تطابق با tolerance
            if self._colors_match(current_color, color, tolerance):
                duration = time.time() - start_time
                logger.info(f"Color found after {duration:.2f}s")
                
                result = WaitResult(
                    success=True,
                    strategy=WaitStrategy.COLOR.value,
                    duration=duration,
                    attempts=attempts,
                    result=current_color,
                )
                
                self._record_wait(result)
                return result
            
            time.sleep(check_interval)
        
        # Timeout
        duration = time.time() - start_time
        logger.warning(f"Color not found after {duration:.2f}s")
        
        result = WaitResult(
            success=False,
            strategy=WaitStrategy.COLOR.value,
            duration=duration,
            attempts=attempts,
            error=f"Color {color} not found within {timeout}s",
        )
        
        self._record_wait(result)
        return result
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Retry & Backoff
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def retry_with_backoff(
        self,
        action: Callable[[], Any],
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        initial_delay: float = 1.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    ) -> WaitResult:
        """تلاش مجدد با Backoff.
        
        Args:
            action: تابع برای اجرا
            max_retries: حداکثر تعداد تلاش
            backoff_factor: ضریب افزایش تاخیر
            initial_delay: تاخیر اولیه (ثانیه)
            strategy: استراتژی Backoff
        
        Returns:
            WaitResult با نتیجه
        
        Example:
            >>> def risky_action():
            >>>     # عملی که ممکن است شکست بخورد
            >>>     return do_something()
            >>> 
            >>> result = waiter.retry_with_backoff(
            >>>     risky_action,
            >>>     max_retries=3,
            >>>     backoff_factor=2.0
            >>> )
        """
        start_time = time.time()
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = action()
                
                duration = time.time() - start_time
                logger.info(f"Action succeeded on attempt {attempt + 1}")
                
                wait_result = WaitResult(
                    success=True,
                    strategy=f"retry_{strategy.value}",
                    duration=duration,
                    attempts=attempt + 1,
                    result=result,
                )
                
                self._record_wait(wait_result)
                return wait_result
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                # محاسبه تاخیر
                if attempt < max_retries - 1:  # اگر آخرین تلاش نیست
                    delay = self._calculate_backoff_delay(
                        attempt,
                        initial_delay,
                        backoff_factor,
                        strategy
                    )
                    logger.info(f"Waiting {delay:.2f}s before retry...")
                    time.sleep(delay)
        
        # تمام تلاش‌ها شکست خوردند
        duration = time.time() - start_time
        logger.error(f"All {max_retries} attempts failed")
        
        wait_result = WaitResult(
            success=False,
            strategy=f"retry_{strategy.value}",
            duration=duration,
            attempts=max_retries,
            error=f"Action failed after {max_retries} attempts: {last_error}",
        )
        
        self._record_wait(wait_result)
        return wait_result
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Polling
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def poll_until(
        self,
        condition_func: Callable[[], bool],
        timeout: Optional[float] = None,
        interval: Optional[float] = None,
    ) -> WaitResult:
        """Polling تا برقرار شدن شرط.
        
        Args:
            condition_func: تابع شرط (باید True/False برگرداند)
            timeout: حداکثر زمان انتظار
            interval: فاصله بررسی
        
        Returns:
            WaitResult با نتیجه
        
        Example:
            >>> # انتظار تا فایل موجود شود
            >>> import os
            >>> result = waiter.poll_until(
            >>>     lambda: os.path.exists("output.txt"),
            >>>     timeout=30
            >>> )
        """
        timeout = timeout or self.default_timeout
        interval = interval or self.default_interval
        
        start_time = time.time()
        attempts = 0
        
        logger.info(f"Polling condition (timeout={timeout}s)")
        
        while (time.time() - start_time) < timeout:
            attempts += 1
            
            try:
                if condition_func():
                    duration = time.time() - start_time
                    logger.info(f"Condition met after {duration:.2f}s")
                    
                    result = WaitResult(
                        success=True,
                        strategy=WaitStrategy.CONDITION.value,
                        duration=duration,
                        attempts=attempts,
                        result=True,
                    )
                    
                    self._record_wait(result)
                    return result
                    
            except Exception as e:
                logger.warning(f"Condition check failed: {e}")
            
            time.sleep(interval)
        
        # Timeout
        duration = time.time() - start_time
        logger.warning(f"Condition not met after {duration:.2f}s")
        
        result = WaitResult(
            success=False,
            strategy=WaitStrategy.CONDITION.value,
            duration=duration,
            attempts=attempts,
            error=f"Condition not met within {timeout}s",
        )
        
        self._record_wait(result)
        return result
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Helper Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _is_process_running(self, name: str) -> bool:
        """بررسی در حال اجرا بودن پروسه."""
        name_lower = name.lower()
        
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() == name_lower:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return False
    
    def _colors_match(
        self,
        color1: tuple,
        color2: tuple,
        tolerance: int
    ) -> bool:
        """بررسی تطابق دو رنگ با tolerance."""
        r1, g1, b1 = color1[:3]
        r2, g2, b2 = color2[:3]
        
        return (
            abs(r1 - r2) <= tolerance and
            abs(g1 - g2) <= tolerance and
            abs(b1 - b2) <= tolerance
        )
    
    def _calculate_backoff_delay(
        self,
        attempt: int,
        initial_delay: float,
        backoff_factor: float,
        strategy: RetryStrategy,
    ) -> float:
        """محاسبه تاخیر Backoff."""
        if strategy == RetryStrategy.LINEAR:
            return initial_delay
        
        elif strategy == RetryStrategy.EXPONENTIAL:
            return initial_delay * (backoff_factor ** attempt)
        
        elif strategy == RetryStrategy.FIBONACCI:
            # محاسبه فیبوناچی
            if attempt == 0:
                return initial_delay
            elif attempt == 1:
                return initial_delay
            
            fib_prev = 1
            fib_curr = 1
            for _ in range(attempt - 1):
                fib_prev, fib_curr = fib_curr, fib_prev + fib_curr
            
            return initial_delay * fib_curr
        
        return initial_delay
    
    def _record_wait(self, result: WaitResult) -> None:
        """ثبت نتیجه انتظار."""
        self.wait_history.append(result)
        
        # محدود کردن طول history
        if len(self.wait_history) > self.max_history:
            self.wait_history.pop(0)
        
        # آپدیت آمار
        self.stats['total_waits'] += 1
        self.stats['total_wait_time'] += result.duration
        
        if result.success:
            self.stats['successful_waits'] += 1
        else:
            self.stats['timeout_waits'] += 1
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Statistics
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def get_stats(self) -> dict:
        """دریافت آمار."""
        stats = self.stats.copy()
        
        if stats['total_waits'] > 0:
            stats['success_rate'] = (
                stats['successful_waits'] / stats['total_waits'] * 100
            )
            stats['avg_wait_time'] = (
                stats['total_wait_time'] / stats['total_waits']
            )
        else:
            stats['success_rate'] = 0.0
            stats['avg_wait_time'] = 0.0
        
        return stats
    
    def get_wait_history(self, limit: int = 10) -> List[WaitResult]:
        """دریافت تاریخچه انتظارها."""
        return self.wait_history[-limit:]
