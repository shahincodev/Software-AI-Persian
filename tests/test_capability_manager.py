"""
Unit tests for CapabilityManager

Tests for capability registration, enabling/disabling, and state management.
"""

import pytest
from core.capability_manager import CapabilityManager, CapabilityType


@pytest.fixture
def manager():
    """Initialize CapabilityManager for testing"""
    manager = CapabilityManager()
    # Register test capabilities
    manager.register("browser_use", risk_level="medium")
    manager.register("desktop_automation", risk_level="high")
    manager.register("autonomous_agent", risk_level="high", dependencies=["desktop_automation"])
    manager.register("task_mode", risk_level="safe")
    return manager


class TestCapabilityRegistration:
    """Test capability registration"""
    
    def test_register_capability(self, manager):
        """Test registering a capability"""
        status = manager.get_status()
        assert "browser_use" in status
        assert not status["browser_use"]["enabled"]
    
    def test_register_with_dependencies(self, manager):
        """Test registering capability with dependencies"""
        status = manager.get_status()
        assert status["autonomous_agent"]["dependencies"] == ["desktop_automation"]
    
    def test_duplicate_registration(self, manager):
        """Test that duplicate registration is ignored"""
        # This should log a warning but not fail
        manager.register("browser_use")
        status = manager.get_status()
        assert "browser_use" in status


class TestCapabilityEnabling:
    """Test enabling/disabling capabilities"""
    
    @pytest.mark.asyncio
    async def test_enable_capability(self, manager):
        """Test enabling a capability"""
        success = await manager.enable("browser_use")
        assert success
        assert manager.is_enabled("browser_use")
    
    @pytest.mark.asyncio
    async def test_disable_capability(self, manager):
        """Test disabling a capability"""
        await manager.enable("browser_use")
        success = await manager.disable("browser_use")
        assert success
        assert not manager.is_enabled("browser_use")
    
    @pytest.mark.asyncio
    async def test_enable_with_initializer(self, manager):
        """Test enabling capability with initializer"""
        initialized = False
        
        async def initializer():
            nonlocal initialized
            initialized = True
        
        success = await manager.enable("browser_use", initializer=initializer)
        assert success
        assert initialized
    
    @pytest.mark.asyncio
    async def test_dependency_auto_enable(self, manager):
        """Test that enabling capability auto-enables dependencies"""
        await manager.enable("autonomous_agent")
        assert manager.is_enabled("autonomous_agent")
        # desktop_automation should also be enabled as it's a dependency
        assert manager.is_enabled("desktop_automation")


class TestCapabilityQueries:
    """Test querying capability status"""
    
    @pytest.mark.asyncio
    async def test_get_status(self, manager):
        """Test getting full status"""
        await manager.enable("browser_use")
        status = manager.get_status()
        
        assert status["browser_use"]["enabled"] is True
        assert status["desktop_automation"]["enabled"] is False
        assert status["browser_use"]["risk_level"] == "medium"
    
    @pytest.mark.asyncio
    async def test_get_enabled(self, manager):
        """Test getting list of enabled capabilities"""
        await manager.enable("browser_use")
        await manager.enable("task_mode")
        
        enabled = manager.get_enabled()
        assert "browser_use" in enabled
        assert "task_mode" in enabled
        assert "desktop_automation" not in enabled
        assert len(enabled) == 2
    
    def test_is_enabled(self, manager):
        """Test is_enabled query"""
        assert not manager.is_enabled("browser_use")
        # Don't enable, just check


class TestCapabilityCallbacks:
    """Test callback registration and execution"""
    
    @pytest.mark.asyncio
    async def test_on_enabled_callback(self, manager):
        """Test callback when capability is enabled"""
        called = False
        
        def callback():
            nonlocal called
            called = True
        
        manager.on_enabled("browser_use", callback)
        await manager.enable("browser_use")
        assert called
    
    @pytest.mark.asyncio
    async def test_on_disabled_callback(self, manager):
        """Test callback when capability is disabled"""
        called = False
        
        def callback():
            nonlocal called
            called = True
        
        await manager.enable("browser_use")
        manager.on_disabled("browser_use", callback)
        await manager.disable("browser_use")
        assert called


class TestCapabilityCleanup:
    """Test cleanup functionality"""
    
    @pytest.mark.asyncio
    async def test_cleanup_disables_all(self, manager):
        """Test cleanup disables all enabled capabilities"""
        await manager.enable("browser_use")
        await manager.enable("task_mode")
        
        await manager.cleanup()
        
        assert not manager.is_enabled("browser_use")
        assert not manager.is_enabled("task_mode")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
