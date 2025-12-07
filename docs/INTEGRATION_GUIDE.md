# راهنمای یکپارچه‌سازی کامل سیستم

## نمای کلی

این راهنما نحوه استفاده ترکیبی از تمام ماژول‌های پیشرفته را توضیح می‌دهد. شما یاد می‌گیرید چگونه Safety، Recovery، Multi-Monitor و Context-Aware را با هم ترکیب کنید تا یک سیستم اتوماسیون قوی و هوشمند بسازید.

## معماری سیستم

```
┌─────────────────────────────────────────┐
│         User Request / Task             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│      Context-Aware Actions               │
│  (Should execute? When? How?)            │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│         Action Safety                    │
│    (Is it safe? Block dangerous?)        │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│      Multi-Monitor Support               │
│   (Which monitor? Coordinate convert?)   │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│       Action Recovery                    │
│   (Execute with retry/rollback)          │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│      Actual Execution                    │
│   (Mouse, Keyboard, Desktop, etc.)       │
└──────────────────────────────────────────┘
```

## Pipeline کامل

### مرحله 1: راه‌اندازی

```python
from core import (
    ContextAwareActions,
    ActionSafety,
    MultiMonitor,
    ActionRecovery,
    RecoveryConfig,
    MouseControl,
    DesktopActions,
)

# ایجاد تمام سیستم‌ها
context = ContextAwareActions()
safety = ActionSafety(strict_mode=True)
multi_mon = MultiMonitor()
recovery = ActionRecovery(
    RecoveryConfig(
        max_retries=3,
        retry_delay=1.0,
        exponential_backoff=True,
        enable_rollback=True,
        timeout=30.0
    )
)

# ابزارهای اجرا
mouse = MouseControl()
desktop = DesktopActions()
```

### مرحله 2: تعریف Pipeline

```python
async def execute_smart_action(action: dict):
    """Pipeline کامل برای اجرای هوشمند اقدام."""
    
    # 1. دریافت Context
    ctx = await context.get_current_context()
    print(f"Context: {ctx.system_state.name}, {ctx.app_category.name}")
    
    # 2. بررسی Context (باید اجرا شود؟)
    should_run, ctx_reason = context.should_execute_action(action, ctx)
    
    if not should_run:
        # منتظر زمان مناسب
        print(f"Waiting: {ctx_reason}")
        success = await context.wait_for_appropriate_time(
            action,
            max_wait=120.0,
            check_interval=3.0
        )
        
        if not success:
            return {
                "success": False,
                "reason": "Context never became appropriate",
                "blocked_by": "context"
            }
        
        # دریافت context جدید
        ctx = await context.get_current_context()
    
    # 3. بررسی Safety
    is_safe, safety_reason = safety.validate_action(action)
    
    if not is_safe:
        return {
            "success": False,
            "reason": safety_reason,
            "blocked_by": "safety"
        }
    
    # 4. تنظیم Timing بر اساس Context
    adjusted_action = context.adjust_action_timing(action, ctx)
    
    # 5. پردازش Multi-Monitor (اگر لازم است)
    if action.get("type") in ["DesktopClick", "DesktopMove"]:
        monitor_idx = action.get("monitor", 0)
        monitor = multi_mon.get_monitor_by_index(monitor_idx)
        
        if monitor:
            # تبدیل مختصات
            x = adjusted_action["params"]["x"]
            y = adjusted_action["params"]["y"]
            
            abs_x = monitor.x + x
            abs_y = monitor.y + y
            
            adjusted_action["params"]["x"] = abs_x
            adjusted_action["params"]["y"] = abs_y
    
    # 6. اجرا با Recovery
    async def execute():
        action_type = adjusted_action["type"]
        params = adjusted_action["params"]
        
        if action_type == "DesktopClick":
            mouse.click(params["x"], params["y"], params.get("button", "left"))
        elif action_type == "LaunchApp":
            desktop.launch_app(params["path"])
        # ... سایر اقدامات
        
        return True
    
    result = await recovery.execute_with_recovery(execute, adjusted_action)
    
    # 7. بازگشت نتیجه
    return {
        "success": result.success,
        "attempts": result.attempts,
        "duration": result.duration,
        "error": result.error,
        "strategy": result.recovery_strategy.name if result.recovery_strategy else None
    }
```

### مرحله 3: استفاده

```python
# تعریف اقدام
action = {
    "type": "DesktopClick",
    "params": {
        "x": 500,
        "y": 300,
        "button": "left"
    },
    "priority": "normal",
    "monitor": 0
}

# اجرا
result = await execute_smart_action(action)

if result["success"]:
    print(f"✓ موفق بعد از {result['attempts']} تلاش در {result['duration']:.2f}s")
else:
    print(f"✗ شکست: {result['reason']} (مسدود شده توسط {result.get('blocked_by')})")
```

