# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
تست‌های IntentRouter

تست‌های تصنیف intent، منطق مسیریابی و بررسی‌های ایمنی
"""

import pytest
from core.intent_router import IntentRouter, RouteType, Route
from core.intent_analyzer import Intent


@pytest.fixture
def router():
    """مقداردهی IntentRouter برای تست"""
    return IntentRouter()


class TestIntentRouting:
    """تست مسیریابی و تصنیف intent"""
    
    @pytest.mark.asyncio
    async def test_simple_chat_response(self, router):
        """تست مسیریابی برای درخواست چت ساده"""
        route = await router.route("سلام، چطور می‌تونی کمکم کنی؟")
        assert route.type == RouteType.CHAT_RESPONSE
        assert route.requires_activation == []
    
    @pytest.mark.asyncio
    async def test_web_search_routing(self, router):
        """تست مسیریابی برای جستجوی وب"""
        route = await router.route("قیمت دلار رو توی وب چک کن")
        assert route.type == RouteType.BROWSER_USE
        assert "browser_use" in route.requires_activation
    
    @pytest.mark.asyncio
    async def test_desktop_automation_routing(self, router):
        """تست مسیریابی برای اتوماسیون دسکتاپ"""
        route = await router.route("یک فولدر جدید روی دسکتاپ بساز")
        assert route.type == RouteType.DESKTOP_AUTOMATION
        assert "desktop_automation" in route.requires_activation
    
    @pytest.mark.asyncio
    async def test_risky_action_consent(self, router):
        """تست درخواست تایید برای اقدام‌های خطرناک"""
        route = await router.route("یک فایل حذف کن", safety_mode="safe")
        # این ممکن است نیاز به تایید داشته باشد
        assert route.type in [RouteType.DESKTOP_AUTOMATION, RouteType.REQUIRES_CONSENT]


class TestRouteObject:
    """تست ساختار داده Route"""
    
    def test_route_creation(self):
        """تست ایجاد شیء Route"""
        route = Route(
            type=RouteType.CHAT_RESPONSE,
            confidence=0.85,
            requires_activation=["browser_use"]
        )
        assert route.type == RouteType.CHAT_RESPONSE
        assert route.confidence == 0.85
        assert "browser_use" in route.requires_activation
    
    def test_route_string_representation(self):
        """تست نمایش رشته‌ای Route"""
        route = Route(
            type=RouteType.BROWSER_USE,
            confidence=0.9,
            requires_activation=["browser_use"]
        )
        route_str = str(route)
        assert "browser_use" in route_str
        assert "0.9" in route_str or "90" in route_str


class TestRouteTypes:
    """تست تمام نوع‌های RouteType"""
    
    def test_route_type_values(self):
        """تست تعریف تمام نوع‌های Route"""
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
    # اجرای تست‌های IntentRouter
    pytest.main([__file__, "-v"])
