# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""اقدامات هوشمند بر اساس Context (Context-Aware Actions).

این ماژول اقدامات را بر اساس شرایط و محیط سیستم هوشمندانه تنظیم می‌کند:
- تشخیص پنجره فعال
- تطبیق اقدامات با برنامه جاری
- تشخیص وضعیت سیستم (idle, busy, gaming, etc.)
- تصمیم‌گیری هوشمند بر اساس زمینه
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import psutil
import pyautogui
import win32gui
import win32process

logger = logging.getLogger(__name__)


class SystemState(Enum):
    """وضعیت سیستم.
    
    - IDLE: بیکار (استفاده کم از CPU/RAM)
    - BUSY: مشغول (استفاده زیاد از CPU/RAM)
    - GAMING: در حال بازی
    - WORKING: در حال کار
    - LOCKED: قفل شده
    - UNKNOWN: نامشخص
    """
    IDLE = "idle"
    BUSY = "busy"
    GAMING = "gaming"
    WORKING = "working"
    LOCKED = "locked"
    UNKNOWN = "unknown"


class ApplicationCategory(Enum):
    """دسته‌بندی برنامه‌ها.
    
    - BROWSER: مرورگر
    - EDITOR: ویرایشگر کد/متن
    - OFFICE: برنامه‌های اداری
    - MEDIA: پخش‌کننده رسانه
    - GAME: بازی
    - SYSTEM: برنامه سیستمی
    - COMMUNICATION: ارتباطات (چت، ایمیل)
    - DEVELOPMENT: توسعه نرم‌افزار
    - DESIGN: طراحی گرافیکی
    - OTHER: سایر
    """
    BROWSER = "browser"
    EDITOR = "editor"
    OFFICE = "office"
    MEDIA = "media"
    GAME = "game"
    SYSTEM = "system"
    COMMUNICATION = "communication"
    DEVELOPMENT = "development"
    DESIGN = "design"
    OTHER = "other"


@dataclass
class ContextInfo:
    """اطلاعات Context سیستم.
    
    Attributes:
        active_window: عنوان پنجره فعال
        active_process: نام فرآیند فعال
        app_category: دسته برنامه فعال
        system_state: وضعیت سیستم
        cpu_usage: درصد استفاده از CPU
        ram_usage: درصد استفاده از RAM
        is_fullscreen: پنجره تمام‌صفحه است یا خیر
        mouse_position: موقعیت فعلی موس
        timestamp: زمان دریافت اطلاعات
    """
    active_window: str
    active_process: str
    app_category: ApplicationCategory
    system_state: SystemState
    cpu_usage: float
    ram_usage: float
    is_fullscreen: bool
    mouse_position: tuple[int, int]
    timestamp: float


