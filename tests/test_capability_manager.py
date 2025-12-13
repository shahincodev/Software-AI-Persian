# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
تست‌های CapabilityManager

تست‌های ثبت، فعال‌سازی/غیرفعال‌سازی، و مدیریت وضعیت قابلیت‌ها
"""

import pytest
from core.capability_manager import CapabilityManager, CapabilityType


@pytest.fixture
def manager():
    """مقداردهی CapabilityManager برای تست"""
    manager = CapabilityManager()
    # Register test capabilities
    manager.register("browser_use", risk_level="medium")
    manager.register("desktop_automation", risk_level="high")
    manager.register("autonomous_agent", risk_level="high", dependencies=["desktop_automation"])
    manager.register("task_mode", risk_level="safe")
    return manager


class TestCapabilityRegistration:
    """تست ثبت قابلیت‌ها"""
    
    def test_register_capability(self, manager):
        """تست ثبت یک قابلیت"""
        status = manager.get_status()
        assert "browser_use" in status
        assert not status["browser_use"]["enabled"]
    
    def test_register_with_dependencies(self, manager):
        """تست ثبت قابلیت با وابستگی‌ها"""
        status = manager.get_status()
        assert status["autonomous_agent"]["dependencies"] == ["desktop_automation"]
    
    def test_duplicate_registration(self, manager):
        """تست که ثبت تکراری무시می‌شود"""
        # این باید هشدار لاگ دهد اما شکست نخورد
        manager.register("browser_use")
        status = manager.get_status()
        assert "browser_use" in status


class TestCapabilityEnabling:
    """تست فعال‌سازی/غیرفعال‌سازی قابلیت‌ها"""
    
    @pytest.mark.asyncio
    async def test_enable_capability(self, manager):
        """تست فعال‌سازی یک قابلیت"""
        success = await manager.enable("browser_use")
        assert success
        assert manager.is_enabled("browser_use")
    
    @pytest.mark.asyncio
    async def test_disable_capability(self, manager):
        """تست غیرفعال‌سازی یک قابلیت"""
        await manager.enable("browser_use")
        success = await manager.disable("browser_use")
        assert success
        assert not manager.is_enabled("browser_use")
    
    @pytest.mark.asyncio
    async def test_enable_with_initializer(self, manager):
        """تست فعال‌سازی قابلیت با تابع اولیه‌سازی"""
        initialized = False
        
        async def initializer():
            nonlocal initialized
            initialized = True
        
        success = await manager.enable("browser_use", initializer=initializer)
        assert success
        assert initialized
    
    @pytest.mark.asyncio
    async def test_dependency_auto_enable(self, manager):
        """تست فعال‌سازی خودکار وابستگی‌ها"""
        await manager.enable("autonomous_agent")
        assert manager.is_enabled("autonomous_agent")
        # desktop_automation باید به عنوان وابستگی فعال شود
        assert manager.is_enabled("desktop_automation")


class TestCapabilityQueries:
    """تست کوئری‌های وضعیت قابلیت‌ها"""
    
    @pytest.mark.asyncio
    async def test_get_status(self, manager):
        """تست دریافت وضعیت کامل"""
        await manager.enable("browser_use")
        status = manager.get_status()
        
        assert status["browser_use"]["enabled"] is True
        assert status["desktop_automation"]["enabled"] is False
        assert status["browser_use"]["risk_level"] == "medium"
    
    @pytest.mark.asyncio
    async def test_get_enabled(self, manager):
        """تست دریافت لیست قابلیت‌های فعال"""
        await manager.enable("browser_use")
        await manager.enable("task_mode")
        
        enabled = manager.get_enabled()
        assert "browser_use" in enabled
        assert "task_mode" in enabled
        assert "desktop_automation" not in enabled
        assert len(enabled) == 2
    
    def test_is_enabled(self, manager):
        """تست کوئری is_enabled"""
        assert not manager.is_enabled("browser_use")
        # Don't enable, just check


class TestCapabilityCallbacks:
    """تست ثبت و اجرای رویدادهای فعال‌سازی"""
    
    @pytest.mark.asyncio
    async def test_on_enabled_callback(self, manager):
        """تست بازخوانی هنگام فعال‌سازی قابلیت"""
        called = False
        
        def callback():
            nonlocal called
            called = True
        
        manager.on_enabled("browser_use", callback)
        await manager.enable("browser_use")
        assert called
    
    @pytest.mark.asyncio
    async def test_on_disabled_callback(self, manager):
        """تست بازخوانی هنگام غیرفعال‌سازی قابلیت"""
        called = False
        
        def callback():
            nonlocal called
            called = True
        
        await manager.enable("browser_use")
        manager.on_disabled("browser_use", callback)
        await manager.disable("browser_use")
        assert called


class TestCapabilityCleanup:
    """تست عملکرد پاک‌سازی"""
    
    @pytest.mark.asyncio
    async def test_cleanup_disables_all(self, manager):
        """تست پاک‌سازی تمام قابلیت‌های فعال"""
        await manager.enable("browser_use")
        await manager.enable("task_mode")
        
        await manager.cleanup()
        
        assert not manager.is_enabled("browser_use")
        assert not manager.is_enabled("task_mode")


if __name__ == "__main__":
    # اجرای تست‌های pytest
    pytest.main([__file__, "-v"])
