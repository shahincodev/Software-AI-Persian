# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Intent Router - مسیریابی هوشمند درخواست‌های کاربر

این ماژول درخواست‌های کاربر را تجزیه می‌کند و تصمیم می‌گیرد کدام مسیر اجرایی
(plain chat response، browser-use، desktop automation، autonomous agent، task mode)
لازم است. این حلقه میانی میان کاربر و قابلیت‌های سیستم است.

مثال:
    >>> router = IntentRouter()
    >>> route = await router.route("برو وب و قیمت دلار رو چک کن")
    >>> print(route.type)  # RouteType.BROWSER_USE
    >>> print(route.requires_activation)  # ["browser_use"]
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any

from core.intent_analyzer import IntentAnalyzer, Intent, IntentAnalysisResult
from core.safety_consent_manager import RiskLevel

logger = logging.getLogger(__name__)


class RouteType(Enum):
    """نوع‌های مسیریابی ممکن"""
    # پاسخ متنی ساده (بدون نیاز به ماژول‌های اضافی)
    CHAT_RESPONSE = "chat_response"
    
    # کنترل مرورگر
    BROWSER_USE = "browser_use"
    
    # اتوماسیون دسکتاپ ویندوز
    DESKTOP_AUTOMATION = "desktop_automation"
    
    # عامل خودمختار (vision-based)
    AUTONOMOUS_AGENT = "autonomous_agent"
    
    # حالت تسک‌محور (صف‌بندی و اجرای ساخت‌یافته)
    TASK_MODE = "task_mode"
    
    # درخواست نیاز به تایید کاربر
    REQUIRES_CONSENT = "requires_consent"
    
    # نیاز به توضیح بیشتر
    CLARIFICATION_NEEDED = "clarification_needed"


@dataclass
class Route:
    """نتیجه مسیریابی
    
    Attributes:
        type: نوع مسیریابی (RouteType)
        intent: Intent تحلیل‌شده
        requires_activation: لیست قابلیت‌هایی که باید فعال شوند
        requires_consent: آیا نیاز به تایید کاربر دارد
        risk_level: سطح ریسک برای این درخواست
        consent_message: پیام تایید (اگر لازم)
        confidence: اطمینان روند مسیریابی
        metadata: اطلاعات اضافی برای اجرا
    """
    type: RouteType
    intent: Optional[Intent] = None
    requires_activation: List[str] = field(default_factory=list)
    requires_consent: bool = False
    risk_level: RiskLevel = RiskLevel.SAFE
    consent_message: str = ""
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """نمایش انسانی Route"""
        msg = f"Route({self.type.value}, confidence={self.confidence:.0%}"
        if self.requires_activation:
            msg += f", activate={self.requires_activation}"
        if self.requires_consent:
            msg += f", needs_consent=True, risk={self.risk_level.value}"
        msg += ")"
        return msg


