# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Capability Manager - مدیریت دینامیکی قابلیت‌های سیستم

این ماژول قابلیت‌های سیستم (browser_use، desktop_automation، autonomous_agent، task_mode)
را مدیریت می‌کند. این امکان فعال‌سازی/غیرفعال‌سازی پویا قابلیت‌ها را فراهم می‌کند
بر اساس درخواست کاربر یا تغییر حالت.

مثال:
    >>> manager = CapabilityManager()
    >>> await manager.enable("browser_use")
    >>> status = manager.get_status()
    >>> print(status["browser_use"]["enabled"])  # True
    >>> await manager.disable("desktop_automation")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class CapabilityType(Enum):
    """انواع قابلیت‌های سیستم"""
    BROWSER_USE = "browser_use"
    DESKTOP_AUTOMATION = "desktop_automation"
    AUTONOMOUS_AGENT = "autonomous_agent"
    TASK_MODE = "task_mode"


@dataclass
class CapabilityInfo:
    """اطلاعات یک قابلیت
    
    Attributes:
        name: نام قابلیت
        enabled: آیا فعال است
        risk_level: سطح ریسک (safe/medium/high)
        dependencies: قابلیت‌های وابسته
        initialization_error: خطای آخر فعال‌سازی (اگر وجود دارد)
        last_used: زمان آخر استفاده
    """
    name: str
    enabled: bool = False
    risk_level: str = "safe"
    dependencies: List[str] = field(default_factory=list)
    initialization_error: Optional[str] = None
    last_used: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CapabilityManager:
    """مدیریت‌کننده قابلیت‌های سیستم
    
    این کلاس:
    1. ثبت قابلیت‌های موجود
    2. فعال‌سازی/غیرفعال‌سازی پویا
    3. بررسی وابستگی‌ها
    4. ثبت وضعیت و خطاها
    5. اعلان تغییرات
    """
    
    def __init__(self):
        """مقداردهی Capability Manager"""
        self._capabilities: Dict[str, CapabilityInfo] = {}
        self._enabled_callbacks: Dict[str, List[callable]] = {}
        self._disabled_callbacks: Dict[str, List[callable]] = {}
        self._initialized = False
        logger.info("CapabilityManager initialized")
    
    def register(
        self,
        name: str,
        risk_level: str = "safe",
        dependencies: Optional[List[str]] = None
    ) -> None:
        """ثبت یک قابلیت جدید
        
        Args:
            name: نام قابلیت
            risk_level: سطح ریسک (safe/medium/high)
            dependencies: لیست قابلیت‌های وابسته
        """
        if name in self._capabilities:
            logger.warning(f"Capability {name} already registered")
            return
        
        self._capabilities[name] = CapabilityInfo(
            name=name,
            risk_level=risk_level,
            dependencies=dependencies or []
        )
        self._enabled_callbacks[name] = []
        self._disabled_callbacks[name] = []
        logger.debug(f"Registered capability: {name} (risk={risk_level})")
    
    async def enable(
        self,
        name: str,
        initializer: Optional[callable] = None
    ) -> bool:
        """فعال‌سازی یک قابلیت
        
        Args:
            name: نام قابلیت
            initializer: تابع اولیه‌سازی (async callable)
        
        Returns:
            bool: True اگر موفق
        """
        if name not in self._capabilities:
            logger.warning(f"Unknown capability: {name}")
            return False
        
        cap = self._capabilities[name]
        
        if cap.enabled:
            logger.debug(f"Capability {name} already enabled")
            return True
        
        try:
            # فعال‌سازی وابستگی‌ها
            for dep in cap.dependencies:
                if not self._capabilities.get(dep, CapabilityInfo(dep)).enabled:
                    await self.enable(dep)
            
            # اولیه‌سازی
            if initializer:
                await initializer()
            
            cap.enabled = True
            cap.initialization_error = None
            logger.info(f"✅ Enabled capability: {name}")
            
            # فراخوانی callback‌های فعال‌سازی
            for callback in self._enabled_callbacks[name]:
                try:
                    await callback() if callable(callback) and hasattr(callback, '__await__') else callback()
                except Exception as e:
                    logger.warning(f"Callback error for {name}: {e}")
            
            return True
            
        except Exception as e:
            cap.enabled = False
            cap.initialization_error = str(e)
            logger.error(f"❌ Failed to enable {name}: {e}", exc_info=True)
            return False
    
    async def disable(self, name: str) -> bool:
        """غیرفعال‌سازی یک قابلیت
        
        Args:
            name: نام قابلیت
        
        Returns:
            bool: True اگر موفق
        """
        if name not in self._capabilities:
            logger.warning(f"Unknown capability: {name}")
            return False
        
        cap = self._capabilities[name]
        
        if not cap.enabled:
            logger.debug(f"Capability {name} already disabled")
            return True
        
        try:
            cap.enabled = False
            logger.info(f"Disabled capability: {name}")
            
            # فراخوانی callback‌های غیرفعال‌سازی
            for callback in self._disabled_callbacks[name]:
                try:
                    await callback() if callable(callback) and hasattr(callback, '__await__') else callback()
                except Exception as e:
                    logger.warning(f"Callback error for {name}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable {name}: {e}")
            return False
    
    def is_enabled(self, name: str) -> bool:
        """بررسی فعال بودن یک قابلیت
        
        Args:
            name: نام قابلیت
        
        Returns:
            bool: True اگر فعال است
        """
        cap = self._capabilities.get(name)
        return cap.enabled if cap else False
    
    def get_status(self) -> Dict[str, Dict[str, Any]]:
        """دریافت وضعیت تمام قابلیت‌ها
        
        Returns:
            dict: وضعیت هر قابلیت
        """
        return {
            name: {
                "enabled": cap.enabled,
                "risk_level": cap.risk_level,
                "dependencies": cap.dependencies,
                "initialization_error": cap.initialization_error,
                "last_used": cap.last_used
            }
            for name, cap in self._capabilities.items()
        }
    
    def get_enabled(self) -> List[str]:
        """دریافت لیست قابلیت‌های فعال
        
        Returns:
            list: نام‌های قابلیت‌های فعال
        """
        return [name for name, cap in self._capabilities.items() if cap.enabled]
    
    def on_enabled(self, name: str, callback: callable) -> None:
        """ثبت callback برای وقتی قابلیت فعال شود
        
        Args:
            name: نام قابلیت
            callback: تابع (async یا sync)
        """
        if name in self._enabled_callbacks:
            self._enabled_callbacks[name].append(callback)
    
    def on_disabled(self, name: str, callback: callable) -> None:
        """ثبت callback برای وقتی قابلیت غیرفعال شود
        
        Args:
            name: نام قابلیت
            callback: تابع (async یا sync)
        """
        if name in self._disabled_callbacks:
            self._disabled_callbacks[name].append(callback)
    
    async def cleanup(self) -> None:
        """تمیز‌کاری: غیرفعال‌سازی تمام قابلیت‌ها
        
        این تابع برای شات‌داون نظیف است.
        """
        logger.info("Cleaning up capabilities...")
        for name in list(self._capabilities.keys()):
            if self._capabilities[name].enabled:
                await self.disable(name)
        logger.info("Cleanup complete")
    
    def __repr__(self) -> str:
        """نمایش مدیریت‌کننده"""
        enabled = self.get_enabled()
        return f"CapabilityManager(enabled={enabled})"
