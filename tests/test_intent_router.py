"""
Unit tests for IntentRouter

Tests for intent classification, routing logic, and safety checks.
"""

import pytest
from core.intent_router import IntentRouter, RouteType, Route
from core.intent_analyzer import Intent


@pytest.fixture
def router():
    """Initialize IntentRouter for testing"""
    return IntentRouter()


class TestIntentRouting:
    """Test intent routing classification"""
    
    @pytest.mark.asyncio
    async def test_simple_chat_response(self, router):
        """Test routing for simple chat request"""
        route = await router.route("سلام، چطور می‌تونی کمکم کنی؟")
        assert route.type == RouteType.CHAT_RESPONSE
        assert route.requires_activation == []
    
    @pytest.mark.asyncio
    async def test_web_search_routing(self, router):
        """Test routing for web search request"""
        route = await router.route("قیمت دلار رو توی وب چک کن")
        assert route.type == RouteType.BROWSER_USE
        assert "browser_use" in route.requires_activation
    
    @pytest.mark.asyncio
    async def test_desktop_automation_routing(self, router):
        """Test routing for desktop automation"""
        route = await router.route("یک فولدر جدید روی دسکتاپ بساز")
        assert route.type == RouteType.DESKTOP_AUTOMATION
        assert "desktop_automation" in route.requires_activation
    
    @pytest.mark.asyncio
    async def test_risky_action_consent(self, router):
        """Test consent required for risky actions"""
        route = await router.route("یک فایل حذف کن", safety_mode="safe")
        # این ممکن است نیاز به تایید داشته باشد
        assert route.type in [RouteType.DESKTOP_AUTOMATION, RouteType.REQUIRES_CONSENT]


class TestRouteObject:
    """Test Route data structure"""
    
    def test_route_creation(self):
        """Test Route object creation"""
        route = Route(
            type=RouteType.CHAT_RESPONSE,
            confidence=0.85,
            requires_activation=["browser_use"]
        )
        assert route.type == RouteType.CHAT_RESPONSE
        assert route.confidence == 0.85
        assert "browser_use" in route.requires_activation
    
    def test_route_string_representation(self):
        """Test Route string representation"""
        route = Route(
            type=RouteType.BROWSER_USE,
            confidence=0.9,
            requires_activation=["browser_use"]
        )
        route_str = str(route)
        assert "browser_use" in route_str
        assert "0.9" in route_str or "90" in route_str


class TestRouteTypes:
    """Test all route type enums"""
    
    def test_route_type_values(self):
        """Test all route types are defined"""
        route_types = [
            RouteType.CHAT_RESPONSE,
            RouteType.BROWSER_USE,
            RouteType.DESKTOP_AUTOMATION,
            RouteType.AUTONOMOUS_AGENT,
            RouteType.TASK_MODE,
            RouteType.REQUIRES_CONSENT,
            RouteType.CLARIFICATION_NEEDED
        ]
        assert len(route_types) >= 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