class ContextAwareActions:
    """سیستم اقدامات هوشمند بر اساس Context.
    
    این کلاس اقدامات را بر اساس شرایط سیستم تنظیم می‌کند:
    - در حالت بازی، اقدامات مزاحم را به تعویق می‌اندازد
    - در حالت کار، اولویت اقدامات را تنظیم می‌کند
    - در حالت Idle، اقدامات سنگین را اجرا می‌کند
    
    Example:
        >>> context = ContextAwareActions()
        >>> info = await context.get_current_context()
        >>> print(f"Active: {info.active_window}")
        >>> print(f"State: {info.system_state.value}")
        >>> 
        >>> # بررسی اینکه آیا می‌توان اقدام را اجرا کرد
        >>> can_execute = context.should_execute_action(
        ...     {"type": "LaunchApp", "priority": "low"},
        ...     info
        ... )
    """
    
    def __init__(self):
        """مقداردهی اولیه سیستم Context-Aware."""
        self._last_context: Optional[ContextInfo] = None
        self._context_cache_duration = 1.0  # ثانیه
        
        # دسته‌بندی برنامه‌ها
        self._app_categories = {
            # مرورگرها
            "chrome.exe": ApplicationCategory.BROWSER,
            "firefox.exe": ApplicationCategory.BROWSER,
            "msedge.exe": ApplicationCategory.BROWSER,
            "opera.exe": ApplicationCategory.BROWSER,
            "brave.exe": ApplicationCategory.BROWSER,
            
            # ویرایشگرها
            "code.exe": ApplicationCategory.EDITOR,
            "notepad++.exe": ApplicationCategory.EDITOR,
            "sublime_text.exe": ApplicationCategory.EDITOR,
            "atom.exe": ApplicationCategory.EDITOR,
            "vim.exe": ApplicationCategory.EDITOR,
            
            # برنامه‌های اداری
            "winword.exe": ApplicationCategory.OFFICE,
            "excel.exe": ApplicationCategory.OFFICE,
            "powerpnt.exe": ApplicationCategory.OFFICE,
            "outlook.exe": ApplicationCategory.OFFICE,
            
            # پخش‌کننده رسانه
            "vlc.exe": ApplicationCategory.MEDIA,
            "spotify.exe": ApplicationCategory.MEDIA,
            "wmplayer.exe": ApplicationCategory.MEDIA,
            
            # بازی‌ها
            "steam.exe": ApplicationCategory.GAME,
            "epicgameslauncher.exe": ApplicationCategory.GAME,
            
            # ارتباطات
            "discord.exe": ApplicationCategory.COMMUNICATION,
            "slack.exe": ApplicationCategory.COMMUNICATION,
            "teams.exe": ApplicationCategory.COMMUNICATION,
            "telegram.exe": ApplicationCategory.COMMUNICATION,
            "skype.exe": ApplicationCategory.COMMUNICATION,
            
            # توسعه
            "pycharm64.exe": ApplicationCategory.DEVELOPMENT,
            "devenv.exe": ApplicationCategory.DEVELOPMENT,  # Visual Studio
            "idea64.exe": ApplicationCategory.DEVELOPMENT,  # IntelliJ
            
            # طراحی
            "photoshop.exe": ApplicationCategory.DESIGN,
            "illustrator.exe": ApplicationCategory.DESIGN,
            "figma.exe": ApplicationCategory.DESIGN,
        }
    
    async def get_current_context(self, use_cache: bool = True) -> ContextInfo:
        """دریافت Context فعلی سیستم.
        
        Args:
            use_cache: استفاده از cache (اگر تازه است)
        
        Returns:
            ContextInfo: اطلاعات Context
        
        Example:
            >>> context = ContextAwareActions()
            >>> info = await context.get_current_context()
            >>> print(f"Active window: {info.active_window}")
            >>> print(f"CPU: {info.cpu_usage}%")
        """
        # بررسی cache
        if use_cache and self._last_context:
            age = time.time() - self._last_context.timestamp
            if age < self._context_cache_duration:
                logger.debug("Using cached context")
                return self._last_context
        
        # دریافت اطلاعات جدید
        try:
            # پنجره فعال
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            
            # فرآیند فعال
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except:
                process_name = "unknown"
            
            # دسته برنامه
            app_category = self._app_categories.get(
                process_name.lower(),
                ApplicationCategory.OTHER
            )
            
            # وضعیت سیستم
            cpu_usage = psutil.cpu_percent(interval=0.1)
            ram_usage = psutil.virtual_memory().percent
            system_state = self._determine_system_state(
                cpu_usage,
                ram_usage,
                app_category
            )
            
            # تمام‌صفحه بودن
            is_fullscreen = self._is_fullscreen_window(hwnd)
            
            # موقعیت موس
            mouse_x, mouse_y = pyautogui.position()
            
            # ساخت Context
            context = ContextInfo(
                active_window=window_title,
                active_process=process_name,
                app_category=app_category,
                system_state=system_state,
                cpu_usage=cpu_usage,
                ram_usage=ram_usage,
                is_fullscreen=is_fullscreen,
                mouse_position=(mouse_x, mouse_y),
                timestamp=time.time(),
            )
            
            self._last_context = context
            logger.debug(
                f"Context: {process_name} ({app_category.value}), "
                f"State: {system_state.value}, CPU: {cpu_usage:.1f}%"
            )
            
            return context
        
        except Exception as e:
            logger.error(f"❌ Failed to get context: {e}")
            # fallback
            return ContextInfo(
                active_window="Unknown",
                active_process="unknown",
                app_category=ApplicationCategory.OTHER,
                system_state=SystemState.UNKNOWN,
                cpu_usage=0.0,
                ram_usage=0.0,
                is_fullscreen=False,
                mouse_position=(0, 0),
                timestamp=time.time(),
            )
    
    def _determine_system_state(
        self,
        cpu_usage: float,
        ram_usage: float,
        app_category: ApplicationCategory
    ) -> SystemState:
        """تشخیص وضعیت سیستم.
        
        Args:
            cpu_usage: درصد استفاده از CPU
            ram_usage: درصد استفاده از RAM
            app_category: دسته برنامه فعال
        
        Returns:
            SystemState: وضعیت سیستم
        """
        # بازی
        if app_category == ApplicationCategory.GAME:
            return SystemState.GAMING
        
        # کار
        if app_category in [
            ApplicationCategory.EDITOR,
            ApplicationCategory.DEVELOPMENT,
            ApplicationCategory.OFFICE
        ]:
            return SystemState.WORKING
        
        # مشغول (CPU/RAM بالا)
        if cpu_usage > 70 or ram_usage > 80:
            return SystemState.BUSY
        
        # بیکار
        if cpu_usage < 20 and ram_usage < 50:
            return SystemState.IDLE
        
        return SystemState.UNKNOWN
    
    def _is_fullscreen_window(self, hwnd: int) -> bool:
        """بررسی تمام‌صفحه بودن پنجره.
        
        Args:
            hwnd: handle پنجره
        
        Returns:
            bool: True اگر تمام‌صفحه باشد
        """
        try:
            import win32api
            
            # اندازه صفحه
            screen_width = win32api.GetSystemMetrics(0)
            screen_height = win32api.GetSystemMetrics(1)
            
            # اندازه پنجره
            rect = win32gui.GetWindowRect(hwnd)
            window_width = rect[2] - rect[0]
            window_height = rect[3] - rect[1]
            
            # بررسی تمام‌صفحه
            return (
                window_width >= screen_width and
                window_height >= screen_height
            )
        
        except:
            return False
    
    def should_execute_action(
        self,
        action: dict[str, Any],
        context: Optional[ContextInfo] = None
    ) -> tuple[bool, str]:
        """بررسی اینکه آیا اقدام باید اجرا شود یا خیر.
        
        Args:
            action: اقدام مورد نظر
            context: Context فعلی (در صورت عدم ارائه، خودکار دریافت می‌شود)
        
        Returns:
            (should_execute, reason): 
                - should_execute: True اگر باید اجرا شود
                - reason: دلیل عدم اجرا (در صورت وجود)
        
        Example:
            >>> context = ContextAwareActions()
            >>> info = await context.get_current_context()
            >>> should_execute, reason = context.should_execute_action(
            ...     {"type": "LaunchApp", "priority": "low"},
            ...     info
            ... )
        """
        if not context:
            # دریافت Context (به صورت همزمان)
            import asyncio
            try:
                context = asyncio.run(self.get_current_context())
            except:
                # اگر نتوانستیم Context بگیریم، اجرا می‌کنیم
                return True, ""
        
        priority = action.get("priority", "normal")
        action_type = action.get("type", "")
        
        # بازی: فقط اقدامات با اولویت بالا
        if context.system_state == SystemState.GAMING:
            if priority not in ["high", "critical"]:
                return False, "System is in gaming mode, only high/critical priority allowed"
        
        # تمام‌صفحه: فقط اقدامات بدون تداخل
        if context.is_fullscreen:
            non_intrusive = ["QueryHardware", "GetSystemInfo"]
            if action_type not in non_intrusive:
                return False, "Fullscreen window active, avoiding intrusive actions"
        
        # مشغول: اولویت پایین به تعویق می‌افتد
        if context.system_state == SystemState.BUSY:
            if priority == "low":
                return False, "System is busy, low priority actions delayed"
        
        # همه چیز OK
        return True, ""
    
    def adjust_action_timing(
        self,
        action: dict[str, Any],
        context: Optional[ContextInfo] = None
    ) -> dict[str, Any]:
        """تنظیم زمان‌بندی اقدام بر اساس Context.
        
        Args:
            action: اقدام مورد نظر
            context: Context فعلی
        
        Returns:
            dict: اقدام با timing تنظیم شده
        
        Example:
            >>> # در حالت Gaming، click سریع‌تر می‌شود
            >>> adjusted = context.adjust_action_timing(
            ...     {"type": "DesktopClick", "params": {"interval": 0.5}},
            ...     info
            ... )
        """
        if not context:
            return action
        
        adjusted = action.copy()
        params = adjusted.get("params", {}).copy()
        
        # تنظیم interval بر اساس وضعیت
        if "interval" in params:
            original_interval = params["interval"]
            
            if context.system_state == SystemState.GAMING:
                # بازی: سریع‌تر
                params["interval"] = original_interval * 0.5
            
            elif context.system_state == SystemState.BUSY:
                # مشغول: کندتر
                params["interval"] = original_interval * 1.5
            
            elif context.system_state == SystemState.IDLE:
                # بیکار: عادی
                params["interval"] = original_interval
        
        # تنظیم timeout
        if "timeout" in params:
            original_timeout = params["timeout"]
            
            if context.system_state == SystemState.BUSY:
                # مشغول: timeout بیشتر
                params["timeout"] = original_timeout * 2
        
        adjusted["params"] = params
        return adjusted
    
    async def wait_for_appropriate_time(
        self,
        action: dict[str, Any],
        max_wait: float = 30.0
    ) -> bool:
        """انتظار برای زمان مناسب اجرای اقدام.
        
        Args:
            action: اقدام مورد نظر
            max_wait: حداکثر زمان انتظار (ثانیه)
        
        Returns:
            bool: True اگر زمان مناسب پیدا شد
        
        Example:
            >>> # منتظر می‌ماند تا سیستم Idle شود
            >>> success = await context.wait_for_appropriate_time(
            ...     {"type": "InstallPackage", "priority": "low"}
            ... )
        """
        start_time = time.time()
        
        while True:
            context = await self.get_current_context(use_cache=False)
            should_execute, reason = self.should_execute_action(action, context)
            
            if should_execute:
                logger.info("✅ Appropriate time found for action execution")
                return True
            
            # بررسی timeout
            elapsed = time.time() - start_time
            if elapsed > max_wait:
                logger.warning(f"⏱️ Timeout waiting for appropriate time ({max_wait}s)")
                return False
            
            # انتظار قبل از بررسی مجدد
            await asyncio.sleep(1.0)
