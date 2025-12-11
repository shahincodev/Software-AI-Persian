# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""پشتیبانی از چند مانیتور (Multi-Monitor Support).

این ماژول امکان کار با چند مانیتور را فراهم می‌کند:
- شناسایی تمام مانیتورها
- تبدیل مختصات بین مانیتورها
- جستجو و کلیک در مانیتور مشخص
- مدیریت هوشمند پنجره‌ها روی مانیتورهای مختلف
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, Any
import pyautogui
import screeninfo

logger = logging.getLogger(__name__)


@dataclass
class MonitorInfo:
    """اطلاعات یک مانیتور.
    
    Attributes:
        index: شماره مانیتور (0-based)
        name: نام مانیتور
        x: موقعیت X (گوشه چپ-بالا)
        y: موقعیت Y (گوشه چپ-بالا)
        width: عرض مانیتور (پیکسل)
        height: ارتفاع مانیتور (پیکسل)
        is_primary: اینکه مانیتور اصلی است یا خیر
    """
    index: int
    name: str
    x: int
    y: int
    width: int
    height: int
    is_primary: bool
    
    @property
    def center(self) -> tuple[int, int]:
        """مرکز مانیتور.
        
        Returns:
            (center_x, center_y)
        """
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def bounds(self) -> tuple[int, int, int, int]:
        """محدوده مانیتور.
        
        Returns:
            (x, y, width, height)
        """
        return (self.x, self.y, self.width, self.height)
    
    def contains_point(self, x: int, y: int) -> bool:
        """بررسی اینکه نقطه داخل این مانیتور است یا خیر.
        
        Args:
            x: موقعیت X
            y: موقعیت Y
        
        Returns:
            bool: True اگر نقطه داخل مانیتور باشد
        """
        return (
            self.x <= x < self.x + self.width and
            self.y <= y < self.y + self.height
        )


