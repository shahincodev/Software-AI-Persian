# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
مدیریت ایمنی و تایید کاربر

این ماژول سطح‌های ریسک را تعریف می‌کند، درخواست تایید کاربر را مدیریت می‌کند،
و اقدامات حساس را کنترل می‌کند. برای هر قابلیت سطح ریسک مشخص است:
- SAFE: بدون نیاز به تایید
- POWER: نیاز به تایید تعاملی
- CRITICAL: نیاز به تایید صریح و ثبت لاگ

مثال:
    >>> manager = SafetyConsentManager()
    >>> consent = await manager.request_consent(
    ...     action="کنترل ماوس",
    ...     risk_level="POWER",
    ...     details="انجام کلیک در مختصات (100, 200)"
    ... )
    >>> if consent:
    ...     # اقدام را انجام بده
    ...     pass
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, Callable, Awaitable

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """سطح‌های ریسک برای اقدامات سیستمی"""
    # کاملاً ایمن - بدون نیاز به تایید
    SAFE = "safe"
    
    # قدرت‌مند - نیاز به تایید ساده
    POWER = "power"
    
    # حساس - نیاز به تایید صریح
    CRITICAL = "critical"


@dataclass
class ConsentRequest:
    """درخواست تایید از کاربر"""
    action: str
    risk_level: RiskLevel
    details: Optional[str] = None
    capability: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_user_message(self) -> str:
        """تبدیل درخواست به پیام مناسب برای نمایش به کاربر"""
        risk_label = {
            RiskLevel.SAFE: "ایمن",
            RiskLevel.POWER: "قدرت‌مند",
            RiskLevel.CRITICAL: "بسیار حساس"
        }.get(self.risk_level, "نامشخص")
        
        msg = f"\n{'='*60}\n"
        msg += f"⚠️  درخواست تایید: {self.action}\n"
        msg += f"سطح ریسک: {risk_label}\n"
        if self.capability:
            msg += f"قابلیت: {self.capability}\n"
        if self.details:
            msg += f"توضیحات: {self.details}\n"
        msg += f"{'='*60}\n"
        msg += "آیا می‌خواهی این اقدام را انجام دهم؟ (بله/خیر): "
        return msg


