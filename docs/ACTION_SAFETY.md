# سیستم امنیت اقدامات (Action Safety)

## نمای کلی

سیستم امنیت اقدامات یک لایه محافظتی هوشمند است که از اجرای اقدامات خطرناک یا مخرب جلوگیری می‌کند. این سیستم تمام اقدامات را قبل از اجرا بررسی کرده و در صورت تشخیص خطر، از اجرای آن‌ها جلوگیری می‌کند.

## ویژگی‌ها

### 🛡️ حفاظت چندلایه

- **حفاظت از فایل‌های سیستمی**: جلوگیری از حذف یا تغییر فایل‌های حیاتی Windows
- **حفاظت از پروسه‌های مهم**: جلوگیری از بستن پروسه‌های سیستمی
- **فیلتر دستورات خطرناک**: مسدودسازی دستورات مخرب (format، delete، shutdown)
- **بررسی فایل‌های قابل اجرا**: تشخیص فایل‌های مشکوک (exe، bat، ps1)
- **محافظت از رجیستری**: جلوگیری از تغییر کلیدهای حساس رجیستری

### 🎯 حالت‌های عملکرد

#### حالت عادی (Normal Mode)
```python
safety = ActionSafety(strict_mode=False)
```
- انعطاف‌پذیرتر برای کاربران حرفه‌ای
- فقط اقدامات بسیار خطرناک را مسدود می‌کند
- مناسب برای محیط توسعه

#### حالت سخت‌گیرانه (Strict Mode)
```python
safety = ActionSafety(strict_mode=True)
```
- امنیت حداکثری
- حتی اقدامات مشکوک را مسدود می‌کند
- **پیشنهادی** برای استفاده روزمره

## نحوه استفاده

### بررسی اقدام تکی

```python
from core import ActionSafety

# ایجاد سیستم امنیت
safety = ActionSafety(strict_mode=True)

# تعریف اقدام
action = {
    "type": "DeleteFile",
    "params": {"path": "C:/Users/Documents/old_file.txt"}
}

# بررسی امنیت
is_safe, reason = safety.validate_action(action)

if is_safe:
    # اجرای اقدام
    execute_action(action)
else:
    print(f"اقدام خطرناک است: {reason}")
```

### بررسی دسته‌ای

```python
actions = [
    {"type": "DeleteFile", "params": {"path": "temp1.txt"}},
    {"type": "DeleteFile", "params": {"path": "C:/Windows/System32/kernel32.dll"}},
    {"type": "LaunchApp", "params": {"path": "notepad.exe"}},
]

# بررسی همه
results = safety.validate_batch(actions)

for action, (is_safe, reason) in zip(actions, results):
    if is_safe:
        print(f"✓ {action['type']} امن است")
    else:
        print(f"✗ {action['type']} خطرناک: {reason}")
```

## انواع اقدامات محافظت‌شده

### 1. DeleteFile
**محافظت از:**
- فایل‌های سیستمی (`C:/Windows/`, `C:/Program Files/`)
- درایورها (`*.sys`, `*.dll`)
- فایل‌های Boot (`bootmgr`, `ntldr`)

**مثال:**
```python
# امن
{"type": "DeleteFile", "params": {"path": "C:/Users/Me/temp.txt"}}

# خطرناک
{"type": "DeleteFile", "params": {"path": "C:/Windows/System32/kernel32.dll"}}
```

### 2. TerminateProcess
**محافظت از:**
- پروسه‌های حیاتی (`explorer.exe`, `csrss.exe`, `winlogon.exe`)
- سرویس‌های سیستمی (`services.exe`, `lsass.exe`)

**مثال:**
```python
# امن
{"type": "TerminateProcess", "params": {"name": "notepad.exe"}}

# خطرناک
{"type": "TerminateProcess", "params": {"name": "csrss.exe"}}
```

### 3. ExecuteCommand
**محافظت از:**
- دستورات format (`format c:`, `diskpart`)
- حذف گسترده (`del /f /s /q`, `rd /s /q`)
- تغییرات سیستمی (`shutdown`, `regedit`)

**مثال:**
```python
# امن
{"type": "ExecuteCommand", "params": {"command": "dir"}}

# خطرناک
{"type": "ExecuteCommand", "params": {"command": "format c: /q"}}
```

### 4. ModifyRegistry
**محافظت از:**
- کلیدهای Startup (`Run`, `RunOnce`)
- تنظیمات امنیتی (`Policies`, `Security`)
- سرویس‌ها (`Services`)

**مثال:**
```python
# امن
{"type": "ModifyRegistry", "params": {"key": "HKCU\\Software\\MyApp\\Settings"}}

# خطرناک
{"type": "ModifyRegistry", "params": {"key": "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"}}
```

### 5. DownloadFile
**محافظت از:**
- فایل‌های قابل اجرا در strict mode
- پروتکل‌های ناامن (`ftp://`, `file://`)