class MultiMonitor:
    """مدیریت چند مانیتور.
    
    این کلاس امکانات زیر را فراهم می‌کند:
    - شناسایی تمام مانیتورها
    - تبدیل مختصات بین مانیتورها
    - جستجوی عنصر در مانیتور خاص
    - کلیک و کنترل موس در مانیتورهای مختلف
    
    Example:
        >>> multi_mon = MultiMonitor()
        >>> monitors = multi_mon.get_monitors()
        >>> print(f"Found {len(monitors)} monitors")
        >>> 
        >>> # کلیک در مانیتور دوم
        >>> monitor = monitors[1]
        >>> multi_mon.click_on_monitor(monitor.index, 100, 100)
    """
    
    def __init__(self):
        """مقداردهی اولیه سیستم چند مانیتور."""
        self._monitors: list[MonitorInfo] = []
        self._detect_monitors()
    
    def _detect_monitors(self) -> None:
        """شناسایی تمام مانیتورها."""
        try:
            screens = screeninfo.get_monitors()
            self._monitors = []
            
            for i, screen in enumerate(screens):
                monitor = MonitorInfo(
                    index=i,
                    name=screen.name or f"Monitor {i}",
                    x=screen.x,
                    y=screen.y,
                    width=screen.width,
                    height=screen.height,
                    is_primary=(screen.is_primary if hasattr(screen, 'is_primary') else (i == 0)) or False,
                )
                self._monitors.append(monitor)
                
                logger.info(
                    f"🖥️ Monitor {i}: {monitor.name} "
                    f"({monitor.width}x{monitor.height}) at ({monitor.x}, {monitor.y}) "
                    f"{'[PRIMARY]' if monitor.is_primary else ''}"
                )
            
            if not self._monitors:
                # fallback: اگر screeninfo کار نکرد، از pyautogui استفاده می‌کنیم
                width, height = pyautogui.size()
                self._monitors = [
                    MonitorInfo(
                        index=0,
                        name="Primary",
                        x=0,
                        y=0,
                        width=width,
                        height=height,
                        is_primary=True,
                    )
                ]
                logger.warning("⚠️ Could not detect monitors, using primary only")
        
        except Exception as e:
            logger.error(f"❌ Failed to detect monitors: {e}")
            # fallback
            width, height = pyautogui.size()
            self._monitors = [
                MonitorInfo(
                    index=0,
                    name="Primary",
                    x=0,
                    y=0,
                    width=width,
                    height=height,
                    is_primary=True,
                )
            ]
    
    def get_monitors(self) -> list[MonitorInfo]:
        """دریافت لیست تمام مانیتورها.
        
        Returns:
            list[MonitorInfo]: لیست مانیتورها
        
        Example:
            >>> multi_mon = MultiMonitor()
            >>> for monitor in multi_mon.get_monitors():
            ...     print(f"{monitor.name}: {monitor.width}x{monitor.height}")
        """
        return self._monitors.copy()
    
    def get_monitor_count(self) -> int:
        """تعداد مانیتورها.
        
        Returns:
            int: تعداد مانیتورها
        """
        return len(self._monitors)
    
    def get_primary_monitor(self) -> MonitorInfo:
        """دریافت مانیتور اصلی.
        
        Returns:
            MonitorInfo: مانیتور اصلی
        """
        for monitor in self._monitors:
            if monitor.is_primary:
                return monitor
        # fallback: اولین مانیتور
        return self._monitors[0]
    
    def get_monitor_by_index(self, index: int) -> Optional[MonitorInfo]:
        """دریافت مانیتور با شماره مشخص.
        
        Args:
            index: شماره مانیتور (0-based)
        
        Returns:
            MonitorInfo یا None
        
        Example:
            >>> monitor = multi_mon.get_monitor_by_index(1)
            >>> if monitor:
            ...     print(f"Monitor 1: {monitor.width}x{monitor.height}")
        """
        if 0 <= index < len(self._monitors):
            return self._monitors[index]
        logger.warning(f"⚠️ Monitor index {index} not found")
        return None
    
    def get_monitor_at_point(self, x: int, y: int) -> Optional[MonitorInfo]:
        """پیدا کردن مانیتوری که نقطه مشخص در آن قرار دارد.
        
        Args:
            x: موقعیت X
            y: موقعیت Y
        
        Returns:
            MonitorInfo یا None
        
        Example:
            >>> x, y = pyautogui.position()
            >>> monitor = multi_mon.get_monitor_at_point(x, y)
            >>> print(f"Mouse is on: {monitor.name}")
        """
        for monitor in self._monitors:
            if monitor.contains_point(x, y):
                return monitor
        logger.warning(f"⚠️ No monitor found at ({x}, {y})")
        return None
    
    def convert_to_monitor(
        self,
        x: int,
        y: int,
        from_monitor: int,
        to_monitor: int
    ) -> tuple[int, int]:
        """تبدیل مختصات از یک مانیتور به مانیتور دیگر.
        
        Args:
            x: موقعیت X در مانیتور مبدأ
            y: موقعیت Y در مانیتور مبدأ
            from_monitor: شماره مانیتور مبدأ
            to_monitor: شماره مانیتور مقصد
        
        Returns:
            (new_x, new_y): مختصات در مانیتور مقصد
        
        Example:
            >>> # تبدیل (100, 100) از مانیتور 0 به مانیتور 1
            >>> new_x, new_y = multi_mon.convert_to_monitor(100, 100, 0, 1)
        """
        mon_from = self.get_monitor_by_index(from_monitor)
        mon_to = self.get_monitor_by_index(to_monitor)
        
        if not mon_from or not mon_to:
            logger.error("❌ Invalid monitor indices")
            return x, y
        
        # محاسبه موقعیت نسبی در مانیتور مبدأ
        rel_x = (x - mon_from.x) / mon_from.width
        rel_y = (y - mon_from.y) / mon_from.height
        
        # تبدیل به موقعیت مطلق در مانیتور مقصد
        new_x = mon_to.x + int(rel_x * mon_to.width)
        new_y = mon_to.y + int(rel_y * mon_to.height)
        
        return new_x, new_y
    
    def click_on_monitor(
        self,
        monitor_index: int,
        x: int,
        y: int,
        button: str = "left",
        clicks: int = 1
    ) -> bool:
        """کلیک در موقعیت مشخص در مانیتور مشخص.
        
        Args:
            monitor_index: شماره مانیتور
            x: موقعیت X نسبی در مانیتور (0 تا width)
            y: موقعیت Y نسبی در مانیتور (0 تا height)
            button: دکمه موس ("left", "right", "middle")
            clicks: تعداد کلیک
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        
        Example:
            >>> # کلیک در مرکز مانیتور 1
            >>> monitor = multi_mon.get_monitor_by_index(1)
            >>> multi_mon.click_on_monitor(1, monitor.width // 2, monitor.height // 2)
        """
        monitor = self.get_monitor_by_index(monitor_index)
        if not monitor:
            logger.error(f"❌ Monitor {monitor_index} not found")
            return False
        
        # تبدیل به مختصات مطلق
        abs_x = monitor.x + x
        abs_y = monitor.y + y
        
        # بررسی محدوده
        if not monitor.contains_point(abs_x, abs_y):
            logger.warning(f"⚠️ Point ({x}, {y}) is outside monitor {monitor_index}")
            return False
        
        try:
            pyautogui.click(abs_x, abs_y, button=button, clicks=clicks)
            logger.debug(f"✅ Clicked on monitor {monitor_index} at ({x}, {y})")
            return True
        
        except Exception as e:
            logger.error(f"❌ Click failed: {e}")
            return False
    
    def move_to_monitor(
        self,
        monitor_index: int,
        x: int,
        y: int,
        duration: float = 0.0
    ) -> bool:
        """انتقال موس به موقعیت مشخص در مانیتور مشخص.
        
        Args:
            monitor_index: شماره مانیتور
            x: موقعیت X نسبی در مانیتور
            y: موقعیت Y نسبی در مانیتور
            duration: مدت زمان حرکت (ثانیه)
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        
        Example:
            >>> # انتقال موس به مرکز مانیتور 2
            >>> monitor = multi_mon.get_monitor_by_index(2)
            >>> multi_mon.move_to_monitor(2, monitor.width // 2, monitor.height // 2)
        """
        monitor = self.get_monitor_by_index(monitor_index)
        if not monitor:
            logger.error(f"❌ Monitor {monitor_index} not found")
            return False
        
        # تبدیل به مختصات مطلق
        abs_x = monitor.x + x
        abs_y = monitor.y + y
        
        # بررسی محدوده
        if not monitor.contains_point(abs_x, abs_y):
            logger.warning(f"⚠️ Point ({x}, {y}) is outside monitor {monitor_index}")
            return False
        
        try:
            pyautogui.moveTo(abs_x, abs_y, duration=duration)
            logger.debug(f"✅ Moved to monitor {monitor_index} at ({x}, {y})")
            return True
        
        except Exception as e:
            logger.error(f"❌ Move failed: {e}")
            return False
    
    def get_current_monitor(self) -> Optional[MonitorInfo]:
        """پیدا کردن مانیتوری که موس در آن قرار دارد.
        
        Returns:
            MonitorInfo یا None
        
        Example:
            >>> current = multi_mon.get_current_monitor()
            >>> print(f"Mouse is on: {current.name}")
        """
        x, y = pyautogui.position()
        return self.get_monitor_at_point(x, y)
    
    def get_total_screen_size(self) -> tuple[int, int]:
        """محاسبه اندازه کل فضای صفحه (همه مانیتورها).
        
        Returns:
            (total_width, total_height)
        
        Example:
            >>> width, height = multi_mon.get_total_screen_size()
            >>> print(f"Total screen: {width}x{height}")
        """
        if not self._monitors:
            return pyautogui.size()
        
        min_x = min(m.x for m in self._monitors)
        max_x = max(m.x + m.width for m in self._monitors)
        min_y = min(m.y for m in self._monitors)
        max_y = max(m.y + m.height for m in self._monitors)
        
        total_width = max_x - min_x
        total_height = max_y - min_y
        
        return total_width, total_height
    
    def get_monitor_layout(self) -> dict[str, Any]:
        """دریافت اطلاعات کامل چیدمان مانیتورها.
        
        Returns:
            dict: اطلاعات کامل
                - count: تعداد مانیتورها
                - primary: شماره مانیتور اصلی
                - monitors: لیست اطلاعات مانیتورها
                - total_size: اندازه کل
        
        Example:
            >>> layout = multi_mon.get_monitor_layout()
            >>> print(f"Monitors: {layout['count']}")
            >>> print(f"Primary: {layout['primary']}")
        """
        primary_index = 0
        for i, monitor in enumerate(self._monitors):
            if monitor.is_primary:
                primary_index = i
                break
        
        total_width, total_height = self.get_total_screen_size()
        
        return {
            "count": len(self._monitors),
            "primary": primary_index,
            "monitors": [
                {
                    "index": m.index,
                    "name": m.name,
                    "x": m.x,
                    "y": m.y,
                    "width": m.width,
                    "height": m.height,
                    "is_primary": m.is_primary,
                }
                for m in self._monitors
            ],
            "total_size": {
                "width": total_width,
                "height": total_height,
            },
        }
