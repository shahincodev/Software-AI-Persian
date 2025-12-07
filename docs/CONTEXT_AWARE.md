# اقدامات هوشمند بر اساس Context

## نمای کلی

سیستم Context-Aware Actions یک لایه هوشمند برای تصمیم‌گیری در مورد اجرای اقدامات است. این سیستم با تحلیل وضعیت سیستم، برنامه فعال، و منابع، بهترین زمان و روش برای اجرای هر اقدام را تعیین می‌کند.

## ویژگی‌ها

### 🧠 تحلیل هوشمند

- **System State Detection**: تشخیص وضعیت سیستم (IDLE، BUSY، GAMING، WORKING)
- **Application Categorization**: دسته‌بندی برنامه‌ها (Browser، Editor، Game، ...)
- **Resource Monitoring**: مانیتورینگ CPU و RAM
- **Fullscreen Detection**: تشخیص حالت تمام‌صفحه

### ⏱️ مدیریت زمان‌بندی

- **Smart Timing**: تنظیم زمان‌بندی بر اساس context
- **Wait for Optimal Time**: انتظار برای بهترین زمان اجرا
- **Priority-Based Execution**: اجرا بر اساس اولویت

### 🎯 تصمیم‌گیری

- **Should Execute**: تصمیم درباره اجرا یا تاخیر
- **Action Adjustment**: تنظیم پارامترهای اقدام
- **Context-Aware Delays**: تاخیرهای هوشمند

## نحوه استفاده

### راه‌اندازی

```python
from core import ContextAwareActions

# ایجاد سیستم context-aware
context = ContextAwareActions()

# دریافت context فعلی
ctx = await context.get_current_context()

print(f"پنجره فعال: {ctx.active_window}")
print(f"وضعیت سیستم: {ctx.system_state}")
print(f"CPU: {ctx.cpu_usage}%")
```

## ContextInfo

### ساختار

```python
@dataclass
class ContextInfo:
    active_window: str              # عنوان پنجره فعال
    active_process: str             # نام پروسه فعال
    app_category: ApplicationCategory  # دسته برنامه
    system_state: SystemState       # وضعیت سیستم
    cpu_usage: float                # مصرف CPU (0-100)
    ram_usage: float                # مصرف RAM (0-100)
    is_fullscreen: bool             # حالت تمام‌صفحه
    mouse_position: Tuple[int, int] # موقعیت موس
    timestamp: float                # زمان دریافت
```

### مثال

```python
ctx = await context.get_current_context()

print(f"پنجره: {ctx.active_window}")
print(f"پروسه: {ctx.active_process}")
print(f"دسته: {ctx.app_category.name}")
print(f"وضعیت: {ctx.system_state.name}")
print(f"CPU: {ctx.cpu_usage:.1f}%")
print(f"RAM: {ctx.ram_usage:.1f}%")
print(f"تمام‌صفحه: {ctx.is_fullscreen}")
print(f"موس: {ctx.mouse_position}")
```

## SystemState (وضعیت سیستم)

### انواع وضعیت

```python
class SystemState(Enum):
    IDLE = "idle"         # بیکار (CPU < 30%, RAM < 50%)
    BUSY = "busy"         # مشغول (CPU > 70%, RAM > 80%)
    GAMING = "gaming"     # در حال بازی
    WORKING = "working"   # در حال کار (Editor/Office/Development)
    LOCKED = "locked"     # قفل شده
    UNKNOWN = "unknown"   # نامشخص
```

### تشخیص خودکار

```python
# سیستم به صورت خودکار وضعیت را تشخیص می‌دهد:

# IDLE: CPU < 30% و RAM < 50%
# BUSY: CPU > 70% یا RAM > 80%
# GAMING: برنامه از دسته GAME
# WORKING: برنامه از دسته EDITOR/OFFICE/DEVELOPMENT
# UNKNOWN: سایر موارد
```

### استفاده

```python
ctx = await context.get_current_context()

if ctx.system_state == SystemState.GAMING:
    print("کاربر در حال بازی است - اقدامات را به تعویق بیانداز")
elif ctx.system_state == SystemState.BUSY:
    print("سیستم مشغول است - منتظر بمان")
elif ctx.system_state == SystemState.IDLE:
    print("سیستم بیکار است - اقدام را اجرا کن")
```

## ApplicationCategory (دسته برنامه)

### انواع دسته

