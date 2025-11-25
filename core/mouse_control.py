# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""کنترل هوشمند موس با یکپارچگی AI.

این ماژول فراتر از یک wrapper ساده برای pyautogui است - این یک سیستم هوشمند
کنترل موس است که با AI یکپارچه شده و می‌تواند:
- موقعیت‌های ایمن را تشخیص دهد
- بهترین مسیر حرکت را محاسبه کند
- از الگوهای رفتاری انسانی تقلید کند
- از Vision system برای هدف‌گیری دقیق استفاده کند
"""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Callable, Any

try:
    import pyautogui
except ImportError:
    pyautogui = None  # type: ignore

try:
    import numpy as np
except ImportError:
    np = None  # type: ignore

logger = logging.getLogger(__name__)


class MouseButton(Enum):
    """دکمه‌های موس."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class ClickPattern(Enum):
    """الگوهای کلیک برای تقلید از رفتار انسانی."""
    INSTANT = "instant"  # کلیک سریع (ربات‌وار)
    HUMAN_FAST = "human_fast"  # انسان سریع (0.05-0.1s)
    HUMAN_NORMAL = "human_normal"  # انسان عادی (0.1-0.2s)
    HUMAN_SLOW = "human_slow"  # انسان کند (0.2-0.5s)
    DOUBLE_CLICK = "double_click"  # دوبل کلیک
    TRIPLE_CLICK = "triple_click"  # تریپل کلیک