@dataclass
class ConsentDecision:
    """تصمیم کاربر در مورد تایید"""
    approved: bool
    reason: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class SafetyConsentManager:
    """مدیریت ایمنی و تایید اقدامات حساس"""
    
    def __init__(self, require_consent_handler: Optional[Callable[[str], Awaitable[bool]]] = None):
        """
        مقداردهی مدیر ایمنی و تایید
        
        Args:
            require_consent_handler: تابع async برای درخواست تایید از کاربر
                                    می‌تواند None باشد (در آن صورت خودکار reject می‌شود)
        """
        self._require_consent_handler = require_consent_handler
        
        # سطح ریسک پیش‌فرض برای هر قابلیت
        self._capability_risk_levels: Dict[str, RiskLevel] = {
            "browser_use": RiskLevel.POWER,
            "desktop_automation": RiskLevel.CRITICAL,
            "autonomous_agent": RiskLevel.CRITICAL,
            "task_mode": RiskLevel.POWER,
            "chat_response": RiskLevel.SAFE,
        }
        
        # تاریخچه تصمیمات
        self._decision_history: list[tuple[ConsentRequest, ConsentDecision]] = []
    
    def set_risk_level(self, capability: str, risk_level: RiskLevel) -> None:
        """تعیین سطح ریسک برای یک قابلیت"""
        self._capability_risk_levels[capability] = risk_level
        logger.info(f"سطح ریسک {capability} به {risk_level.value} تغییر یافت")
    
    def get_risk_level(self, capability: str) -> RiskLevel:
        """دریافت سطح ریسک برای یک قابلیت"""
        return self._capability_risk_levels.get(capability, RiskLevel.POWER)
    
    async def request_consent(
        self,
        action: str,
        risk_level: Optional[RiskLevel] = None,
        capability: Optional[str] = None,
        details: Optional[str] = None
    ) -> bool:
        """
        درخواست تایید از کاربر برای یک اقدام حساس
        
        Args:
            action: توضیح اقدام
            risk_level: سطح ریسک (اگر None باشد از capability استخراج می‌شود)
            capability: نام قابلیت (برای استخراج risk level اگر داده نشده)
            details: جزئیات اضافی
            
        Returns:
            True اگر کاربر تایید کرد، False در غیر این صورت
        """
        # تعیین سطح ریسک
        if risk_level is None:
            if capability:
                risk_level = self.get_risk_level(capability)
            else:
                risk_level = RiskLevel.POWER
        
        # اگر SAFE است، خودکار تایید کن
        if risk_level == RiskLevel.SAFE:
            logger.debug(f"اقدام SAFE تایید شد: {action}")
            return True
        
        # درخواست ایجاد کن
        request = ConsentRequest(
            action=action,
            risk_level=risk_level,
            capability=capability,
            details=details
        )
        
        logger.info(f"درخواست تایید: {action} (risk={risk_level.value})")
        
        # اگر handler نیست، پیش‌فرض reject کن
        if self._require_consent_handler is None:
            logger.warning(f"هیچ handler تایید موجود نیست. اقدام {action} رد شد")
            decision = ConsentDecision(approved=False, reason="بدون handler تایید")
            self._decision_history.append((request, decision))
            return False
        
        # درخواست تایید
        try:
            approved = await self._require_consent_handler(request.to_user_message())
            decision = ConsentDecision(
                approved=approved,
                reason="تایید کاربر" if approved else "رد کاربر"
            )
            self._decision_history.append((request, decision))
            logger.info(f"تصمیم: {decision.reason}")
            return approved
        except Exception as e:
            logger.error(f"خطا در درخواست تایید: {e}")
            decision = ConsentDecision(approved=False, reason=f"خطا: {str(e)}")
            self._decision_history.append((request, decision))
            return False
    
    async def can_execute_action(
        self,
        action: str,
        capability: Optional[str] = None,
        allow_auto_approve: bool = True
    ) -> bool:
        """
        بررسی اینکه آیا اقدام می‌تواند اجرا شود
        
        Args:
            action: توضیح اقدام
            capability: نام قابلیت
            allow_auto_approve: آیا اقدام‌های SAFE خودکار تایید شوند؟
            
        Returns:
            True اگر اقدام می‌تواند اجرا شود
        """
        risk_level = self.get_risk_level(capability) if capability else RiskLevel.POWER
        
        if not allow_auto_approve or risk_level != RiskLevel.SAFE:
            return await self.request_consent(action, risk_level, capability)
        
        return True
    
    def get_decision_history(self) -> list[Dict[str, Any]]:
        """دریافت تاریخچه تمام تصمیمات"""
        return [
            {
                "action": req.action,
                "risk_level": req.risk_level.value,
                "capability": req.capability,
                "approved": dec.approved,
                "reason": dec.reason,
                "timestamp": dec.timestamp.isoformat()
            }
            for req, dec in self._decision_history
        ]
    
    def clear_history(self) -> None:
        """پاک کردن تاریخچه تصمیمات"""
        self._decision_history.clear()
        logger.info("تاریخچه تصمیمات پاک شد")
    
    def get_statistics(self) -> Dict[str, Any]:
        """دریافت آمار تصمیمات"""
        total = len(self._decision_history)
        approved = sum(1 for _, dec in self._decision_history if dec.approved)
        rejected = total - approved
        
        return {
            "total_requests": total,
            "approved": approved,
            "rejected": rejected,
            "approval_rate": (approved / total * 100) if total > 0 else 0
        }

    def record_decision(
        self,
        action: str,
        risk_level: RiskLevel,
        approved: bool,
        capability: Optional[str] = None,
        reason: Optional[str] = None
    ) -> None:
        """ثبت یک تصمیم تایید/رد برای سازگاری با ورودی‌های CLI.

        این متد اجازه می‌دهد تصمیم‌های کاربر که خارج از request_consent گرفته می‌شوند
        نیز در تاریخچه و متریک‌ها ثبت شوند.
        """
        request = ConsentRequest(action=action, risk_level=risk_level, capability=capability)
        decision = ConsentDecision(approved=approved, reason=reason or ("user_yes" if approved else "user_no"))
        self._decision_history.append((request, decision))
        logger.info(
            "Consent decision recorded action=%s risk=%s approved=%s reason=%s",
            action,
            risk_level.value,
            approved,
            decision.reason,
        )
