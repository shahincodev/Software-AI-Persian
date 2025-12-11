# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""سیستم بازیابی خودکار (Action Recovery).

این ماژول مسئول بازیابی خودکار در صورت بروز خطا در اجرای اقدامات است.
هدف: Retry هوشمند، Rollback، و گزارش‌دهی دقیق خطاها.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class RecoveryStrategy(Enum):
    """استراتژی‌های بازیابی.
    
    - RETRY: تلاش مجدد
    - RETRY_WITH_DELAY: تلاش مجدد با تأخیر
    - ROLLBACK: بازگشت به حالت قبل
    - SKIP: رد شدن از اقدام
    - ABORT: توقف کامل
    """
    RETRY = "retry"
    RETRY_WITH_DELAY = "retry_with_delay"
    ROLLBACK = "rollback"
    SKIP = "skip"
    ABORT = "abort"


class ErrorSeverity(Enum):
    """شدت خطا.
    
    - LOW: خطای کم‌اهمیت (می‌توان نادیده گرفت)
    - MEDIUM: خطای متوسط (نیاز به retry)
    - HIGH: خطای شدید (نیاز به rollback)
    - CRITICAL: خطای بحرانی (نیاز به abort)
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RecoveryConfig:
    """پیکربندی سیستم بازیابی.
    
    Attributes:
        max_retries: حداکثر تعداد تلاش مجدد
        retry_delay: تأخیر بین تلاش‌ها (ثانیه)
        exponential_backoff: استفاده از تأخیر تصاعدی
        enable_rollback: فعال‌سازی rollback خودکار
        log_errors: ثبت خطاها در log
    """
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    enable_rollback: bool = True
    log_errors: bool = True
    timeout: float = 30.0  # timeout برای هر اقدام (ثانیه)


@dataclass
class ActionResult:
    """نتیجه اجرای یک اقدام.
    
    Attributes:
        success: موفقیت‌آمیز بودن اقدام
        action: اقدام اجرا شده
        error: خطای رخ داده (در صورت وجود)
        attempts: تعداد تلاش‌ها
        duration: مدت زمان اجرا (ثانیه)
        recovery_strategy: استراتژی بازیابی استفاده شده
    """
    success: bool
    action: dict[str, Any]
    error: Optional[str] = None
    attempts: int = 1
    duration: float = 0.0
    recovery_strategy: Optional[RecoveryStrategy] = None
    rollback_actions: list[dict[str, Any]] = field(default_factory=list)


class ActionRecovery:
    """سیستم بازیابی خودکار برای اقدامات.
    
    این کلاس مسئولیت‌های زیر را بر عهده دارد:
    - Retry هوشمند با exponential backoff
    - Rollback خودکار در صورت خطا
    - تشخیص نوع خطا و انتخاب استراتژی مناسب
    - گزارش‌دهی دقیق از خطاها و بازیابی‌ها
    
    Example:
        >>> config = RecoveryConfig(max_retries=3, retry_delay=1.0)
        >>> recovery = ActionRecovery(config)
        >>> 
        >>> async def risky_action():
        ...     # کاری که ممکن است خطا دهد
        ...     return True
        >>> 
        >>> result = await recovery.execute_with_recovery(
        ...     risky_action,
        ...     action={"type": "LaunchApp", "params": {"app_name": "app.exe"}}
        ... )
        >>> print(result.success)  # True یا False
    """
    
    def __init__(self, config: Optional[RecoveryConfig] = None):
        """مقداردهی اولیه سیستم بازیابی.
        
        Args:
            config: پیکربندی بازیابی (در صورت عدم ارائه، پیش‌فرض استفاده می‌شود)
        """
        self.config = config or RecoveryConfig()
        self._history: list[ActionResult] = []
        self._rollback_stack: list[dict[str, Any]] = []
    
    async def execute_with_recovery(
        self,
        action_func: Callable,
        action: dict[str, Any],
        rollback_func: Optional[Callable] = None,
    ) -> ActionResult:
        """اجرای اقدام با بازیابی خودکار.
        
        Args:
            action_func: تابعی که اقدام را اجرا می‌کند
            action: اقدام مورد نظر (dict)
            rollback_func: تابع rollback (اختیاری)
        
        Returns:
            ActionResult: نتیجه اجرا
        
        Example:
            >>> async def launch_app():
            ...     # کد اجرای برنامه
            ...     return True
            >>> 
            >>> async def close_app():
            ...     # کد بستن برنامه (rollback)
            ...     return True
            >>> 
            >>> result = await recovery.execute_with_recovery(
            ...     launch_app,
            ...     action={"type": "LaunchApp", "params": {"app_name": "notepad.exe"}},
            ...     rollback_func=close_app
            ... )
        """
        start_time = time.time()
        attempts = 0
        last_error = None
        
        logger.info(f"🚀 Executing action: {action.get('type', 'Unknown')}")
        
        for attempt in range(1, self.config.max_retries + 1):
            attempts = attempt
            
            try:
                logger.debug(f"Attempt {attempt}/{self.config.max_retries}")
                
                # اجرای اقدام با timeout
                result = await asyncio.wait_for(
                    action_func(),
                    timeout=self.config.timeout
                )
                
                # موفقیت
                duration = time.time() - start_time
                logger.info(f"✅ Action succeeded on attempt {attempt} (took {duration:.2f}s)")
                
                action_result = ActionResult(
                    success=True,
                    action=action,
                    attempts=attempts,
                    duration=duration,
                )
                
                self._history.append(action_result)
                return action_result
            
            except asyncio.TimeoutError as e:
                last_error = f"Timeout after {self.config.timeout}s"
                logger.warning(f"⏱️ Action timed out on attempt {attempt}")
                
                # تعیین استراتژی بازیابی
                severity = self._classify_error(e)
                strategy = self._choose_strategy(severity, attempt)
                
                if strategy == RecoveryStrategy.ABORT:
                    logger.error("💥 Aborting due to timeout")
                    break
                
                # تأخیر قبل از retry
                if attempt < self.config.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.info(f"⏳ Waiting {delay:.1f}s before retry...")
                    await asyncio.sleep(delay)
            
            except Exception as e:
                last_error = str(e)
                logger.warning(f"❌ Action failed on attempt {attempt}: {e}")
                
                # تعیین استراتژی بازیابی
                severity = self._classify_error(e)
                strategy = self._choose_strategy(severity, attempt)
                
                logger.info(f"🔧 Recovery strategy: {strategy.value}")
                
                if strategy == RecoveryStrategy.ABORT:
                    logger.error("💥 Aborting due to critical error")
                    break
                
                elif strategy == RecoveryStrategy.ROLLBACK:
                    if self.config.enable_rollback and rollback_func:
                        logger.info("⏪ Attempting rollback...")
                        await self._execute_rollback(rollback_func)
                    break
                
                elif strategy == RecoveryStrategy.SKIP:
                    logger.info("⏭️ Skipping action")
                    break
                
                # RETRY یا RETRY_WITH_DELAY
                if attempt < self.config.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.info(f"⏳ Waiting {delay:.1f}s before retry...")
                    await asyncio.sleep(delay)
        
        # همه تلاش‌ها فیل شد
        duration = time.time() - start_time
        logger.error(
            f"💥 Action failed after {attempts} attempts "
            f"(took {duration:.2f}s): {last_error}"
        )
        
        action_result = ActionResult(
            success=False,
            action=action,
            error=last_error,
            attempts=attempts,
            duration=duration,
        )
        
        self._history.append(action_result)
        return action_result
    
    def _classify_error(self, error: Exception) -> ErrorSeverity:
        """تشخیص شدت خطا.
        
        Args:
            error: خطای رخ داده
        
        Returns:
            ErrorSeverity: شدت خطا
        """
        error_str = str(error).lower()
        
        # خطاهای بحرانی
        critical_keywords = [
            "permission denied",
            "access denied",
            "system error",
            "fatal error",
        ]
        
        for keyword in critical_keywords:
            if keyword in error_str:
                return ErrorSeverity.CRITICAL
        
        # خطاهای شدید
        high_keywords = [
            "file not found",
            "invalid path",
            "process not found",
        ]
        
        for keyword in high_keywords:
            if keyword in error_str:
                return ErrorSeverity.HIGH
        
        # خطاهای متوسط
        medium_keywords = [
            "timeout",
            "connection",
            "network",
        ]
        
        for keyword in medium_keywords:
            if keyword in error_str:
                return ErrorSeverity.MEDIUM
        
        # پیش‌فرض: خطای کم‌اهمیت
        return ErrorSeverity.LOW
    
    def _choose_strategy(
        self,
        severity: ErrorSeverity,
        attempt: int
    ) -> RecoveryStrategy:
        """انتخاب استراتژی بازیابی بر اساس شدت خطا.
        
        Args:
            severity: شدت خطا
            attempt: شماره تلاش فعلی
        
        Returns:
            RecoveryStrategy: استراتژی مناسب
        """
        # خطای بحرانی: توقف کامل
        if severity == ErrorSeverity.CRITICAL:
            return RecoveryStrategy.ABORT
        
        # خطای شدید: rollback
        if severity == ErrorSeverity.HIGH:
            if self.config.enable_rollback:
                return RecoveryStrategy.ROLLBACK
            return RecoveryStrategy.ABORT
        
        # خطای متوسط: retry با تأخیر
        if severity == ErrorSeverity.MEDIUM:
            if attempt >= self.config.max_retries:
                return RecoveryStrategy.SKIP
            return RecoveryStrategy.RETRY_WITH_DELAY
        
        # خطای کم‌اهمیت: retry فوری
        if attempt >= self.config.max_retries:
            return RecoveryStrategy.SKIP
        return RecoveryStrategy.RETRY
    
    def _calculate_delay(self, attempt: int) -> float:
        """محاسبه تأخیر قبل از retry.
        
        Args:
            attempt: شماره تلاش فعلی
        
        Returns:
            float: تأخیر (ثانیه)
        """
        if self.config.exponential_backoff:
            # Exponential backoff: 1s, 2s, 4s, 8s, ...
            return self.config.retry_delay * (2 ** (attempt - 1))
        else:
            # تأخیر ثابت
            return self.config.retry_delay
    
    async def _execute_rollback(self, rollback_func: Callable) -> bool:
        """اجرای rollback.
        
        Args:
            rollback_func: تابع rollback
        
        Returns:
            bool: موفقیت‌آمیز بودن rollback
        """
        try:
            logger.info("⏪ Executing rollback...")
            await rollback_func()
            logger.info("✅ Rollback succeeded")
            return True
        
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
    
    def get_history(self) -> list[ActionResult]:
        """دریافت تاریخچه اجراها.
        
        Returns:
            list[ActionResult]: لیست نتایج اجراها
        
        Example:
            >>> history = recovery.get_history()
            >>> for result in history:
            ...     print(f"{result.action['type']}: {result.success}")
        """
        return self._history.copy()
    
    def get_statistics(self) -> dict[str, Any]:
        """دریافت آمار اجراها.
        
        Returns:
            dict: آمار کلی
                - total: تعداد کل اجراها
                - successful: تعداد موفق
                - failed: تعداد ناموفق
                - avg_attempts: میانگین تلاش‌ها
                - avg_duration: میانگین مدت زمان
        
        Example:
            >>> stats = recovery.get_statistics()
            >>> print(f"Success rate: {stats['successful']}/{stats['total']}")
        """
        if not self._history:
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "avg_attempts": 0.0,
                "avg_duration": 0.0,
            }
        
        total = len(self._history)
        successful = sum(1 for r in self._history if r.success)
        failed = total - successful
        avg_attempts = sum(r.attempts for r in self._history) / total
        avg_duration = sum(r.duration for r in self._history) / total
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful / total * 100):.1f}%",
            "avg_attempts": round(avg_attempts, 2),
            "avg_duration": round(avg_duration, 2),
        }
    
    def clear_history(self) -> None:
        """پاک کردن تاریخچه اجراها."""
        self._history.clear()
        logger.info("🗑️ History cleared")
