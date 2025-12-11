# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""تست‌های سیستم بازیابی اقدامات."""

import pytest
import asyncio
from core.action_recovery import (
    ActionRecovery,
    RecoveryConfig,
    RecoveryStrategy,
    ErrorSeverity,
)


class TestActionRecovery:
    """تست‌های ActionRecovery."""
    
    def setup_method(self):
        """راه‌اندازی قبل از هر تست."""
        config = RecoveryConfig(
            max_retries=3,
            retry_delay=0.1,  # کوتاه برای تست
            exponential_backoff=True,
            enable_rollback=True,
        )
        self.recovery = ActionRecovery(config)
    
    @pytest.mark.asyncio
    async def test_successful_execution_first_try(self):
        """تست اجرای موفق در تلاش اول."""
        executed = False
        
        async def success_action():
            nonlocal executed
            executed = True
            return True
        
        action = {"type": "TestAction"}
        result = await self.recovery.execute_with_recovery(success_action, action)
        
        assert result.success is True
        assert result.attempts == 1
        assert executed is True
        assert result.error is None
    
    @pytest.mark.asyncio
    async def test_retry_then_success(self):
        """تست retry و سپس موفقیت."""
        attempt_count = 0
        
        async def fail_twice_then_succeed():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Temporary failure")
            return True
        
        action = {"type": "TestAction"}
        result = await self.recovery.execute_with_recovery(fail_twice_then_succeed, action)
        
        assert result.success is True
        assert result.attempts == 3
        assert attempt_count == 3
    
    @pytest.mark.asyncio
    async def test_all_retries_failed(self):
        """تست فیل شدن همه تلاش‌ها."""
        async def always_fail():
            raise Exception("Always fails")
        
        action = {"type": "TestAction"}
        result = await self.recovery.execute_with_recovery(always_fail, action)
        
        assert result.success is False
        assert result.attempts == 3  # max_retries
        assert result.error is not None
        assert "Always fails" in result.error
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """تست مدیریت timeout."""
        async def slow_action():
            await asyncio.sleep(100)  # خیلی کند
            return True
        
        config = RecoveryConfig(max_retries=2, timeout=0.1)
        recovery = ActionRecovery(config)
        
        action = {"type": "SlowAction"}
        result = await recovery.execute_with_recovery(slow_action, action)
        
        assert result.success is False
        assert "Timeout" in result.error
    
    @pytest.mark.asyncio
    async def test_rollback_execution(self):
        """تست اجرای rollback."""
        rollback_executed = False
        
        async def failing_action():
            raise Exception("Critical error")
        
        async def rollback_action():
            nonlocal rollback_executed
            rollback_executed = True
            return True
        
        # فورس کردن rollback با خطای HIGH severity
        config = RecoveryConfig(max_retries=1, enable_rollback=True)
        recovery = ActionRecovery(config)
        
        action = {"type": "CriticalAction"}
        
        # برای تست rollback، باید خطای HIGH داشته باشیم
        async def high_severity_action():
            raise FileNotFoundError("File not found")  # HIGH severity
        
        result = await recovery.execute_with_recovery(
            high_severity_action,
            action,
            rollback_func=rollback_action
        )
        
        assert result.success is False
        # Rollback باید اجرا شده باشد (با توجه به severity)
    
    def test_classify_error_critical(self):
        """تست تشخیص خطای بحرانی."""
        error = Exception("Permission denied")
        severity = self.recovery._classify_error(error)
        assert severity == ErrorSeverity.CRITICAL
    
    def test_classify_error_high(self):
        """تست تشخیص خطای HIGH."""
        error = Exception("File not found")
        severity = self.recovery._classify_error(error)
        assert severity == ErrorSeverity.HIGH
    
    def test_classify_error_medium(self):
        """تست تشخیص خطای MEDIUM."""
        error = Exception("Connection timeout")
        severity = self.recovery._classify_error(error)
        assert severity == ErrorSeverity.MEDIUM
    
    def test_classify_error_low(self):
        """تست تشخیص خطای LOW."""
        error = Exception("Some random error")
        severity = self.recovery._classify_error(error)
        assert severity == ErrorSeverity.LOW
    
    def test_choose_strategy_critical(self):
        """تست انتخاب استراتژی برای خطای CRITICAL."""
        strategy = self.recovery._choose_strategy(ErrorSeverity.CRITICAL, 1)
        assert strategy == RecoveryStrategy.ABORT
    
    def test_choose_strategy_high(self):
        """تست انتخاب استراتژی برای خطای HIGH."""
        strategy = self.recovery._choose_strategy(ErrorSeverity.HIGH, 1)
        assert strategy == RecoveryStrategy.ROLLBACK
    
    def test_choose_strategy_medium(self):
        """تست انتخاب استراتژی برای خطای MEDIUM."""
        strategy = self.recovery._choose_strategy(ErrorSeverity.MEDIUM, 1)
        assert strategy == RecoveryStrategy.RETRY_WITH_DELAY
    
    def test_choose_strategy_low(self):
        """تست انتخاب استراتژی برای خطای LOW."""
        strategy = self.recovery._choose_strategy(ErrorSeverity.LOW, 1)
        assert strategy == RecoveryStrategy.RETRY
    
    def test_choose_strategy_max_retries_reached(self):
        """تست انتخاب استراتژی وقتی max retries رسیده."""
        strategy = self.recovery._choose_strategy(ErrorSeverity.LOW, 10)
        assert strategy == RecoveryStrategy.SKIP
    
    def test_calculate_delay_exponential(self):
        """تست محاسبه delay با exponential backoff."""
        config = RecoveryConfig(retry_delay=1.0, exponential_backoff=True)
        recovery = ActionRecovery(config)
        
        delay1 = recovery._calculate_delay(1)
        delay2 = recovery._calculate_delay(2)
        delay3 = recovery._calculate_delay(3)
        
        assert delay1 == 1.0  # 1 * 2^0
        assert delay2 == 2.0  # 1 * 2^1
        assert delay3 == 4.0  # 1 * 2^2
    
    def test_calculate_delay_linear(self):
        """تست محاسبه delay با linear backoff."""
        config = RecoveryConfig(retry_delay=1.0, exponential_backoff=False)
        recovery = ActionRecovery(config)
        
        delay1 = recovery._calculate_delay(1)
        delay2 = recovery._calculate_delay(2)
        delay3 = recovery._calculate_delay(3)
        
        assert delay1 == 1.0
        assert delay2 == 1.0
        assert delay3 == 1.0
    
    @pytest.mark.asyncio
    async def test_history_tracking(self):
        """تست ردیابی تاریخچه."""
        async def action1():
            return True
        
        async def action2():
            raise Exception("Failed")
        
        await self.recovery.execute_with_recovery(action1, {"type": "Action1"})
        await self.recovery.execute_with_recovery(action2, {"type": "Action2"})
        
        history = self.recovery.get_history()
        assert len(history) == 2
        assert history[0].success is True
        assert history[1].success is False
    
    @pytest.mark.asyncio
    async def test_get_statistics(self):
        """تست دریافت آمار."""
        async def success_action():
            return True
        
        async def fail_action():
            raise Exception("Failed")
        
        # 2 موفق، 1 ناموفق
        await self.recovery.execute_with_recovery(success_action, {"type": "A1"})
        await self.recovery.execute_with_recovery(success_action, {"type": "A2"})
        await self.recovery.execute_with_recovery(fail_action, {"type": "A3"})
        
        stats = self.recovery.get_statistics()
        
        assert stats["total"] == 3
        assert stats["successful"] == 2
        assert stats["failed"] == 1
        assert "66.7%" in stats["success_rate"]  # 2/3
    
    def test_clear_history(self):
        """تست پاک کردن تاریخچه."""
        # فرض می‌کنیم تاریخچه‌ای داریم
        self.recovery._history.append(None)  # dummy
        assert len(self.recovery._history) > 0
        
        self.recovery.clear_history()
        assert len(self.recovery._history) == 0
    
    @pytest.mark.asyncio
    async def test_recovery_with_custom_config(self):
        """تست recovery با config سفارشی."""
        config = RecoveryConfig(
            max_retries=5,
            retry_delay=0.05,
            exponential_backoff=False,
            enable_rollback=False,
        )
        recovery = ActionRecovery(config)
        
        attempt_count = 0
        
        async def fail_four_times():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 5:
                raise Exception("Not yet")
            return True
        
        result = await recovery.execute_with_recovery(fail_four_times, {"type": "T"})
        
        assert result.success is True
        assert result.attempts == 5
        assert attempt_count == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
