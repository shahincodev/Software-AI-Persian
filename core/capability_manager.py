# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Capability Manager - مدیریت پویای قابلیت‌های سیستم با فعال‌سازی تنبل

این ماژول بعنوان هسته مرکزی معماری capability-driven عمل می‌کند:
- ثبت قابلیت‌ها با factory function (ایجاد تنبل)
- فعال‌سازی خودکار وابستگی‌ها
- مدیریت چرخه حیات resources
- یکپارچه‌سازی با IntentRouter برای مسیریابی هوشمند

مثال:
    >>> manager = CapabilityManager()
    >>> manager.register("ai", factory=lambda: AIBrain())
    >>> manager.register("desktop", factory=lambda: DesktopVision(), 
    ...                  dependencies=["ai"])
    >>> 
    >>> # فعال‌سازی تنبل — resource فقط در زمان نیاز ساخته می‌شود
    >>> vision = await manager.activate("desktop")
    >>> # بازیابی resource فعال‌شده
    >>> same_vision = manager.get("desktop")
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class CapabilityType(Enum):
    """انواع قابلیت‌های سیستم"""
    BROWSER_USE = "browser_use"
    DESKTOP_AUTOMATION = "desktop_automation"
    AUTONOMOUS_AGENT = "autonomous_agent"
    TASK_MODE = "task_mode"
    DESKTOP_MOUSE = "desktop_mouse"
    DESKTOP_KEYBOARD = "desktop_keyboard"
    SCREEN_OBSERVATION = "screen_observation"
    SYSTEM_OPERATIONS = "system_operations"
    VOICE_IO = "voice_io"
    INTENT_ANALYSIS = "intent_analysis"
    PLANNING = "planning"
    PLAN_VALIDATION = "plan_validation"
    EXECUTION_HISTORY = "execution_history"
    CHAT = "chat"
    WEB_BROWSING = "web_browsing"


