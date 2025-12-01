# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""تست‌های سیستم اقدامات هوشمند بر اساس Context."""

import pytest
import asyncio
from core.context_aware_actions import (
    ContextAwareActions,
    SystemState,
    ApplicationCategory,
)


class TestContextAwareActions:
    """تست‌های ContextAwareActions."""
    
    def setup_method(self):
        """راه‌اندازی قبل از هر تست."""
        self.context = ContextAwareActions()
    
    @pytest.mark.asyncio
    async def test_get_current_context(self):
        """تست دریافت Context فعلی."""
        info = await self.context.get_current_context()
        
        assert info is not None
        assert hasattr(info, "active_window")
        assert hasattr(info, "active_process")
        assert hasattr(info, "app_category")
        assert hasattr(info, "system_state")
        assert hasattr(info, "cpu_usage")
        assert hasattr(info, "ram_usage")
        assert hasattr(info, "is_fullscreen")
        assert hasattr(info, "mouse_position")
        assert hasattr(info, "timestamp")
    
    @pytest.mark.asyncio
    async def test_context_values_valid(self):
        """تست معتبر بودن مقادیر Context."""
        info = await self.context.get_current_context()
        
        # Strings
        assert isinstance(info.active_window, str)
        assert isinstance(info.active_process, str)
        
        # Enums
        assert isinstance(info.app_category, ApplicationCategory)
        assert isinstance(info.system_state, SystemState)
        
        # Numbers
        assert isinstance(info.cpu_usage, float)
        assert isinstance(info.ram_usage, float)
        assert 0 <= info.cpu_usage <= 100
        assert 0 <= info.ram_usage <= 100
        
        # Boolean
        assert isinstance(info.is_fullscreen, bool)
        
        # Tuple
        assert isinstance(info.mouse_position, tuple)
        assert len(info.mouse_position) == 2
        
        # Timestamp
        assert isinstance(info.timestamp, float)
        assert info.timestamp > 0
    
    @pytest.mark.asyncio
    async def test_context_cache(self):
        """تست سیستم cache Context."""
        # دریافت اول
        info1 = await self.context.get_current_context(use_cache=True)
        timestamp1 = info1.timestamp
        
        # دریافت دوم (باید از cache استفاده کند)
        info2 = await self.context.get_current_context(use_cache=True)
        timestamp2 = info2.timestamp
        
        # Timestamps باید یکسان باشند (از cache)
        assert timestamp1 == timestamp2
        
        # دریافت سوم (بدون cache)
        await asyncio.sleep(0.1)
        info3 = await self.context.get_current_context(use_cache=False)
        timestamp3 = info3.timestamp
        
        # Timestamp سوم باید متفاوت باشد
        assert timestamp3 > timestamp1
    
    def test_determine_system_state_idle(self):
        """تست تشخیص وضعیت IDLE."""
        state = self.context._determine_system_state(
            cpu_usage=10.0,
            ram_usage=30.0,
            app_category=ApplicationCategory.OTHER
        )
        assert state == SystemState.IDLE
    
    def test_determine_system_state_busy(self):
        """تست تشخیص وضعیت BUSY."""
        state = self.context._determine_system_state(
            cpu_usage=80.0,
            ram_usage=85.0,
            app_category=ApplicationCategory.OTHER
        )
        assert state == SystemState.BUSY
    
    def test_determine_system_state_gaming(self):
        """تست تشخیص وضعیت GAMING."""
        state = self.context._determine_system_state(
            cpu_usage=50.0,
            ram_usage=60.0,
            app_category=ApplicationCategory.GAME
        )
        assert state == SystemState.GAMING
    
    def test_determine_system_state_working(self):
        """تست تشخیص وضعیت WORKING."""
        state = self.context._determine_system_state(
            cpu_usage=40.0,
            ram_usage=50.0,
            app_category=ApplicationCategory.EDITOR
        )
        assert state == SystemState.WORKING
    
    @pytest.mark.asyncio
    async def test_should_execute_action_normal(self):
        """تست تصمیم اجرای اقدام در حالت عادی."""
        info = await self.context.get_current_context()
        
        action = {
            "type": "LaunchApp",
            "priority": "normal",
        }
        
        should_execute, reason = self.context.should_execute_action(action, info)
        
        # در حالت عادی باید اجرا شود
        assert isinstance(should_execute, bool)
        assert isinstance(reason, str)
    
    def test_should_execute_action_gaming_low_priority(self):
        """تست رد شدن اقدام با اولویت پایین در حالت GAMING."""
        # ساخت Context با وضعیت GAMING
        from core.context_aware_actions import ContextInfo
        import time
        
        gaming_context = ContextInfo(
            active_window="Game Window",
            active_process="game.exe",
            app_category=ApplicationCategory.GAME,
            system_state=SystemState.GAMING,
            cpu_usage=60.0,
            ram_usage=70.0,
            is_fullscreen=True,
            mouse_position=(100, 100),
            timestamp=time.time(),
        )
        
        action = {
            "type": "InstallPackage",
            "priority": "low",
        }
        
        should_execute, reason = self.context.should_execute_action(action, gaming_context)
        
        assert should_execute is False
        assert "gaming" in reason.lower()
    
    def test_should_execute_action_gaming_high_priority(self):
        """تست اجرای اقدام با اولویت بالا در حالت GAMING."""
        from core.context_aware_actions import ContextInfo
        import time
        
        gaming_context = ContextInfo(
            active_window="Game Window",
            active_process="game.exe",
            app_category=ApplicationCategory.GAME,
            system_state=SystemState.GAMING,
            cpu_usage=60.0,
            ram_usage=70.0,
            is_fullscreen=True,
            mouse_position=(100, 100),
            timestamp=time.time(),
        )
        
        action = {
            "type": "CriticalAction",
            "priority": "high",
        }
        
        should_execute, reason = self.context.should_execute_action(action, gaming_context)
        
        assert should_execute is True
    
    def test_should_execute_action_fullscreen(self):
        """تست رد شدن اقدام مزاحم در حالت fullscreen."""
        from core.context_aware_actions import ContextInfo
        import time
        
        fullscreen_context = ContextInfo(
            active_window="Presentation",
            active_process="powerpoint.exe",
            app_category=ApplicationCategory.OFFICE,
            system_state=SystemState.WORKING,
            cpu_usage=30.0,
            ram_usage=40.0,
            is_fullscreen=True,
            mouse_position=(100, 100),
            timestamp=time.time(),
        )
        
        action = {
            "type": "LaunchApp",  # intrusive
            "priority": "normal",
        }
        
        should_execute, reason = self.context.should_execute_action(action, fullscreen_context)
        
        assert should_execute is False
        assert "fullscreen" in reason.lower()
    
    def test_adjust_action_timing_gaming(self):
        """تست تنظیم timing در حالت GAMING."""
        from core.context_aware_actions import ContextInfo
        import time
        
        gaming_context = ContextInfo(
            active_window="Game",
            active_process="game.exe",
            app_category=ApplicationCategory.GAME,
            system_state=SystemState.GAMING,
            cpu_usage=60.0,
            ram_usage=70.0,
            is_fullscreen=False,
            mouse_position=(100, 100),
            timestamp=time.time(),
        )
        
        action = {
            "type": "DesktopClick",
            "params": {"interval": 1.0},
        }
        
        adjusted = self.context.adjust_action_timing(action, gaming_context)
        
        # در حالت gaming باید سریع‌تر شود (0.5x)
        assert adjusted["params"]["interval"] == 0.5
    
    def test_adjust_action_timing_busy(self):
        """تست تنظیم timing در حالت BUSY."""
        from core.context_aware_actions import ContextInfo
        import time
        
        busy_context = ContextInfo(
            active_window="App",
            active_process="app.exe",
            app_category=ApplicationCategory.OTHER,
            system_state=SystemState.BUSY,
            cpu_usage=80.0,
            ram_usage=85.0,
            is_fullscreen=False,
            mouse_position=(100, 100),
            timestamp=time.time(),
        )
        
        action = {
            "type": "DesktopClick",
            "params": {"interval": 1.0, "timeout": 10.0},
        }
        
        adjusted = self.context.adjust_action_timing(action, busy_context)
        
        # در حالت busy باید کندتر شود (1.5x) و timeout بیشتر (2x)
        assert adjusted["params"]["interval"] == 1.5
        assert adjusted["params"]["timeout"] == 20.0
    
    def test_app_category_detection_browser(self):
        """تست تشخیص دسته Browser."""
        assert self.context._app_categories.get("chrome.exe") == ApplicationCategory.BROWSER
        assert self.context._app_categories.get("firefox.exe") == ApplicationCategory.BROWSER
    
    def test_app_category_detection_editor(self):
        """تست تشخیص دسته Editor."""
        assert self.context._app_categories.get("code.exe") == ApplicationCategory.EDITOR
        assert self.context._app_categories.get("notepad++.exe") == ApplicationCategory.EDITOR
    
    def test_app_category_detection_game(self):
        """تست تشخیص دسته Game."""
        assert self.context._app_categories.get("steam.exe") == ApplicationCategory.GAME
    
    def test_app_category_detection_communication(self):
        """تست تشخیص دسته Communication."""
        assert self.context._app_categories.get("discord.exe") == ApplicationCategory.COMMUNICATION
        assert self.context._app_categories.get("telegram.exe") == ApplicationCategory.COMMUNICATION
    
    @pytest.mark.asyncio
    async def test_wait_for_appropriate_time_immediate(self):
        """تست انتظار برای زمان مناسب (فوری)."""
        action = {
            "type": "QueryHardware",  # اقدام ساده
            "priority": "normal",
        }
        
        # باید خیلی سریع True برگرداند
        success = await asyncio.wait_for(
            self.context.wait_for_appropriate_time(action, max_wait=2.0),
            timeout=3.0
        )
        
        assert success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
