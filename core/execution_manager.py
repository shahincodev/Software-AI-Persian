# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""مدیر اجرای اقدامات سیستمی با صف، اولویت، و مدیریت خطا.

این ماژول تمام اجزای سیستم اتوماسیون را به هم متصل می‌کند:
- اعتبارسنجی با SafetyFilter
- دریافت تایید از UserConsentManager
- اجرا با SystemToolAdapter
- لاگینگ و ممیزی
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections import deque
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from .safety_filter import SafetyFilter, UserConsentManager
from .system_actions import ActionResult, ActionStatus, SystemAction
from .system_tools import SystemToolAdapter

logger = logging.getLogger(__name__)


class ExecutionPriority(Enum):
    """اولویت اجرای اقدامات."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class QueuedAction:
    """یک اقدام در صف اجرا."""
    
    def __init__(
        self,
        action: SystemAction,
        priority: ExecutionPriority = ExecutionPriority.NORMAL,
    ):
        self.action = action
        self.priority = priority
        self.queued_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.result: Optional[ActionResult] = None
    
    def __lt__(self, other: QueuedAction) -> bool:
        """برای مقایسه در صف اولویت‌دار."""
        if self.priority.value != other.priority.value:
            return self.priority.value > other.priority.value  # اولویت بالاتر اول
        return self.queued_at < other.queued_at  # قدیمی‌تر اول


class ExecutionManager:
    """مدیر اجرای اقدامات سیستمی."""
    
    def __init__(
        self,
        safety_filter: Optional[SafetyFilter] = None,
        consent_manager: Optional[UserConsentManager] = None,
        adapter: Optional[SystemToolAdapter] = None,
        audit_log_path: Optional[Path] = None,
        max_concurrent: int = 3,
        dry_run: bool = False,
    ):
        """
        Args:
            safety_filter: فیلتر امنیتی (اگر None باشد، پیش‌فرض استفاده می‌شود)
            consent_manager: مدیر تایید کاربر
            adapter: آداپتور ابزارها
            audit_log_path: مسیر فایل لاگ ممیزی
            max_concurrent: حداکثر تعداد اقدامات همزمان
            dry_run: اگر True باشد، هیچ اقدامی واقعاً اجرا نمی‌شود
        """
        self.safety_filter = safety_filter or SafetyFilter()
        self.consent_manager = consent_manager or UserConsentManager()
        self.adapter = adapter or SystemToolAdapter(dry_run=dry_run)
        self.audit_log_path = audit_log_path or Path("data/logs/audit.jsonl")
        self.max_concurrent = max_concurrent
        self.dry_run = dry_run
        
        # صف اقدامات
        self.queue: deque[QueuedAction] = deque()
        self.executing: dict[str, QueuedAction] = {}  # action_id -> QueuedAction
        self.completed: dict[str, QueuedAction] = {}  # action_id -> QueuedAction
        
        # آمار
        self.stats = {
            "total_queued": 0,
            "total_executed": 0,
            "total_succeeded": 0,
            "total_failed": 0,
            "total_cancelled": 0,
        }
    
    def submit(
        self,
        action: SystemAction,
        priority: ExecutionPriority = ExecutionPriority.NORMAL,
    ) -> str:
        """افزودن اقدام به صف.
        
        Returns:
            action_id: شناسه اقدام برای پیگیری
        """
        queued_action = QueuedAction(action, priority)
        
        # مرتب‌سازی صف بر اساس اولویت
        # برای سادگی، از یک deque ساده استفاده می‌کنیم و در زمان اجرا مرتب می‌کنیم
        self.queue.append(queued_action)
        
        self.stats["total_queued"] += 1
        
        logger.info(
            "Action added to queue: %s (priority: %s)",
            action.action_id,
            priority.name,
        )
        
        return action.action_id
    
    def _sort_queue(self) -> None:
        """مرتب‌سازی صف بر اساس اولویت."""
        sorted_items = sorted(self.queue, reverse=True)
        self.queue.clear()
        self.queue.extend(sorted_items)
    
    async def execute_next(self) -> Optional[ActionResult]:
        """اجرای یک اقدام از صف.
        
        Returns:
            ActionResult اگر اقدامی اجرا شد، None اگر صف خالی بود
        """
        if not self.queue:
            return None
        
        # مرتب‌سازی برای گرفتن بالاترین اولویت
        self._sort_queue()
        
        queued_action = self.queue.popleft()
        action = queued_action.action
        
        queued_action.started_at = datetime.now()
        self.executing[action.action_id] = queued_action
        
        try:
            result = await self._execute_action(action)
            queued_action.result = result
            
            # آمارگیری
            self.stats["total_executed"] += 1
            if result.success:
                self.stats["total_succeeded"] += 1
            else:
                self.stats["total_failed"] += 1
            
            # لاگ ممیزی
            self._audit_log(action, result)
            
            return result
        
        except Exception as e:
            logger.exception("Unexpected error executing action %s", action.action_id)
            
            result = ActionResult(
                action_id=action.action_id,
                status=ActionStatus.FAILED,
                started_at=queued_action.started_at or datetime.now(),
                completed_at=datetime.now(),
                error=f"Internal error: {e}",
            )
            queued_action.result = result
            self.stats["total_failed"] += 1
            
            self._audit_log(action, result)
            
            return result
        
        finally:
            # انتقال از حال اجرا به تکمیل‌شده
            if action.action_id in self.executing:
                del self.executing[action.action_id]
            self.completed[action.action_id] = queued_action
    
    async def _execute_action(self, action: SystemAction) -> ActionResult:
        """اجرای یک اقدام با تمام بررسی‌ها.
        
        مراحل:
        1. اعتبارسنجی امنیتی
        2. درخواست تایید (در صورت نیاز)
        3. اجرای اقدام
        4. لاگینگ
        """
        started_at = datetime.now()
        
        # 1. بررسی امنیتی
        is_safe, reason, needs_consent = self.safety_filter.validate(action)
        
        if not is_safe:
            logger.warning("Action %s rejected: %s", action.action_id, reason)
            return ActionResult(
                action_id=action.action_id,
                status=ActionStatus.CANCELLED,
                started_at=started_at,
                completed_at=datetime.now(),
                error=f"Rejected by security filter: {reason}",
            )
        
        # 2. درخواست تایید
        if needs_consent:
            approved = self.consent_manager.request_consent(action, self.safety_filter)
            if not approved:
                logger.info("Action %s was rejected by the user", action.action_id)
                self.stats["total_cancelled"] += 1
                return ActionResult(
                    action_id=action.action_id,
                    status=ActionStatus.CANCELLED,
                    started_at=started_at,
                    completed_at=datetime.now(),
                    output="Cancelled by user",
                )
        
        # 3. اجرای اقدام
        logger.info("Starting execution of action: %s", action.describe())
        
        # اگر در حالت dry-run هستیم، علامت بزن
        if self.dry_run:
            action.dry_run = True
        
        # اجرا در یک thread جداگانه برای عملیات‌های سنگین
        result = await asyncio.to_thread(self.adapter.execute, action)
        
        logger.info(
            "Executing action %s: %s (duration: %.2f seconds)",
            action.action_id,
            result.status.value,
            result.duration or 0,
        )
        
        return result
    
    async def execute_all(self, wait_between: float = 0.1) -> list[ActionResult]:
        """اجرای تمام اقدامات در صف.
        
        Args:
            wait_between: فاصله زمانی بین اجراها به ثانیه
        
        Returns:
            لیست نتایج
        """
        results = []
        
        while self.queue or self.executing:
            # اجرای اقدامات تا حد max_concurrent
            while len(self.executing) < self.max_concurrent and self.queue:
                result = await self.execute_next()
                if result:
                    results.append(result)
            
            # صبر کوتاه
            if wait_between > 0:
                await asyncio.sleep(wait_between)
        
        logger.info("All actions executed: %d results", len(results))
        return results
    
    def _audit_log(self, action: SystemAction, result: ActionResult) -> None:
        """ثبت لاگ ممیزی."""
        try:
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action.to_dict(),
                "result": {
                    "action_id": result.action_id,
                    "status": result.status.value,
                    "duration": result.duration,
                    "output": result.output[:500] if result.output else None,  # محدود کردن
                    "error": result.error,
                },
            }
            
            # افزودن به فایل JSONL (هر خط یک JSON)
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        except Exception as e:
            logger.exception("Error writing audit log: %s", e)
    
    def get_status(self, action_id: str) -> Optional[dict[str, Any]]:
        """دریافت وضعیت یک اقدام."""
        # جستجو در صف
        for qa in self.queue:
            if qa.action.action_id == action_id:
                return {
                    "status": "queued",
                    "priority": qa.priority.name,
                    "queued_at": qa.queued_at.isoformat(),
                }
        
        # جستجو در حال اجرا
        if action_id in self.executing:
            qa = self.executing[action_id]
            return {
                "status": "executing",
                "started_at": qa.started_at.isoformat() if qa.started_at else None,
            }
        
        # جستجو در تکمیل‌شده
        if action_id in self.completed:
            qa = self.completed[action_id]
            return {
                "status": "completed",
                "result": qa.result.status.value if qa.result else "unknown",
                "started_at": qa.started_at.isoformat() if qa.started_at else None,
                "duration": qa.result.duration if qa.result else None,
            }
        
        return None
    
    def get_stats(self) -> dict[str, Any]:
        """دریافت آمار اجرا."""
        return {
            **self.stats,
            "queue_size": len(self.queue),
            "executing_count": len(self.executing),
            "completed_count": len(self.completed),
        }
    
    def clear_completed(self) -> int:
        """پاک کردن اقدامات تکمیل‌شده از حافظه.
        
        Returns:
            تعداد اقدامات پاک‌شده
        """
        count = len(self.completed)
        self.completed.clear()
        logger.info("Memory cleared: %d completed actions removed", count)
        return count


__all__ = ["ExecutionManager", "ExecutionPriority", "QueuedAction"]
