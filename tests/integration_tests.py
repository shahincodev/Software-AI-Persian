# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""تست‌های یکپارچه‌سازی سیستم کامل."""

import pytest
from core.action_safety import ActionSafety
from core.action_recovery import ActionRecovery


class TestIntegration:
    """تست‌های integration کل سیستم."""
    
    def setup_method(self):
        """راه‌اندازی قبل از هر تست."""
        self.safety = ActionSafety(strict_mode=True)
        self.recovery = ActionRecovery()
    
    @pytest.mark.asyncio
    async def test_safety_and_recovery_integration(self):
        """تست یکپارچه‌سازی Safety + Recovery."""
        
        # اقدام امن
        safe_action = {
            "type": "DeleteFile",
            "params": {"path": "temp_test.txt"}
        }
        
        # بررسی امنیت
        is_safe, reason = self.safety.validate_action(safe_action)
        assert is_safe is True
        
        # اجرا با recovery
        async def safe_delete():
            return True
        
        result = await self.recovery.execute_with_recovery(safe_delete, safe_action)
        assert result.success is True
        assert result.attempts == 1
    
    @pytest.mark.asyncio
    async def test_unsafe_action_blocked(self):
        """تست مسدود شدن اقدام ناامن."""
        
        # اقدام خطرناک
        unsafe_action = {
            "type": "DeleteFile",
            "params": {"path": "C:/Windows/System32/kernel32.dll"}
        }
        
        # بررسی امنیت
        is_safe, reason = self.safety.validate_action(unsafe_action)
        assert is_safe is False
        assert "system" in reason.lower()
        
        # نباید اجرا شود
        # در سیستم واقعی، pipeline باید از اجرا جلوگیری کند
    
    @pytest.mark.asyncio
    async def test_batch_actions_with_safety(self):
        """تست اجرای دسته‌ای اقدامات با بررسی امنیت."""
        
        actions = [
            {"type": "DesktopClick", "params": {"x": 100, "y": 100}},
            {"type": "LaunchApp", "params": {"path": "notepad.exe"}},
            {"type": "DeleteFile", "params": {"path": "temp.txt"}},
        ]
        
        # بررسی امنیت دسته‌ای
        results = self.safety.validate_batch(actions)
        
        assert len(results) == len(actions)
        
        # فیلتر اقدامات امن
        safe_actions = [
            action for action, (is_safe, _) in zip(actions, results) if is_safe
        ]
        
        # حداقل یک اقدام امن باید باشد
        assert len(safe_actions) > 0
    
    @pytest.mark.asyncio
    async def test_error_recovery_with_safety_validation(self):
        """تست recovery خطا با اعتبارسنجی مجدد امنیت."""
        
        action = {
            "type": "DeleteFile",
            "params": {"path": "test_file.txt"}
        }
        
        # بررسی امنیت اولیه
        is_safe, reason = self.safety.validate_action(action)
        
        if not is_safe:
            pytest.skip(f"Action not safe: {reason}")
        
        # شبیه‌سازی اجرا با خطا
        attempt_count = 0
        
        async def failing_action():
            nonlocal attempt_count
            attempt_count += 1
            
            if attempt_count < 2:
                raise Exception("Temporary failure")
            
            # قبل از اجرای موفق، دوباره امنیت بررسی شود
            is_safe_retry, _ = self.safety.validate_action(action)
            if not is_safe_retry:
                raise Exception("Action became unsafe")
            
            return True
        
        result = await self.recovery.execute_with_recovery(failing_action, action)
        assert result.success is True
        assert result.attempts == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