@dataclass
class MouseAction:
    """اطلاعات یک اقدام موس برای audit trail."""
    action_type: str  # 'click', 'move', 'drag', 'scroll'
    x: Optional[int] = None
    y: Optional[int] = None
    button: Optional[str] = None
    timestamp: Optional[datetime] = None
    duration: float = 0.0
    success: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class MouseController:
    """کنترلر هوشمند موس با یکپارچگی AI.
    
    این کلاس نه تنها موس را کنترل می‌کند، بلکه با سیستم Vision و AI
    یکپارچه شده تا اقدامات هوشمندانه‌تری انجام دهد.
    
    Example:
        >>> from core.mouse_control import MouseController
        >>> mouse = MouseController()
        >>> 
        >>> # کلیک ساده
        >>> mouse.click(100, 100)
        >>> 
        >>> # کلیک انسانی‌تر
        >>> mouse.click_human(100, 100, pattern=ClickPattern.HUMAN_NORMAL)
        >>> 
        >>> # حرکت هموار
        >>> mouse.move(500, 300, duration=0.5, smooth=True)
    """
    
    def __init__(
        self,
        safety_enabled: bool = True,
        human_behavior: bool = True,
        vision_system: Optional[Any] = None,
    ):
        """
        Args:
            safety_enabled: فعال‌سازی بررسی‌های امنیتی
            human_behavior: تقلید از رفتار انسانی (تصادفی‌سازی، تاخیر)
            vision_system: سیستم بینایی برای هدف‌گیری هوشمند (DesktopVision)
        """
        self.safety_enabled = safety_enabled
        self.human_behavior = human_behavior
        self.vision_system = vision_system
        
        # بررسی وجود pyautogui
        if pyautogui is None:
            raise ImportError("pyautogui is required. Install with: pip install pyautogui")
        
        # تنظیمات pyautogui
        pyautogui.FAILSAFE = True  # حرکت به گوشه برای توقف
        pyautogui.PAUSE = 0.1  # تاخیر پیش‌فرض
        
        # محدوده‌های امن (پیش‌فرض: کل صفحه منهای حاشیه‌ها)
        screen_width, screen_height = pyautogui.size()
        self.safe_bounds = {
            'min_x': 10,
            'max_x': screen_width - 10,
            'min_y': 10,
            'max_y': screen_height - 50,  # فضا برای taskbar
        }
        
        # History برای تحلیل الگو
        self.action_history: list[MouseAction] = []
        self.max_history = 100
        
        # آمار
        self.stats = {
            'total_clicks': 0,
            'total_moves': 0,
            'total_drags': 0,
            'total_scrolls': 0,
            'failed_actions': 0,
        }
        
        logger.info("MouseController initialized (safety=%s, human_behavior=%s, vision=%s)",
                   safety_enabled, human_behavior, vision_system is not None)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Safety & Validation
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def is_safe_position(self, x: int, y: int) -> bool:
        """بررسی امن بودن موقعیت.
        
        Args:
            x: موقعیت X
            y: موقعیت Y
        
        Returns:
            True اگر موقعیت امن باشد
        """
        if not self.safety_enabled:
            return True
        
        return (
            self.safe_bounds['min_x'] <= x <= self.safe_bounds['max_x'] and
            self.safe_bounds['min_y'] <= y <= self.safe_bounds['max_y']
        )
    
    def validate_coordinates(self, x: int, y: int) -> tuple[int, int]:
        """اعتبارسنجی و تصحیح مختصات.
        
        Args:
            x: موقعیت X
            y: موقعیت Y
        
        Returns:
            مختصات معتبر (x, y)
        
        Raises:
            ValueError: اگر مختصات خارج از محدوده امن باشد
        """
        if not self.is_safe_position(x, y):
            if self.safety_enabled:
                raise ValueError(
                    f"Unsafe position: ({x}, {y}). "
                    f"Safe bounds: x({self.safe_bounds['min_x']}-{self.safe_bounds['max_x']}), "
                    f"y({self.safe_bounds['min_y']}-{self.safe_bounds['max_y']})"
                )
            else:
                logger.warning("Unsafe position detected but safety is disabled: (%d, %d)", x, y)
        
        return x, y
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Human Behavior Simulation
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _add_human_variation(self, x: int, y: int, max_offset: int = 2) -> tuple[int, int]:
        """افزودن نویز انسانی به مختصات.
        
        انسان‌ها دقیقاً روی پیکسل target کلیک نمی‌کنند.
        این متد کمی نویز تصادفی اضافه می‌کند.
        """
        if not self.human_behavior:
            return x, y
        
        offset_x = random.randint(-max_offset, max_offset)
        offset_y = random.randint(-max_offset, max_offset)
        
        return x + offset_x, y + offset_y
    
    def _get_human_delay(self, pattern: ClickPattern) -> float:
        """تاخیر انسانی بر اساس الگو.
        
        Args:
            pattern: الگوی کلیک
        
        Returns:
            تاخیر به ثانیه
        """
        if not self.human_behavior:
            return 0.0
        
        delays = {
            ClickPattern.INSTANT: 0.0,
            ClickPattern.HUMAN_FAST: random.uniform(0.05, 0.1),
            ClickPattern.HUMAN_NORMAL: random.uniform(0.1, 0.2),
            ClickPattern.HUMAN_SLOW: random.uniform(0.2, 0.5),
            ClickPattern.DOUBLE_CLICK: random.uniform(0.05, 0.15),
            ClickPattern.TRIPLE_CLICK: random.uniform(0.05, 0.15),
        }
        
        return delays.get(pattern, 0.1)
    
    def _bezier_curve(
        self,
        start: tuple[int, int],
        end: tuple[int, int],
        control_points: int = 2,
        steps: int = 20
    ) -> list[tuple[int, int]]:
        """محاسبه منحنی Bezier برای حرکت طبیعی‌تر موس.
        
        انسان‌ها موس را به صورت خطی حرکت نمی‌دهند - مسیرشان
        کمی منحنی است.
        
        Args:
            start: نقطه شروع (x, y)
            end: نقطه پایان (x, y)
            control_points: تعداد نقاط کنترل
            steps: تعداد مراحل در مسیر
        
        Returns:
            لیست نقاط در مسیر
        """
        if not self.human_behavior:
            # خطی ساده
            return [start, end]
        
        # نقاط کنترل تصادفی
        controls = []
        for _ in range(control_points):
            cx = random.randint(
                min(start[0], end[0]),
                max(start[0], end[0])
            )
            cy = random.randint(
                min(start[1], end[1]),
                max(start[1], end[1])
            )
            controls.append((cx, cy))
        
        # محاسبه نقاط روی منحنی
        points = [start] + controls + [end]
        curve_points = []
        
        for i in range(steps + 1):
            t = i / steps
            # Bezier curve calculation
            point = self._bezier_point(points, t)
            curve_points.append((int(point[0]), int(point[1])))
        
        return curve_points
    
    def _bezier_point(self, points: list[tuple[int, int]], t: float) -> tuple[float, float]:
        """محاسبه یک نقطه روی منحنی Bezier."""
        n = len(points) - 1
        x = sum(
            self._binomial(n, i) * (1 - t) ** (n - i) * t ** i * points[i][0]
            for i in range(n + 1)
        )
        y = sum(
            self._binomial(n, i) * (1 - t) ** (n - i) * t ** i * points[i][1]
            for i in range(n + 1)
        )
        return x, y
    
    def _binomial(self, n: int, k: int) -> int:
        """ضریب دوجمله‌ای."""
        if k > n:
            return 0
        if k == 0 or k == n:
            return 1
        
        result = 1
        for i in range(min(k, n - k)):
            result = result * (n - i) // (i + 1)
        return result
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Core Mouse Operations
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def get_position(self) -> tuple[int, int]:
        """دریافت موقعیت فعلی موس.
        
        Returns:
            (x, y) موقعیت فعلی
        """
        x, y = pyautogui.position()
        return int(x), int(y)
    
    def move(
        self,
        x: int,
        y: int,
        duration: float = 0.5,
        smooth: bool = True
    ) -> bool:
        """حرکت موس به موقعیت مشخص.
        
        Args:
            x: موقعیت X هدف
            y: موقعیت Y هدف
            duration: مدت زمان حرکت (ثانیه)
            smooth: استفاده از منحنی Bezier برای حرکت طبیعی‌تر
        
        Returns:
            True اگر موفق باشد
        
        Example:
            >>> mouse.move(500, 300, duration=0.5, smooth=True)
            True
        """
        start_time = time.time()
        action = MouseAction(action_type='move', x=x, y=y)
        
        try:
            # اعتبارسنجی
            x, y = self.validate_coordinates(x, y)
            
            # افزودن نویز انسانی
            if self.human_behavior:
                x, y = self._add_human_variation(x, y)
            
            # حرکت
            if smooth and self.human_behavior:
                # حرکت با منحنی Bezier
                start_pos = self.get_position()
                curve_points = self._bezier_curve(start_pos, (x, y))
                
                for i, (px, py) in enumerate(curve_points):
                    progress = i / len(curve_points)
                    point_duration = duration * 0.05  # کوتاه برای هر نقطه
                    pyautogui.moveTo(px, py, duration=point_duration)
            else:
                # حرکت خطی
                pyautogui.moveTo(x, y, duration=duration)
            
            action.success = True
            action.duration = time.time() - start_time
            self.stats['total_moves'] += 1
            
            logger.debug("Mouse moved to (%d, %d) in %.3fs", x, y, action.duration)
            return True
            
        except Exception as e:
            action.success = False
            action.duration = time.time() - start_time
            self.stats['failed_actions'] += 1
            logger.error("Failed to move mouse to (%d, %d): %s", x, y, e)
            return False
        
        finally:
            self._log_action(action)
    
    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: MouseButton = MouseButton.LEFT,
        clicks: int = 1,
        interval: float = 0.1
    ) -> bool:
        """کلیک موس.
        
        Args:
            x: موقعیت X (None = موقعیت فعلی)
            y: موقعیت Y (None = موقعیت فعلی)
            button: دکمه موس
            clicks: تعداد کلیک‌ها
            interval: فاصله بین کلیک‌ها
        
        Returns:
            True اگر موفق باشد
        
        Example:
            >>> mouse.click(100, 100)  # کلیک چپ
            >>> mouse.click(100, 100, button=MouseButton.RIGHT)  # کلیک راست
            >>> mouse.click(100, 100, clicks=2)  # دوبل کلیک
        """
        start_time = time.time()
        action = MouseAction(
            action_type='click',
            x=x,
            y=y,
            button=button.value
        )
        
        try:
            # حرکت به موقعیت (اگر مشخص شده)
            if x is not None and y is not None:
                if not self.move(x, y, duration=0.3):
                    raise ValueError("Failed to move to target position")
            
            # کلیک
            pyautogui.click(
                button=button.value,
                clicks=clicks,
                interval=interval
            )
            
            action.success = True
            action.duration = time.time() - start_time
            self.stats['total_clicks'] += clicks
            
            logger.debug("Clicked %s button %d time(s) at (%s, %s)",
                        button.value, clicks, x or 'current', y or 'current')
            return True
            
        except Exception as e:
            action.success = False
            action.duration = time.time() - start_time
            self.stats['failed_actions'] += 1
            logger.error("Failed to click: %s", e)
            return False
        
        finally:
            self._log_action(action)
    
    def click_human(
        self,
        x: int,
        y: int,
        button: MouseButton = MouseButton.LEFT,
        pattern: ClickPattern = ClickPattern.HUMAN_NORMAL
    ) -> bool:
        """کلیک با الگوی رفتاری انسانی.
        
        این متد کلیک را شبیه‌تر به انسان می‌کند:
        - تاخیر تصادفی
        - نویز در موقعیت
        - الگوهای کلیک متنوع
        
        Args:
            x: موقعیت X
            y: موقعیت Y
            button: دکمه موس
            pattern: الگوی کلیک
        
        Returns:
            True اگر موفق باشد
        
        Example:
            >>> mouse.click_human(100, 100)  # کلیک طبیعی
            >>> mouse.click_human(100, 100, pattern=ClickPattern.DOUBLE_CLICK)
        """
        # تاخیر قبل از کلیک
        delay = self._get_human_delay(pattern)
        if delay > 0:
            time.sleep(delay)
        
        # تعداد کلیک‌ها بر اساس الگو
        clicks = 1
        if pattern == ClickPattern.DOUBLE_CLICK:
            clicks = 2
        elif pattern == ClickPattern.TRIPLE_CLICK:
            clicks = 3
        
        # اجرای کلیک
        return self.click(x, y, button=button, clicks=clicks)
    
    def drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 0.5,
        button: MouseButton = MouseButton.LEFT
    ) -> bool:
        """کشیدن از یک نقطه به نقطه دیگر.
        
        Args:
            start_x, start_y: نقطه شروع
            end_x, end_y: نقطه پایان
            duration: مدت زمان کشیدن
            button: دکمه موس برای نگه داشتن
        
        Returns:
            True اگر موفق باشد
        
        Example:
            >>> mouse.drag(100, 100, 500, 300)  # کشیدن فایل
        """
        start_time = time.time()
        action = MouseAction(
            action_type='drag',
            x=end_x,
            y=end_y
        )
        
        try:
            # اعتبارسنجی
            start_x, start_y = self.validate_coordinates(start_x, start_y)
            end_x, end_y = self.validate_coordinates(end_x, end_y)
            
            # حرکت به نقطه شروع
            self.move(start_x, start_y, duration=0.2)
            
            # کشیدن
            pyautogui.drag(
                end_x - start_x,
                end_y - start_y,
                duration=duration,
                button=button.value
            )
            
            action.success = True
            action.duration = time.time() - start_time
            self.stats['total_drags'] += 1
            
            logger.debug("Dragged from (%d,%d) to (%d,%d) in %.3fs",
                        start_x, start_y, end_x, end_y, action.duration)
            return True
            
        except Exception as e:
            action.success = False
            action.duration = time.time() - start_time
            self.stats['failed_actions'] += 1
            logger.error("Failed to drag: %s", e)
            return False
        
        finally:
            self._log_action(action)
    
    def scroll(
        self,
        clicks: int,
        x: Optional[int] = None,
        y: Optional[int] = None
    ) -> bool:
        """اسکرول صفحه.
        
        Args:
            clicks: تعداد کلیک‌های اسکرول (مثبت = بالا، منفی = پایین)
            x, y: موقعیت برای اسکرول (None = موقعیت فعلی)
        
        Returns:
            True اگر موفق باشد
        
        Example:
            >>> mouse.scroll(5)  # اسکرول به بالا
            >>> mouse.scroll(-5)  # اسکرول به پایین
        """
        start_time = time.time()
        action = MouseAction(action_type='scroll', x=x, y=y)
        
        try:
            # حرکت به موقعیت (اگر مشخص شده)
            if x is not None and y is not None:
                self.move(x, y, duration=0.2)
            
            # اسکرول
            pyautogui.scroll(clicks)
            
            action.success = True
            action.duration = time.time() - start_time
            self.stats['total_scrolls'] += 1
            
            logger.debug("Scrolled %d clicks", clicks)
            return True
            
        except Exception as e:
            action.success = False
            action.duration = time.time() - start_time
            self.stats['failed_actions'] += 1
            logger.error("Failed to scroll: %s", e)
            return False
        
        finally:
            self._log_action(action)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Vision-Guided Operations (AI Integration)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def click_on_text(
        self,
        text: str,
        button: MouseButton = MouseButton.LEFT,
        pattern: ClickPattern = ClickPattern.HUMAN_NORMAL
    ) -> bool:
        """کلیک روی متن با استفاده از Vision system.
        
        این یک operation هوشمند است که:
        1. از Vision برای پیدا کردن متن استفاده می‌کند
        2. روی مرکز متن کلیک می‌کند
        3. از الگوی رفتاری انسانی استفاده می‌کند
        
        Args:
            text: متن هدف
            button: دکمه موس
            pattern: الگوی کلیک
        
        Returns:
            True اگر موفق باشد
        
        Example:
            >>> mouse.click_on_text("OK")
            >>> mouse.click_on_text("Submit", pattern=ClickPattern.HUMAN_SLOW)
        
        Raises:
            ValueError: اگر Vision system تنظیم نشده باشد
            RuntimeError: اگر متن پیدا نشود
        """
        if self.vision_system is None:
            raise ValueError("Vision system not configured. Initialize with vision_system parameter.")
        
        logger.info("Looking for text: '%s'", text)
        
        # جستجوی متن با Vision
        text_boxes = self.vision_system.find_text_boxes(text)
        
        if not text_boxes:
            raise RuntimeError(f"Text not found: '{text}'")
        
        # استفاده از اولین نتیجه
        target_box = text_boxes[0]
        cx, cy = target_box.center
        
        logger.info("Found text '%s' at (%d, %d)", text, cx, cy)
        
        # کلیک انسانی
        return self.click_human(cx, cy, button=button, pattern=pattern)
    
    def click_on_image(
        self,
        image_path: str,
        confidence: float = 0.8,
        button: MouseButton = MouseButton.LEFT,
        pattern: ClickPattern = ClickPattern.HUMAN_NORMAL
    ) -> bool:
        """کلیک روی تصویر با استفاده از Vision system.
        
        این یک operation هوشمند است که از template matching استفاده می‌کند.
        
        Args:
            image_path: مسیر تصویر template
            confidence: آستانه اطمینان (0.0-1.0)
            button: دکمه موس
            pattern: الگوی کلیک
        
        Returns:
            True اگر موفق باشد
        
        Example:
            >>> mouse.click_on_image("button_ok.png")
            >>> mouse.click_on_image("icon.png", confidence=0.9)
        
        Raises:
            ValueError: اگر Vision system تنظیم نشده باشد
            RuntimeError: اگر تصویر پیدا نشود
        """
        if self.vision_system is None:
            raise ValueError("Vision system not configured.")
        
        logger.info("Looking for image: %s", image_path)
        
        # جستجوی تصویر
        box = self.vision_system.find_image(image_path, confidence=confidence)
        
        if box is None:
            raise RuntimeError(f"Image not found: {image_path}")
        
        cx, cy = box.center
        logger.info("Found image at (%d, %d)", cx, cy)
        
        # کلیک انسانی
        return self.click_human(cx, cy, button=button, pattern=pattern)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Utility & Stats
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _log_action(self, action: MouseAction):
        """ثبت اقدام در history."""
        self.action_history.append(action)
        
        # محدود کردن سایز history
        if len(self.action_history) > self.max_history:
            self.action_history = self.action_history[-self.max_history:]
    
    def get_stats(self) -> dict:
        """دریافت آمار استفاده.
        
        Returns:
            دیکشنری آمار
        """
        total_actions = sum([
            self.stats['total_clicks'],
            self.stats['total_moves'],
            self.stats['total_drags'],
            self.stats['total_scrolls'],
        ])
        
        success_rate = 0.0
        if total_actions > 0:
            success_rate = ((total_actions - self.stats['failed_actions']) / total_actions) * 100
        
        return {
            **self.stats,
            'total_actions': total_actions,
            'success_rate': f"{success_rate:.2f}%",
            'recent_actions': len(self.action_history),
        }
    
    def reset_stats(self):
        """بازنشانی آمار."""
        self.stats = {
            'total_clicks': 0,
            'total_moves': 0,
            'total_drags': 0,
            'total_scrolls': 0,
            'failed_actions': 0,
        }
        self.action_history.clear()
        logger.info("Stats reset")