## الگوهای رایج

### الگو 1: Batch Processing با Safety

```python
async def execute_batch_safe(actions: list):
    """اجرای دسته‌ای با بررسی امنیت."""
    
    # بررسی امنیت همه
    results = safety.validate_batch(actions)
    
    # فیلتر اقدامات امن
    safe_actions = [
        action
        for action, (is_safe, _) in zip(actions, results)
        if is_safe
    ]
    
    print(f"Safe: {len(safe_actions)}/{len(actions)}")
    
    # اجرای اقدامات امن
    execution_results = []
    for action in safe_actions:
        result = await execute_smart_action(action)
        execution_results.append(result)
    
    return execution_results
```

### الگو 2: Multi-Monitor Workflow

```python
async def multi_monitor_workflow():
    """کار با چند مانیتور."""
    
    # دریافت مانیتورها
    monitors = multi_mon.get_monitors()
    print(f"Found {len(monitors)} monitors")
    
    # اقدام در هر مانیتور
    for mon in monitors:
        action = {
            "type": "DesktopClick",
            "params": {
                "x": mon.width // 2,
                "y": mon.height // 2,
                "button": "left"
            },
            "monitor": mon.index,
            "priority": "normal"
        }
        
        result = await execute_smart_action(action)
        print(f"Monitor {mon.index}: {result['success']}")
        
        await asyncio.sleep(1)
```

### الگو 3: Context-Aware Automation

```python
async def context_aware_automation(actions: list):
    """اتوماسیون هوشمند بر اساس context."""
    
    for action in actions:
        # دریافت context
        ctx = await context.get_current_context()
        
        # اگر gaming است، فقط HIGH priority
        if ctx.system_state == SystemState.GAMING:
            if action.get("priority") != "high":
                print(f"Skipping {action['type']} - user is gaming")
                continue
        
        # اگر busy است، تنظیم timing
        if ctx.system_state == SystemState.BUSY:
            action = context.adjust_action_timing(action, ctx)
        
        # اجرا
        result = await execute_smart_action(action)
        print(f"{action['type']}: {result['success']}")
```

### الگو 4: Recovery with Rollback

```python
async def execute_with_rollback(action: dict, rollback_data: dict):
    """اجرا با قابلیت rollback."""
    
    # تابع rollback
    async def rollback():
        print("Performing rollback...")
        # بازگشت تغییرات
        restore_state(rollback_data)
    
    # بررسی safety
    is_safe, reason = safety.validate_action(action)
    if not is_safe:
        return {"success": False, "reason": reason}
    
    # اجرا با recovery
    async def execute():
        # ذخیره state قبلی
        save_state(rollback_data)
        
        # اجرای اقدام
        perform_action(action)
        
        return True
    
    result = await recovery.execute_with_recovery(
        execute,
        action,
        rollback_func=rollback
    )
    
    return {
        "success": result.success,
        "error": result.error
    }
```

## مثال‌های کامل

### مثال 1: سیستم اتوماسیون هوشمند

```python
import asyncio
from core import *

class SmartAutomation:
    """سیستم اتوماسیون هوشمند."""
    
    def __init__(self):
        self.context = ContextAwareActions()
        self.safety = ActionSafety(strict_mode=True)
        self.multi_mon = MultiMonitor()
        self.recovery = ActionRecovery()
        
        self.mouse = MouseControl()
        self.desktop = DesktopActions()
    
    async def execute(self, action: dict):
        """اجرای هوشمند اقدام."""
        
        # 1. Context
        ctx = await self.context.get_current_context()
        should_run, reason = self.context.should_execute_action(action, ctx)
        
        if not should_run:
            return {"success": False, "reason": f"Deferred: {reason}"}
        
        # 2. Safety
        is_safe, reason = self.safety.validate_action(action)
        if not is_safe:
            return {"success": False, "reason": f"Blocked: {reason}"}
        
        # 3. Timing
        action = self.context.adjust_action_timing(action, ctx)
        
        # 4. Multi-Monitor
        if "monitor" in action:
            action = self._adjust_for_monitor(action)
        
        # 5. Execute with Recovery
        result = await self._execute_action(action)
        
        return result
    
    def _adjust_for_monitor(self, action: dict):
        """تنظیم برای multi-monitor."""
        monitor_idx = action.get("monitor", 0)
        monitor = self.multi_mon.get_monitor_by_index(monitor_idx)
        
        if monitor and "x" in action["params"]:
            x = action["params"]["x"]
            y = action["params"]["y"]
            
            action["params"]["x"] = monitor.x + x
            action["params"]["y"] = monitor.y + y
        
        return action
    
    async def _execute_action(self, action: dict):
        """اجرا با recovery."""
        async def do_action():
            action_type = action["type"]
            params = action["params"]
            
            if action_type == "DesktopClick":
                self.mouse.click(params["x"], params["y"])
            elif action_type == "LaunchApp":
                self.desktop.launch_app(params["path"])
            
            return True
        
        result = await self.recovery.execute_with_recovery(do_action, action)
        
        return {
            "success": result.success,
            "attempts": result.attempts,
            "error": result.error
        }

# استفاده
async def main():
    automation = SmartAutomation()
    
    actions = [
        {
            "type": "DesktopClick",
            "params": {"x": 100, "y": 100},
            "priority": "normal",
            "monitor": 0
        },
        {
            "type": "LaunchApp",
            "params": {"path": "notepad.exe"},
            "priority": "normal"
        }
    ]
    
    for action in actions:
        result = await automation.execute(action)
        print(f"{action['type']}: {result}")

asyncio.run(main())
```

