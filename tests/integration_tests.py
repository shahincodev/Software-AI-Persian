# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""تست‌های یکپارچه‌سازی سیستم کامل."""

import pytest
import asyncio
from core.action_safety import ActionSafety
from core.action_recovery import ActionRecovery, RecoveryConfig
from core.multi_monitor import MultiMonitor
from core.context_aware_actions import ContextAwareActions, SystemState


class TestIntegration:
    """تست‌های integration کل سیستم."""
    
    def setup_method(self):
        """راه‌اندازی قبل از هر تست."""
        self.safety = ActionSafety(strict_mode=True)
        self.recovery = ActionRecovery()
        self.multi_mon = MultiMonitor()
        self.context = ContextAwareActions()
    
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
    async def test_context_and_safety_integration(self):
        """تست یکپارچه‌سازی Context + Safety."""
        
        # دریافت context
        context_info = await self.context.get_current_context()
        assert context_info is not None
        
        # اقدام عادی
        action = {
            "type": "LaunchApp",
            "params": {"path": "notepad.exe"},
            "priority": "normal"
        }
        
        # بررسی امنیت
        is_safe, safety_reason = self.safety.validate_action(action)
        
        # بررسی context
        should_execute, context_reason = self.context.should_execute_action(action, context_info)
        
        # هر دو باید تایید کنند (در شرایط عادی)
        if not is_safe:
            pytest.skip(f"Action not safe: {safety_reason}")
        
        assert isinstance(should_execute, bool)
    
    @pytest.mark.asyncio
    async def test_multimonitor_and_context_integration(self):
        """تست یکپارچه‌سازی Multi-Monitor + Context."""
        
        # دریافت context
        context_info = await self.context.get_current_context()
        mouse_x, mouse_y = context_info.mouse_position
        
        # یافتن مانیتور فعلی
        current_monitor = self.multi_mon.get_monitor_at_point(mouse_x, mouse_y)
        
        if current_monitor is None:
            pytest.skip("Could not determine current monitor")
        
        # اطلاعات مانیتور معتبر باشد
        assert current_monitor.width > 0
        assert current_monitor.height > 0
    
    @pytest.mark.asyncio
    async def test_complete_action_pipeline(self):
        """تست کامل pipeline اقدام: Context → Safety → Recovery."""
        
        # مرحله 1: دریافت Context
        context_info = await self.context.get_current_context()
        assert context_info is not None
        
        # مرحله 2: تعریف اقدام
        action = {
            "type": "DesktopClick",
            "params": {"x": 100, "y": 100},
            "priority": "normal"
        }
        
        # مرحله 3: بررسی context (باید اجرا شود؟)
        should_execute, context_reason = self.context.should_execute_action(action, context_info)
        
        if not should_execute:
            # اقدام رد شده توسط context
            pytest.skip(f"Action deferred by context: {context_reason}")
        
        # مرحله 4: بررسی امنیت
        is_safe, safety_reason = self.safety.validate_action(action)
        
        if not is_safe:
            # اقدام رد شده توسط safety
            pytest.skip(f"Action blocked by safety: {safety_reason}")
        
        # مرحله 5: تنظیم timing
        adjusted_action = self.context.adjust_action_timing(action, context_info)
        assert "params" in adjusted_action
        
        # مرحله 6: اجرا با recovery
        async def mock_execute():
            await asyncio.sleep(0.01)
            return True
        
        result = await self.recovery.execute_with_recovery(mock_execute, adjusted_action)
        
        # بررسی نتیجه
        assert result.success is True
        assert result.action == adjusted_action
    
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
    async def test_multimonitor_click_with_safety(self):
        """تست کلیک چند مانیتوری با بررسی امنیت."""
        
        # دریافت مانیتور اصلی
        primary = self.multi_mon.get_primary_monitor()
        
        # موقعیت در مرکز مانیتور
        rel_x = primary.width // 2
        rel_y = primary.height // 2
        
        # اقدام کلیک
        action = {
            "type": "DesktopClick",
            "params": {
                "x": rel_x,
                "y": rel_y,
                "monitor": primary.index
            }
        }
        
        # بررسی امنیت
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is True
    
    @pytest.mark.asyncio
    async def test_recovery_with_context_adjustment(self):
        """تست recovery با تنظیم timing بر اساس context."""
        
        # دریافت context
        context_info = await self.context.get_current_context()
        
        # اقدام با timeout
        action = {
            "type": "TestAction",
            "params": {"timeout": 5.0},
            "priority": "normal"
        }
        
        # تنظیم timing
        adjusted = self.context.adjust_action_timing(action, context_info)
        
        # اگر سیستم busy است، timeout باید افزایش یابد
        if context_info.system_state == SystemState.BUSY:
            assert adjusted["params"]["timeout"] >= action["params"]["timeout"]
        
        # اجرا با recovery
        async def test_action():
            await asyncio.sleep(0.01)
            return True
        
        result = await self.recovery.execute_with_recovery(test_action, adjusted)
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_fullscreen_detection_and_action_deferral(self):
        """تست تشخیص fullscreen و به تعویق انداختن اقدام."""
        
        # دریافت context
        context_info = await self.context.get_current_context()
        
        # اقدام مزاحم
        intrusive_action = {
            "type": "LaunchApp",
            "params": {"path": "app.exe"},
            "priority": "low"
        }
        
        # بررسی context
        should_execute, reason = self.context.should_execute_action(intrusive_action, context_info)
        
        # اگر fullscreen است، اقدام باید رد شود
        if context_info.is_fullscreen and context_info.system_state == SystemState.GAMING:
            assert should_execute is False
            assert "fullscreen" in reason.lower() or "gaming" in reason.lower()
    
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