**مثال:**
```python
# امن
{"type": "DownloadFile", "params": {"url": "https://example.com/data.json"}}

# مشکوک (در strict mode)
{"type": "DownloadFile", "params": {"url": "https://example.com/app.exe"}}
```

### 6. LaunchApp
**محافظت از:**
- آرگومان‌های خطرناک (`/admin`, `/elevated`)

**مثال:**
```python
# امن
{"type": "LaunchApp", "params": {"path": "notepad.exe"}}

# خطرناک
{"type": "LaunchApp", "params": {"path": "cmd.exe", "args": "/admin"}}
```

## لیست‌های محافظت

### مسیرهای ممنوع
```python
"C:/Windows/System32"
"C:/Windows/SysWOW64"
"C:/Program Files"
"C:/ProgramData"
"C:/$"  # فایل‌های سیستم مخفی
```

### پسوندهای مشکوک
```python
".exe"
".bat"
".cmd"
".ps1"
".vbs"
".reg"
".msi"
".scr"
```

### پروسه‌های حیاتی
```python
"explorer.exe"
"csrss.exe"
"services.exe"
"lsass.exe"
"winlogon.exe"
"smss.exe"
```

### دستورات ممنوع
```python
"format"
"diskpart"
"del /f /s /q"
"rd /s /q"
"shutdown"
"regedit"
```

## پیکربندی پیشرفته

### تغییر حالت امنیت

```python
# برای کار عادی
safety = ActionSafety(strict_mode=False)

# برای محیط حساس
safety = ActionSafety(strict_mode=True)
```

### استفاده در pipeline

```python
from core import ActionSafety, ActionRecovery

safety = ActionSafety(strict_mode=True)
recovery = ActionRecovery()

async def safe_execute(action):
    # بررسی امنیت
    is_safe, reason = safety.validate_action(action)
    
    if not is_safe:
        print(f"اقدام مسدود شد: {reason}")
        return None
    
    # اجرا با recovery
    result = await recovery.execute_with_recovery(
        lambda: perform_action(action),
        action
    )
    
    return result
```

## عیب‌یابی

### مشکل: اقدام امن مسدود می‌شود

**علت**: Strict mode فعال است

**راه‌حل**:
```python
# غیرفعال کردن strict mode
safety = ActionSafety(strict_mode=False)
```

### مشکل: نیاز به افزودن استثنا

**راه‌حل**: فعلاً لیست‌های محافظت ثابت هستند. در آینده قابلیت افزودن استثنا اضافه می‌شود.

### مشکل: بررسی امنیت کند است

**راه‌حل**: بررسی امنیت بسیار سریع است (< 1ms). اگر کند است، مشکل از جای دیگری است.

## بهترین شیوه‌ها

1. **همیشه strict mode را فعال کنید** مگر در محیط توسعه
2. **قبل از هر اقدام امنیت بررسی کنید** - حتی اگر قبلاً بررسی شده
3. **دلیل رد شدن را لاگ کنید** - برای عیب‌یابی
4. **با سایر سیستم‌ها ترکیب کنید** - Context-aware، Recovery
5. **به کاربر اطلاع دهید** - چرا اقدام مسدود شد

## API Reference

### ActionSafety

#### `__init__(strict_mode: bool = True)`
ایجاد سیستم امنیت.

#### `validate_action(action: Dict[str, Any]) -> Tuple[bool, str]`
بررسی امنیت یک اقدام.

**بازگشت:** `(is_safe, reason)`
- `is_safe`: True اگر امن باشد
- `reason`: دلیل رد یا تایید

#### `validate_batch(actions: List[Dict[str, Any]]) -> List[Tuple[bool, str]]`
بررسی دسته‌ای اقدامات.

**بازگشت:** لیست نتایج `(is_safe, reason)` برای هر اقدام

## مثال‌های کامل

### استفاده ساده
```python
from core import ActionSafety

safety = ActionSafety()

action = {
    "type": "DeleteFile",
    "params": {"path": "old_data.txt"}
}

is_safe, reason = safety.validate_action(action)
print(f"امنیت: {is_safe}, دلیل: {reason}")
```

### استفاده پیشرفته با Context
```python
from core import ActionSafety, ContextAwareActions

safety = ActionSafety(strict_mode=True)
context = ContextAwareActions()

async def smart_execute(action):
    # بررسی context
    ctx = await context.get_current_context()
    should_run, ctx_reason = context.should_execute_action(action, ctx)
    
    if not should_run:
        return f"رد شد (context): {ctx_reason}"
    
    # بررسی امنیت
    is_safe, safety_reason = safety.validate_action(action)
    
    if not is_safe:
        return f"رد شد (safety): {safety_reason}"
    
    # اجرا
    return await execute(action)
```

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: December 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