```python
class ApplicationCategory(Enum):
    BROWSER = "browser"           # مرورگر
    EDITOR = "editor"             # ویرایشگر متن
    OFFICE = "office"             # برنامه اداری
    MEDIA = "media"               # پخش‌کننده رسانه
    GAME = "game"                 # بازی
    SYSTEM = "system"             # سیستمی
    COMMUNICATION = "communication"  # ارتباطات
    DEVELOPMENT = "development"   # توسعه
    DESIGN = "design"             # طراحی
    OTHER = "other"               # سایر
```

### برنامه‌های پیش‌فرض

```python
BROWSER:
- chrome.exe, firefox.exe, msedge.exe, opera.exe

EDITOR:
- code.exe, notepad++.exe, sublime_text.exe, atom.exe

OFFICE:
- winword.exe, excel.exe, powerpnt.exe

MEDIA:
- vlc.exe, spotify.exe, wmplayer.exe

GAME:
- steam.exe

COMMUNICATION:
- discord.exe, telegram.exe, slack.exe, teams.exe

DEVELOPMENT:
- devenv.exe (Visual Studio), pycharm64.exe, idea64.exe

DESIGN:
- photoshop.exe, illustrator.exe
```

### استفاده

```python
ctx = await context.get_current_context()

if ctx.app_category == ApplicationCategory.GAME:
    print("بازی در حال اجرا - اقدامات مزاحم را مسدود کن")
elif ctx.app_category == ApplicationCategory.EDITOR:
    print("در حال کدنویسی - تایمینگ را کندتر کن")
```

## تصمیم‌گیری اجرا

### should_execute_action

```python
action = {
    "type": "LaunchApp",
    "params": {"path": "app.exe"},
    "priority": "normal"  # low, normal, high
}

ctx = await context.get_current_context()

should_run, reason = context.should_execute_action(action, ctx)

if should_run:
    print("اجرا کن")
else:
    print(f"منتظر بمان: {reason}")
```

### قوانین تصمیم‌گیری

#### GAMING State
```python
# اولویت LOW → رد می‌شود
# اولویت NORMAL → رد می‌شود
# اولویت HIGH → اجرا می‌شود
```

#### BUSY State
```python
# اولویت LOW → رد می‌شود
# اولویت NORMAL → تاخیر
# اولویت HIGH → اجرا می‌شود
```

#### Fullscreen Mode
```python
# اقدامات مزاحم (LaunchApp, ExecuteCommand) → رد می‌شود
# اقدامات غیرمزاحم (QueryHardware, WaitAction) → اجرا می‌شود
```

#### IDLE State
```python
# همه اقدامات → اجرا می‌شود
```

## تنظیم زمان‌بندی

### adjust_action_timing

```python
action = {
    "type": "DesktopClick",
    "params": {"interval": 1.0, "timeout": 10.0}
}

ctx = await context.get_current_context()

adjusted = context.adjust_action_timing(action, ctx)

print(f"Interval: {adjusted['params']['interval']}")
print(f"Timeout: {adjusted['params']['timeout']}")
```

### ضرایب تنظیم

```python
# GAMING: سریع‌تر (0.5x interval)
# BUSY: کندتر (1.5x interval, 2x timeout)
# WORKING: کمی کندتر (1.2x interval, 1.5x timeout)
# IDLE: عادی (1x)
```

### مثال

```python
# GAMING
action = {"type": "Click", "params": {"interval": 2.0}}
adjusted = context.adjust_action_timing(action, gaming_ctx)
# interval = 1.0 (2.0 * 0.5)

# BUSY
action = {"type": "Click", "params": {"interval": 2.0, "timeout": 10.0}}
adjusted = context.adjust_action_timing(action, busy_ctx)
# interval = 3.0 (2.0 * 1.5)
# timeout = 20.0 (10.0 * 2.0)
```

## انتظار هوشمند

### wait_for_appropriate_time

```python
action = {
    "type": "InstallPackage",
    "priority": "low"
}

# منتظر ماندن تا زمان مناسب
success = await context.wait_for_appropriate_time(
    action,
    max_wait=60.0,  # حداکثر 60 ثانیه منتظر بمان
    check_interval=2.0  # هر 2 ثانیه بررسی کن
)

if success:
    # زمان مناسب رسید - اجرا کن
    execute_action(action)
else:
    # timeout - منصرف شو
    print("زمان مناسب پیدا نشد")
```

### الگوریتم