@dataclass
class CapabilityInfo:
    """اطلاعات یک قابلیت
    
    Attributes:
        name: نام قابلیت
        enabled: آیا فعال است (برای backward compatibility)
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


# Type alias for capability factory
CapabilityFactory = Callable[[], Any]


class CapabilityManager:
    """مدیریت‌کننده قابلیت‌های سیستم با فعال‌سازی تنبل.
    
    دو لایه مجزا:
    1. ثبت (registration) — قابلیت‌ها با factory function ثبت می‌شوند
    2. فعال‌سازی (activation) — resource فقط در اولین درخواست ساخته می‌شود
    
    backward compatibility با متدهای enable/disable حفظ شده است.
    """
    
    def __init__(self):
        """مقداردهی Capability Manager"""
        self._capabilities: Dict[str, CapabilityInfo] = {}
        self._factories: Dict[str, CapabilityFactory] = {}
        self._resources: Dict[str, Any] = {}
        self._enabled_callbacks: Dict[str, List[callable]] = {}
        self._disabled_callbacks: Dict[str, List[callable]] = {}
        self._initialized = False
        logger.info("CapabilityManager initialized")
    
    def register(
        self,
        name: str,
        factory: Optional[CapabilityFactory] = None,
        risk_level: str = "safe",
        dependencies: Optional[List[str]] = None,
    ) -> None:
        """ثبت یک قابلیت جدید با factory function (اختیاری).
        
        Args:
            name: نام قابلیت
            factory: تابع سازنده (async یا sync) — اگر None باشد،
                     فعال‌سازی فقط flag را true می‌کند (بدون ایجاد resource)
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
        if factory:
            self._factories[name] = factory
        self._enabled_callbacks[name] = []
        self._disabled_callbacks[name] = []
        logger.debug(f"Registered capability: {name} (risk={risk_level}, has_factory={factory is not None})")
    
    async def activate(self, name: str) -> Any:
        """فعال‌سازی تنبل یک قابلیت — resource را ایجاد می‌کند.
        
        - اگر resource قبلاً فعال شده، همان را برمی‌گرداند
        - وابستگی‌ها را به صورت بازگشتی فعال می‌کند
        - factory function را فراخوانی می‌کند (async یا sync)
        - resource را کش می‌کند و status را به‌روز می‌کند
        
        Args:
            name: نام قابلیت
            
        Returns:
            resource فعال‌شده، یا None اگر factory نداشته باشد
            
        Raises:
            ValueError: اگر قابلیت ثبت نشده باشد
        """
        if name not in self._capabilities:
            raise ValueError(f"Unknown capability: {name}")
        
        # Already activated — return cached resource
        if name in self._resources:
            cap = self._capabilities[name]
            cap.last_used = f"{time.time():.0f}"
            return self._resources[name]
        
        cap = self._capabilities[name]
        
        try:
            # Activate dependencies first (recursive)
            for dep in cap.dependencies:
                if dep not in self._resources:
                    await self.activate(dep)
            
            # Create resource via factory
            factory = self._factories.get(name)
            if factory:
                resource = factory()
                if asyncio.iscoroutine(resource) or (hasattr(resource, '__await__')):
                    resource = await resource
                self._resources[name] = resource
                logger.info(f"Activated capability: {name} ({type(resource).__name__})")
            else:
                logger.debug(f"Activated capability: {name} (no factory)")
            
            cap.enabled = True
            cap.initialization_error = None
            cap.last_used = f"{time.time():.0f}"
            
            # Fire activation callbacks
            for callback in self._enabled_callbacks.get(name, []):
                try:
                    result = callback()
                    if asyncio.iscoroutine(result) or (hasattr(result, '__await__')):
                        await result
                except Exception as e:
                    logger.warning(f"Callback error for {name}: {e}")
            
            return self._resources.get(name)
            
        except Exception as e:
            cap.initialization_error = str(e)
            logger.error(f"Failed to activate {name}: {e}", exc_info=True)
            raise
    
    def get(self, name: str) -> Any:
        """بازیابی resource فعال‌شده.
        
        Args:
            name: نام قابلیت
            
        Returns:
            resource اگر فعال شده باشد، در غیر اینصورت None
        """
        return self._resources.get(name)
    
    def is_active(self, name: str) -> bool:
        """آیا قابلیت فعال شده است (resource وجود دارد)؟
        
        Args:
            name: نام قابلیت
            
        Returns:
            bool: True اگر resource فعال شده
        """
        return name in self._resources
    
    def has(self, name: str) -> bool:
        """آیا قابلیت ثبت شده است؟
        
        Args:
            name: نام قابلیت
            
        Returns:
            bool: True اگر ثبت شده
        """
        return name in self._capabilities
    
    async def deactivate(self, name: str) -> bool:
        """غیرفعال‌سازی یک قابلیت و حذف resource آن.
        
        Args:
            name: نام قابلیت
            
        Returns:
            bool: True اگر موفق
        """
        resource = self._resources.pop(name, None)
        if resource is not None:
            # Try cleanup if the resource has a cleanup/shutdown method
            for method_name in ('cleanup', 'shutdown', 'close'):
                method = getattr(resource, method_name, None)
                if method:
                    try:
                        result = method()
                        if asyncio.iscoroutine(result) or (hasattr(result, '__await__')):
                            await result
                    except Exception as e:
                        logger.warning(f"Cleanup error for {name}.{method_name}: {e}")
                    break
            
            if name in self._capabilities:
                self._capabilities[name].enabled = False
            logger.info(f"Deactivated capability: {name}")
            
            # Fire deactivation callbacks
            for callback in self._disabled_callbacks.get(name, []):
                try:
                    result = callback()
                    if asyncio.iscoroutine(result) or (hasattr(result, '__await__')):
                        await result
                except Exception as e:
                    logger.warning(f"Callback error for {name}: {e}")
            
            return True
        
        return False
    
    # ═══════════════════════════════════════════════════════════
    # Legacy API (backward compatible)
    # ═══════════════════════════════════════════════════════════
    
    async def enable(
        self,
        name: str,
        initializer: Optional[callable] = None
    ) -> bool:
        """فعال‌سازی یک قابلیت (backward compatible).
        
        در معماری جدید، این متد activate را صدا می‌زند.
        اگر factory ثبت شده باشد، resource ساخته می‌شود.
        
        Args:
            name: نام قابلیت
            initializer: (قدیمی) تابع اولیه‌سازی — اگر factory نباشد استفاده می‌شود
        
        Returns:
            bool: True اگر موفق
        """
        if name not in self._capabilities:
            logger.warning(f"Unknown capability: {name}")
            return False
        
        cap = self._capabilities[name]
        
        if cap.enabled:
            return True
        
        try:
            # Activate dependencies
            for dep in cap.dependencies:
                dep_cap = self._capabilities.get(dep)
                if dep_cap and not dep_cap.enabled:
                    await self.enable(dep)
            
            # Use factory if registered, otherwise use legacy initializer
            if name in self._factories:
                await self.activate(name)
            elif initializer:
                await initializer()
            
            cap.enabled = True
            cap.initialization_error = None
            logger.info(f"Enabled capability: {name}")
            
            for callback in self._enabled_callbacks.get(name, []):
                try:
                    result = callback()
                    if asyncio.iscoroutine(result) or (hasattr(result, '__await__')):
                        await result
                except Exception as e:
                    logger.warning(f"Callback error for {name}: {e}")
            
            return True
            
        except Exception as e:
            cap.enabled = False
            cap.initialization_error = str(e)
            logger.error(f"Failed to enable {name}: {e}", exc_info=True)
            return False
    
    async def disable(self, name: str) -> bool:
        """غیرفعال‌سازی یک قابلیت (backward compatible).
        
        Args:
            name: نام قابلیت
        
        Returns:
            bool: True اگر موفق
        """
        if name not in self._capabilities:
            logger.warning(f"Unknown capability: {name}")
            return False
        
        cap = self._capabilities[name]
        
        if not cap.enabled and name not in self._resources:
            return True
        
        try:
            # Deactivate via new or legacy path
            if name in self._resources:
                await self.deactivate(name)
            else:
                cap.enabled = False
                logger.info(f"Disabled capability: {name}")
                
                for callback in self._disabled_callbacks.get(name, []):
                    try:
                        result = callback()
                        if asyncio.iscoroutine(result) or (hasattr(result, '__await__')):
                            await result
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
        if name in self._resources:
            return True
        cap = self._capabilities.get(name)
        return cap.enabled if cap else False
    
    def get_status(self) -> Dict[str, Dict[str, Any]]:
        """دریافت وضعیت تمام قابلیت‌ها
        
        Returns:
            dict: وضعیت هر قابلیت
        """
        result = {}
        for name, cap in self._capabilities.items():
            info = {
                "enabled": cap.enabled or name in self._resources,
                "risk_level": cap.risk_level,
                "dependencies": cap.dependencies,
                "has_factory": name in self._factories,
                "has_resource": name in self._resources,
                "initialization_error": cap.initialization_error,
                "last_used": cap.last_used,
            }
            if name in self._resources:
                info["resource_type"] = type(self._resources[name]).__name__
            result[name] = info
        return result
    
    def get_enabled(self) -> List[str]:
        """دریافت لیست قابلیت‌های فعال
        
        Returns:
            list: نام‌های قابلیت‌های فعال
        """
        enabled = [name for name, cap in self._capabilities.items() if cap.enabled]
        for name in self._resources:
            if name not in enabled:
                enabled.append(name)
        return enabled
    
    def get_active(self) -> Dict[str, Any]:
        """دریافت دیکشنری قابلیت‌های فعال با resourceهایشان.
        
        Returns:
            dict: {name: resource} برای هر قابلیت فعال
        """
        return dict(self._resources)
    
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
        # Deactivate all active resources
        for name in list(self._resources.keys()):
            await self.deactivate(name)
        # Legacy cleanup
        for name in list(self._capabilities.keys()):
            cap = self._capabilities[name]
            if cap.enabled and name not in self._resources:
                cap.enabled = False
        logger.info("Cleanup complete")
    
    def __repr__(self) -> str:
        """نمایش مدیریت‌کننده"""
        active = list(self._resources.keys())
        enabled = self.get_enabled()
        return f"CapabilityManager(active={active}, enabled={enabled})"