class IntentRouter:
    """مسیریاب هوشمند برای درخواست‌های کاربر
    
    این کلاس:
    1. درخواست را با IntentAnalyzer تجزیه می‌کند
    2. نوع مسیریابی را تعیین می‌کند
    3. قابلیت‌های لازم برای فعال‌سازی را شناسایی می‌کند
    4. درخواست‌های پرریسک را برای تایید پرچم می‌کند
    """
    
    def __init__(self):
        """مقداردهی Router"""
        self.intent_analyzer = IntentAnalyzer()
        logger.info("IntentRouter initialized")
    
    async def route(
        self,
        user_text: str,
        safety_mode: str = "safe",
        current_capabilities: Optional[Dict[str, bool]] = None
    ) -> Route:
        """مسیریابی درخواست کاربر
        
        Args:
            user_text: درخواست کاربر
            safety_mode: حالت ایمنی (safe/power)
            current_capabilities: وضعیت قابلیت‌های فعلی {'browser_use': True, ...}
        
        Returns:
            Route: نتیجه مسیریابی با سطح ریسک
        """
        try:
            # تجزیه درخواست
            result = await self.intent_analyzer.analyze(user_text)
            logger.debug(f"Analyzed intent: {result}")
            
            if not result or not result.intent:
                return Route(
                    type=RouteType.CLARIFICATION_NEEDED,
                    confidence=0.0,
                    risk_level=RiskLevel.SAFE,
                    consent_message="نتوانستم درخواست شما را درک کنم. لطفاً توضیح دهید."
                )
            
            intent = result.intent
            
            # تعیین مسیریابی بر اساس intent
            route = self._classify_intent(intent, safety_mode)
            route.intent = intent
            
            # تعیین سطح ریسک
            route.risk_level = self._assess_risk_level(intent, route)
            
            # بررسی نیاز به تایید
            if safety_mode == "safe" and route.risk_level in [RiskLevel.POWER, RiskLevel.CRITICAL]:
                route.requires_consent = True
                route.consent_message = self._build_consent_message(intent, route)
            
            logger.debug(f"Routed to: {route}")
            return route
            
        except Exception as e:
            logger.exception(f"Routing failed: {e}")
            return Route(
                type=RouteType.CLARIFICATION_NEEDED,
                confidence=0.0,
                risk_level=RiskLevel.SAFE,
                consent_message=f"خطایی رخ داد: {str(e)}"
            )
    
    def _classify_intent(self, intent: Intent, safety_mode: str) -> Route:
        """تصنیف Intent به نوع مسیریابی
        
        Args:
            intent: Intent تجزیه‌شده
            safety_mode: حالت ایمنی
        
        Returns:
            Route: نتیجه تصنیف
        """
        verb = intent.verb.lower()
        target = intent.target.lower()
        
        # الگوهای وب
        web_verbs = ["search", "browse", "check", "find", "look", "visit", "go"]
        web_targets = ["web", "website", "google", "browser", "internet", "online"]
        
        if any(v in verb for v in web_verbs) or any(t in target for t in web_targets):
            return Route(
                type=RouteType.BROWSER_USE,
                requires_activation=["browser_use"],
                confidence=intent.confidence,
                risk_level=RiskLevel.POWER,
                metadata={"search_query": target, "action": verb}
            )
        
        # الگوهای اتوماسیون دسکتاپ
        desktop_verbs = ["open", "create", "type", "click", "delete", "move", "copy"]
        desktop_targets = ["file", "folder", "notepad", "desktop", "window", "app"]
        
        if any(v in verb for v in desktop_verbs) or any(t in target for t in desktop_targets):
            return Route(
                type=RouteType.DESKTOP_AUTOMATION,
                requires_activation=["desktop_automation"],
                confidence=intent.confidence,
                risk_level=RiskLevel.CRITICAL,
                metadata={"target_app": target, "action": verb}
            )
        
        # الگوهای عامل خودکار
        autonomous_verbs = ["goal", "accomplish", "complete", "do", "perform"]
        if any(v in verb for v in autonomous_verbs) and intent.parameters.get("complex"):
            return Route(
                type=RouteType.AUTONOMOUS_AGENT,
                requires_activation=["autonomous_agent"],
                confidence=intent.confidence,
                risk_level=RiskLevel.CRITICAL,
                metadata={"goal": intent.raw_request}
            )

        # الگوهای حالت تسک‌محور (Opt-in)
        task_verbs = ["task", "tasks", "todo", "prioritize", "queue", "assign", "schedule", "project"]
        task_targets = ["task", "todo", "project", "backlog", "list"]
        if any(v in verb for v in task_verbs) or any(t in target for t in task_targets):
            tasks = self._extract_tasks(intent.raw_request)
            return Route(
                type=RouteType.TASK_MODE,
                requires_activation=["task_mode"],
                confidence=intent.confidence,
                risk_level=RiskLevel.SAFE,
                metadata={"tasks": tasks, "tasks_count": len(tasks)}
            )
        
        # پیش‌فرض: پاسخ چت ساده
        return Route(
            type=RouteType.CHAT_RESPONSE,
            requires_activation=[],
            confidence=intent.confidence,
            risk_level=RiskLevel.SAFE,
            metadata={"response_type": "conversational"}
        )
    
    def _assess_risk_level(self, intent: Intent, route: Route) -> RiskLevel:
        """ارزیابی سطح ریسک برای یک درخواست
        
        Args:
            intent: Intent برای ارزیابی
            route: Route تعیین‌شده
        
        Returns:
            RiskLevel: سطح ریسک برای درخواست
        """
        if route.type == RouteType.CHAT_RESPONSE:
            return RiskLevel.SAFE
        
        risky_verbs = ["delete", "format", "uninstall", "shutdown", "restart", "kill", "remove"]
        risky_targets = ["system", "windows", "registry", "hard drive", "boot"]
        
        verb = intent.verb.lower()
        target = intent.target.lower()
        
        # CRITICAL: اقدامات بسیار حساس
        if any(v in verb for v in risky_verbs) or any(t in target for t in risky_targets):
            return RiskLevel.CRITICAL
        
        # POWER: اتوماسیون دسکتاپ و عامل خودکار
        if route.type in [RouteType.DESKTOP_AUTOMATION, RouteType.AUTONOMOUS_AGENT]:
            return RiskLevel.POWER
        
        # POWER: مرورگر (درخواست وب)
        if route.type == RouteType.BROWSER_USE:
            return RiskLevel.POWER
        
        # SAFE: پیش‌فرض
        return RiskLevel.SAFE
    
    def _is_risky(self, intent: Intent) -> bool:
        """بررسی درخواست برای ریسک بالا
        
        Args:
            intent: Intent برای بررسی
        
        Returns:
            bool: True اگر ریسک بالا
        """
        risky_verbs = ["delete", "format", "uninstall", "shutdown", "restart"]
        risky_targets = ["system", "windows", "registry", "hard drive"]
        
        verb = intent.verb.lower()
        target = intent.target.lower()
        
        return (
            any(v in verb for v in risky_verbs)
            or any(t in target for t in risky_targets)
        )
    
    def _build_consent_message(self, intent: Intent, route: Route) -> str:
        """ساخت پیام تایید برای درخواست‌های پرریسک
        
        Args:
            intent: Intent
            route: Route
        
        Returns:
            str: پیام تایید
        """
        return (
            f"⚠️ This request requires your confirmation:\n"
            f"Action: {intent.verb} → Target: {intent.target}\n"
            f"Do you approve? (yes/no)"
        )

    def _extract_tasks(self, raw_request: str) -> List[str]:
        """استخراج لیست تسک‌ها از متن خام کاربر.

        این تابع تلاش می‌کند تسک‌ها را با جداکننده‌های رایج (؛، ";", "\n") تشخیص دهد.
        در صورت عدم وجود جداکننده، کل متن را به‌عنوان یک تسک برمی‌گرداند.
        """
        # جداکننده‌های رایج تسک‌ها
        separators = [";", "\n", "،"]
        collected: List[str] = []
        working = raw_request

        for sep in separators:
            if sep in working:
                parts = [item.strip() for item in working.split(sep) if item.strip()]
                collected.extend(parts)
                break

        if not collected and working.strip():
            collected.append(working.strip())

        return collected