```
while time < max_wait:
    ctx = get_current_context()
    should_run, reason = should_execute_action(action, ctx)
    
    if should_run:
        return True
    
    await sleep(check_interval)

return False
```

## کش‌کردن Context

### استفاده از Cache

```python
# با cache (سریع‌تر، اما ممکن است قدیمی باشد)
ctx1 = await context.get_current_context(use_cache=True)

# بدون cache (کندتر، اما همیشه به‌روز)
ctx2 = await context.get_current_context(use_cache=False)
```

### زمان Cache

```python
# Cache برای 1 ثانیه معتبر است
# بعد از 1 ثانیه، دوباره Context بررسی می‌شود
```

## سناریوهای کاربردی

### سناریو 1: اجرای اتوماسیون بدون مزاحمت

```python
from core import ContextAwareActions, ActionSafety

context = ContextAwareActions()
safety = ActionSafety()

async def smart_automation(action):
    # بررسی context
    ctx = await context.get_current_context()
    should_run, reason = context.should_execute_action(action, ctx)
    
    if not should_run:
        # منتظر زمان مناسب
        success = await context.wait_for_appropriate_time(action, max_wait=300)
        if not success:
            return "Timeout - context never became appropriate"
    
    # بررسی امنیت
    is_safe, safety_reason = safety.validate_action(action)
    if not is_safe:
        return f"Blocked by safety: {safety_reason}"
    
    # تنظیم timing
    ctx = await context.get_current_context()
    adjusted = context.adjust_action_timing(action, ctx)
    
    # اجرا
    return await execute(adjusted)
```

### سناریو 2: جلوگیری از مزاحمت در بازی

```python
ctx = await context.get_current_context()

if ctx.system_state == SystemState.GAMING or ctx.is_fullscreen:
    # اقدامات غیرضروری را به تعویق بیانداز
    if action.get("priority") != "high":
        await asyncio.sleep(300)  # 5 دقیقه صبر کن
```

### سناریو 3: سازگاری با وضعیت سیستم

```python
ctx = await context.get_current_context()

if ctx.system_state == SystemState.BUSY:
    # سیستم مشغول است - آرام‌تر کار کن
    action["params"]["interval"] *= 2
    action["params"]["max_concurrent"] = 1
elif ctx.system_state == SystemState.IDLE:
    # سیستم بیکار است - سریع‌تر کار کن
    action["params"]["max_concurrent"] = 4
```

## API Reference

### ContextAwareActions

#### `get_current_context(use_cache: bool = True) -> ContextInfo`
دریافت context فعلی سیستم.

#### `should_execute_action(action: Dict, context_info: ContextInfo) -> Tuple[bool, str]`
تصمیم درباره اجرای اقدام.

**بازگشت:** `(should_execute, reason)`

#### `adjust_action_timing(action: Dict, context_info: ContextInfo) -> Dict`
تنظیم timing بر اساس context.

**بازگشت:** اقدام با timing تنظیم شده

#### `wait_for_appropriate_time(action: Dict, max_wait: float = 60, check_interval: float = 2) -> bool`
منتظر ماندن تا زمان مناسب.

**بازگشت:** True اگر زمان مناسب پیدا شد

## بهترین شیوه‌ها

1. **همیشه context بررسی کنید** قبل از اقدامات مزاحم
2. **از wait_for_appropriate_time استفاده کنید** برای اقدامات غیرفوری
3. **timing را تنظیم کنید** بر اساس وضعیت سیستم
4. **اولویت تعیین کنید** - HIGH برای اقدامات ضروری
5. **از cache استفاده کنید** برای عملکرد بهتر

## عیب‌یابی

### مشکل: همیشه اجرا می‌شود حتی در بازی

**علت:** اولویت HIGH تنظیم شده

**راه‌حل:**
```python
action["priority"] = "normal"  # یا "low"
```

### مشکل: هیچ‌وقت اجرا نمی‌شود

**علت:** شرایط context هرگز مناسب نمی‌شود

**راه‌حل:**
```python
# افزایش max_wait
await context.wait_for_appropriate_time(action, max_wait=600)

# یا اولویت HIGH
action["priority"] = "high"
```

### مشکل: timing خیلی کند است

**علت:** سیستم BUSY تشخیص داده شده

**راه‌حل:**
```python
# غیرفعال کردن auto-adjustment
# نباید adjust_action_timing استفاده کنید
```

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: December 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