### مثال 2: مانیتورینگ و لاگ کامل

```python
import logging
from datetime import datetime

class MonitoredAutomation(SmartAutomation):
    """اتوماسیون با مانیتورینگ کامل."""
    
    def __init__(self):
        super().__init__()
        
        # Setup logging
        logging.basicConfig(
            filename='automation.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def execute(self, action: dict):
        """اجرا با لاگ کامل."""
        
        start_time = datetime.now()
        
        # لاگ شروع
        self.logger.info(f"Starting: {action['type']}")
        
        # دریافت context
        ctx = await self.context.get_current_context()
        self.logger.info(
            f"Context: state={ctx.system_state.name}, "
            f"cpu={ctx.cpu_usage:.1f}%, ram={ctx.ram_usage:.1f}%"
        )
        
        # اجرا
        result = await super().execute(action)
        
        # لاگ نتیجه
        duration = (datetime.now() - start_time).total_seconds()
        
        if result["success"]:
            self.logger.info(
                f"Success: {action['type']} in {duration:.2f}s "
                f"(attempts: {result.get('attempts', 1)})"
            )
        else:
            self.logger.error(
                f"Failed: {action['type']} - {result['reason']}"
            )
        
        # آمار recovery
        stats = self.recovery.get_statistics()
        self.logger.info(
            f"Recovery stats: {stats['successful']}/{stats['total_attempts']} "
            f"({stats['success_rate']:.1f}%)"
        )
        
        return result
```

## بهترین شیوه‌ها

### 1. همیشه از Pipeline کامل استفاده کنید

```python
# ✗ بد
mouse.click(100, 100)

# ✓ خوب
await execute_smart_action({
    "type": "DesktopClick",
    "params": {"x": 100, "y": 100},
    "priority": "normal"
})
```

### 2. اولویت را درست تعیین کنید

```python
# اقدامات ضروری
action["priority"] = "high"

# اقدامات عادی
action["priority"] = "normal"

# اقدامات اختیاری
action["priority"] = "low"
```

### 3. از Rollback برای عملیات حیاتی استفاده کنید

```python
config = RecoveryConfig(enable_rollback=True)
recovery = ActionRecovery(config)

await recovery.execute_with_recovery(
    critical_operation,
    action,
    rollback_func=rollback_changes
)
```

### 4. مانیتور مناسب را مشخص کنید

```python
# مانیتور فعلی
current = multi_mon.get_current_monitor()
action["monitor"] = current.index

# یا مانیتور مشخص
action["monitor"] = 0  # مانیتور اصلی
```

### 5. خطاها را لاگ کنید

```python
result = await execute_smart_action(action)

if not result["success"]:
    logging.error(f"Failed: {action['type']} - {result['reason']}")
```

## عیب‌یابی

### مشکل: اقدام اجرا نمی‌شود

**بررسی:**
1. Context مناسب است؟
2. Safety اجازه می‌دهد؟
3. Multi-Monitor صحیح است؟
4. Recovery timeout نشده؟

**راه‌حل:**
```python
# فعال کردن لاگ کامل
logging.basicConfig(level=logging.DEBUG)

# بررسی هر مرحله
ctx = await context.get_current_context()
print(f"Context: {ctx}")

is_safe, reason = safety.validate_action(action)
print(f"Safety: {is_safe}, {reason}")
```

### مشکل: عملکرد کند

**علت:**
- Cache غیرفعال است
- خیلی زیاد retry می‌کند

**راه‌حل:**
```python
# فعال کردن cache
ctx = await context.get_current_context(use_cache=True)

# کاهش retry
config = RecoveryConfig(max_retries=2)
```

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: November 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
