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
    async def test_task_mode_routing(self, router):
        """تست مسیریابی برای حالت تسک‌محور و استخراج چند تسک"""
        route = await router.route("task one; task two")
        assert route.type == RouteType.TASK_MODE
        assert "task_mode" in route.requires_activation
        assert route.metadata.get("tasks_count") == 2
    
    @pytest.mark.asyncio
    async def test_risky_action_consent(self, router):
        """تست درخواست تایید برای اقدام‌های خطرناک"""
        route = await router.route("یک فایل حذف کن", safety_mode="safe")
        # این ممکن است نیاز به تایید داشته باشد
        assert route.type in [RouteType.DESKTOP_AUTOMATION, RouteType.REQUIRES_CONSENT]

    # ===== Gap 1 regression tests: conversational questions → CHAT_RESPONSE =====

    @pytest.mark.asyncio
    async def test_conversational_what_is_a_folder(self, router):
        """Regression: 'What is a folder?' should not route to desktop automation"""
        route = await router.route("What is a folder?")
        assert route.type == RouteType.CHAT_RESPONSE

    @pytest.mark.asyncio
    async def test_conversational_what_is_the_desktop(self, router):
        """Regression: 'What is the desktop?' should not route to desktop automation"""
        route = await router.route("What is the desktop?")
        assert route.type == RouteType.CHAT_RESPONSE

    @pytest.mark.asyncio
    async def test_conversational_how_do_i_use_notepad(self, router):
        """Regression: 'How do I use Notepad?' should not route to desktop automation"""
        route = await router.route("How do I use Notepad?")
        assert route.type == RouteType.CHAT_RESPONSE

    @pytest.mark.asyncio
    async def test_conversational_can_you_tell_me_what_a_file_is(self, router):
        """Regression: 'Can you tell me what a file is?' should not route to desktop automation"""
        route = await router.route("Can you tell me what a file is?")
        assert route.type == RouteType.CHAT_RESPONSE

    @pytest.mark.asyncio
    async def test_conversational_what_is_a_directory(self, router):
        """Regression: 'What is a directory?' should not route to desktop automation"""
        route = await router.route("What is a directory?")
        assert route.type == RouteType.CHAT_RESPONSE

    @pytest.mark.asyncio
    async def test_desktop_create_file_on_drive(self, router):
        """Regression: 'Create a file on drive D' must route to desktop automation"""
        route = await router.route("Create a file on drive D")
        assert route.type == RouteType.DESKTOP_AUTOMATION

    @pytest.mark.asyncio
    async def test_desktop_open_notepad(self, router):
        """Regression: 'open notepad' must route to desktop automation"""
        route = await router.route("open notepad")
        assert route.type == RouteType.DESKTOP_AUTOMATION

    @pytest.mark.asyncio
    async def test_desktop_delete_file(self, router):
        """Regression: 'delete the file report.txt' must route to desktop automation"""
        route = await router.route("delete the file report.txt")
        assert route.type == RouteType.DESKTOP_AUTOMATION

    @pytest.mark.asyncio
    async def test_desktop_click_on_start(self, router):
        """Regression: 'Click on start' must route to desktop automation"""
        route = await router.route("Click on start")
        assert route.type == RouteType.DESKTOP_AUTOMATION

    # ===== Verb override regression: informational "how to" questions =====

    @pytest.mark.asyncio
    async def test_conversational_tell_me_how_to_create_a_folder(self, router):
        """Regression: 'Tell me how to create a folder' → CHAT_RESPONSE, not DESKTOP_AUTOMATION.
        The verb override in _check_verb_override must NOT rewrite 'converse'→'create'
        for informational how-to questions."""
        route = await router.route("Tell me how to create a folder")
        assert route.type == RouteType.CHAT_RESPONSE, (
            f"Expected CHAT_RESPONSE, got {route.type.name}. "
            f"Verb override may have misfired."
        )

    @pytest.mark.asyncio
    async def test_conversational_how_can_i_create_a_backup(self, router):
        """Regression: 'How can I create a backup?' → CHAT_RESPONSE"""
        route = await router.route("How can I create a backup?")
        assert route.type == RouteType.CHAT_RESPONSE

    @pytest.mark.asyncio
    async def test_conversational_how_do_i_delete_a_file(self, router):
        """Regression: 'How do I delete a file?' → CHAT_RESPONSE"""
        route = await router.route("How do I delete a file?")
        assert route.type == RouteType.CHAT_RESPONSE

    @pytest.mark.asyncio
    async def test_automation_can_you_create_a_folder(self, router):
        """Verification: 'Can you create a folder?' must still route to DESKTOP_AUTOMATION
        (polite command, not informational question — no 'how' pattern)."""
        route = await router.route("Can you create a folder?")
        assert route.type == RouteType.DESKTOP_AUTOMATION, (
            f"Polite command incorrectly routed to {route.type.name}. "
            f"Fix must not suppress legitimate action requests."
        )


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
