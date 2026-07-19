# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
تست‌های SafetyConsentManager

تست‌های درخواست تایید، سطح‌های ریسک، و تصمیم‌های کاربر
"""

import pytest
from core.safety_consent_manager import (
    SafetyConsentManager,
    RiskLevel,
    ConsentRequest,
)


@pytest.fixture
def manager():
    """مقداردهی SafetyConsentManager برای تست"""
    return SafetyConsentManager()


@pytest.fixture
def manager_with_handler():
    """SafetyConsentManager با handler تایید"""
    async def consent_handler(message: str) -> bool:
        # شبیه‌سازی تایید خودکار برای تست
        return "browser_use" in message or "chat" in message
    
    return SafetyConsentManager(require_consent_handler=consent_handler)


class TestRiskLevels:
    """تست تعریف و مدیریت سطح‌های ریسک"""
    
    def test_default_risk_levels(self, manager):
        """تست سطح‌های ریسک پیش‌فرض"""
        assert manager.get_risk_level("browser_use") == RiskLevel.POWER
        assert manager.get_risk_level("desktop_automation") == RiskLevel.CRITICAL
        assert manager.get_risk_level("autonomous_agent") == RiskLevel.CRITICAL
        assert manager.get_risk_level("task_mode") == RiskLevel.POWER
        assert manager.get_risk_level("chat_response") == RiskLevel.SAFE
    
    def test_set_custom_risk_level(self, manager):
        """تست تنظیم سطح ریسک سفارشی"""
        manager.set_risk_level("browser_use", RiskLevel.SAFE)
        assert manager.get_risk_level("browser_use") == RiskLevel.SAFE
    
    def test_unknown_capability_defaults_to_power(self, manager):
        """تست قابلیت نامعروف به POWER پیش‌فرض است"""
        assert manager.get_risk_level("unknown_capability") == RiskLevel.POWER


class TestConsentRequests:
    """تست درخواست تایید"""
    
    @pytest.mark.asyncio
    async def test_safe_actions_auto_approved(self, manager):
        """تست اقدام‌های SAFE خودکار تایید می‌شوند"""
        result = await manager.request_consent(
            action="پاسخ چت",
            risk_level=RiskLevel.SAFE
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_power_action_without_handler_rejected(self, manager):
        """تست اقدام POWER بدون handler رد می‌شود"""
        result = await manager.request_consent(
            action="درخواست وب",
            risk_level=RiskLevel.POWER
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_critical_action_without_handler_rejected(self, manager):
        """تست اقدام CRITICAL بدون handler رد می‌شود"""
        result = await manager.request_consent(
            action="اتوماسیون دسکتاپ",
            risk_level=RiskLevel.CRITICAL
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_consent_message_format(self, manager):
        """تست فرمت پیام تایید"""
        request = ConsentRequest(
            action="کنترل ماوس",
            risk_level=RiskLevel.POWER,
            capability="desktop_automation",
            details="انجام کلیک در مختصات (100, 200)"
        )
        msg = request.to_user_message()
        assert "کنترل ماوس" in msg
        assert "قدرت‌مند" in msg
        assert "desktop_automation" in msg
        assert "انجام کلیک" in msg


class TestConsentWithHandler:
    """تست درخواست تایید با handler"""
    
    @pytest.mark.asyncio
    async def test_handler_approved_consent(self, manager_with_handler):
        """تست handler تایید درخواست"""
        result = await manager_with_handler.request_consent(
            action="browser_use",
            risk_level=RiskLevel.POWER
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_handler_rejected_consent(self, manager_with_handler):
        """تست handler رد درخواست"""
        result = await manager_with_handler.request_consent(
            action="حذف سیستمی",
            risk_level=RiskLevel.CRITICAL
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_capability_based_risk_level(self, manager_with_handler):
        """تست تعیین risk level بر اساس capability"""
        result = await manager_with_handler.request_consent(
            action="جستجو در وب",
            capability="browser_use"
        )
        assert result is True


class TestConsentHistory:
    """تست تاریخچه تصمیمات"""
    
    @pytest.mark.asyncio
    async def test_decision_recorded(self, manager_with_handler):
        """تست ثبت تصمیم"""
        await manager_with_handler.request_consent(
            action="جستجو",
            risk_level=RiskLevel.POWER
        )
        history = manager_with_handler.get_decision_history()
        assert len(history) == 1
        assert history[0]["action"] == "جستجو"
    
    @pytest.mark.asyncio
    async def test_multiple_decisions_tracked(self, manager_with_handler):
        """تست ثبت چندین تصمیم"""
        await manager_with_handler.request_consent(
            action="درخواست اول",
            risk_level=RiskLevel.POWER
        )
        await manager_with_handler.request_consent(
            action="درخواست دوم",
            risk_level=RiskLevel.CRITICAL
        )
        history = manager_with_handler.get_decision_history()
        assert len(history) == 2
    
    def test_clear_history(self, manager_with_handler):
        """تست پاک‌سازی تاریخچه"""
        manager_with_handler.clear_history()
        history = manager_with_handler.get_decision_history()
        assert len(history) == 0
    
    @pytest.mark.asyncio
    async def test_statistics(self, manager_with_handler):
        """تست آمار تصمیمات"""
        await manager_with_handler.request_consent("جستجو", RiskLevel.POWER)
        await manager_with_handler.request_consent("حذف", RiskLevel.CRITICAL)
        
        stats = manager_with_handler.get_statistics()
        assert stats["total_requests"] == 2
        assert stats["approved"] >= 0
        assert stats["rejected"] >= 0
        assert stats["approval_rate"] >= 0


class TestCanExecuteAction:
    """تست بررسی قابلیت اجرای اقدام"""
    
    @pytest.mark.asyncio
    async def test_safe_action_can_execute(self, manager):
        """تست اقدام SAFE می‌تواند اجرا شود"""
        result = await manager.can_execute_action(
            "پاسخ چت",
            capability="chat_response"
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_power_action_without_handler(self, manager):
        """تست اقدام POWER بدون handler نمی‌تواند اجرا شود"""
        result = await manager.can_execute_action(
            "درخواست وب",
            capability="browser_use"
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_critical_action_requires_approval(self, manager_with_handler):
        """تست اقدام CRITICAL برای تایید نیاز دارد"""
        result = await manager_with_handler.can_execute_action(
            "اتوماسیون",
            capability="desktop_automation",
            allow_auto_approve=False
        )
        # handler فقط browser_use و chat تایید می‌کند
        assert result is False


if __name__ == "__main__":
    # اجرای تست‌های pytest
    pytest.main([__file__, "-v"])
