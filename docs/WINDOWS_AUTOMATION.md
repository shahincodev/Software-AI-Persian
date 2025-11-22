# 🖥️ سیستم اتوماسیون ویندوز - Windows Automation System

یک سیستم قدرتمند و ایمن برای اتوماسیون کارهای ویندوز با استفاده از هوش مصنوعی.

## 🎯 قابلیت‌ها

### ✅ اقدامات سیستمی
- **باز کردن برنامه‌ها**: اجرای برنامه‌های نصب‌شده (Photoshop, Notepad, Chrome, ...)
- **نصب نرم‌افزار**: نصب بسته‌ها از طریق winget, choco, pip, npm
- **دریافت اطلاعات سخت‌افزار**: CPU, RAM, Disk, Network, Processes
- **مدیریت فرآیندها**: بستن فرآیندهای در حال اجرا

### 🛡️ امنیت
- **فیلتر امنیتی**: بررسی اقدامات قبل از اجرا
- **Whitelist/Blacklist**: محدود کردن برنامه‌ها و فرآیندهای قابل اجرا
- **سطوح ریسک**: تعیین خودکار خطر هر اقدام (SAFE → CRITICAL)
- **تایید کاربر**: درخواست مجوز برای اقدامات پرخطر
- **Dry-Run**: شبیه‌سازی بدون اجرای واقعی

### 📊 نظارت
- **نظارت real-time**: CPU, RAM, Disk usage
- **هشدارهای هوشمند**: اعلام هنگام مصرف بالای منابع
- **تاریخچه**: ذخیره و تحلیل روند استفاده
- **فرآیندهای پرمصرف**: شناسایی برنامه‌های سنگین

### 🔍 کشف قابلیت‌ها
- **اسکن خودکار سیستم**: یافتن برنامه‌ها و ابزارهای نصب‌شده
- **کش هوشمند**: ذخیره اطلاعات برای دسترسی سریع
- **مشخصات سخت‌افزار**: نمای کامل از قطعات سیستم

### 🧠 یکپارچگی با AI
- **تشخیص خودکار**: AI خودش تصمیم می‌گیرد کدام اقدام لازم است
- **مدل اختصاصی**: purpose جدید `system` برای عملیات سیستمی
- **Context-aware**: استفاده از اطلاعات سیستم برای تصمیم‌گیری بهتر

## 📁 ساختار

```
core/
├── system_actions.py          # تعریف اقدامات (Action Schema)
├── system_tools.py            # آداپتورهای اجرایی
├── safety_filter.py           # فیلتر امنیتی و تایید کاربر
├── system_capabilities.py    # کشف و رجیستری قابلیت‌ها
├── execution_manager.py       # مدیر صف و اجرا
├── monitoring_service.py      # نظارت بر منابع
└── ai_brain.py               # یکپارچگی با LLM (بروز شده)
```

## 🚀 نصب

### پیش‌نیازها
```powershell
pip install psutil>=5.9.0
pip install pywin32>=305  # برای ویندوز
```

یا:
```powershell
pip install -r requirements.txt
```

## 💡 نمونه‌های استفاده

### 1️⃣ دریافت اطلاعات سخت‌افزار

```python
from core.system_actions import QueryHardwareAction
from core.execution_manager import ExecutionManager

# ساخت اقدام
action = QueryHardwareAction(query_type="all")

# اجرا
manager = ExecutionManager()
action_id = manager.submit(action)
result = await manager.execute_next()

print(result.output)  # اطلاعات CPU, RAM, Disk, ...
```

### 2️⃣ باز کردن برنامه

```python
from core.system_actions import LaunchAppAction

# باز کردن Notepad
action = LaunchAppAction(
    app_name="notepad.exe",
    require_consent=True
)

manager = ExecutionManager()
manager.submit(action)
result = await manager.execute_next()
```

### 3️⃣ نصب نرم‌افزار (Dry-Run)

```python
from core.system_actions import InstallPackageAction

# شبیه‌سازی نصب Git
action = InstallPackageAction(
    package_name="git",
    package_manager="winget",
    silent=True,
    dry_run=True  # فقط شبیه‌سازی
)

manager = ExecutionManager(dry_run=True)
result = await manager.execute_next()
print(result.output)  # نمایش دستور بدون اجرا
```

### 4️⃣ کشف قابلیت‌های سیستم

```python
from core.system_capabilities import SystemCapabilityRegistry

registry = SystemCapabilityRegistry()
registry.scan_system()

# نمایش خلاصه
print(registry.get_summary())

# لیست برنامه‌ها
apps = registry.list_capabilities(type_filter="app")
for app in apps:
    print(f"{app.name}: {app.path}")
```

### 5️⃣ نظارت بر منابع

```python
from core.monitoring_service import MonitoringService

monitor = MonitoringService(interval_seconds=5.0)
monitor.start()

# بعد از مدتی...
print(monitor.get_summary())
avg = monitor.get_average_usage(last_n=10)

monitor.stop()
```

### 6️⃣ استفاده با AI

```python
from core.ai_brain import AIBrain

brain = AIBrain()

# تشخیص خودکار: task شامل کلمات کلیدی سیستمی
model = brain.get_model(task="Photoshop را باز کن")
# خودکار purpose='system' انتخاب می‌شود

# یا به صورت صریح:
model = brain.get_model(purpose="system")
```

## 🔒 تنظیمات امنیتی

### حالت Strict
```python
from core.safety_filter import SafetyFilter

filter = SafetyFilter(strict_mode=True)
# در این حالت:
# - فقط برنامه‌های whitelist اجرا می‌شوند
# - اقدامات CRITICAL رد می‌شوند
```

### سفارشی‌سازی Policy
```python
from core.safety_filter import SafetyPolicy

policy = SafetyPolicy()
policy.allowed_apps.add("myapp.exe")
policy.protected_processes.add("important.exe")

filter = SafetyFilter(policy=policy)
```

## 🧪 تست

فایل نمونه کامل:
```powershell
python examples/windows_automation_demo.py
```

این فایل تمام قابلیت‌ها را نمایش می‌دهد:
- ✅ کشف قابلیت‌ها
- ✅ دریافت اطلاعات سخت‌افزار
- ✅ Dry-run نصب
- ✅ نظارت real-time
- ✅ باز کردن برنامه (با تایید)

## ⚙️ متغیرهای محیطی

```bash
# مدل برای عملیات سیستمی
GOOGLE_SYSTEM_MODEL=gemini-2.5-flash
SYSTEM_MODEL_TEMPERATURE=0.3

# مدل‌های دیگر
GOOGLE_REASONING_MODEL=gemini-2.5-flash
GROQ_MODEL=groq-1
OPENAI_MODEL=openai/gpt-4o-mini
```

## 📊 لاگ‌ها و ممیزی

تمام اقدامات در فایل audit log ذخیره می‌شوند:
```
data/logs/audit.jsonl
```

هر خط یک JSON شامل:
- اطلاعات اقدام (action)
- نتیجه (result)
- زمان و مدت اجرا
- خروجی یا خطا

## 🎨 معماری

```
┌─────────────────────────────────────────────────────┐
│                    User / AI                        │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              AIBrain (Purpose: system)              │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              SystemCapabilityRegistry               │
│         (کشف برنامه‌ها و سخت‌افزار)                │
└─────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│                ExecutionManager                      │
│  ┌──────────────┐  ┌──────────────┐                │
│  │ Action Queue │  │ Concurrency  │                │
│  └──────────────┘  └──────────────┘                │
└───┬─────────────────────────────────────────────┬───┘
    │                                             │
    ▼                                             ▼
┌──────────────────────┐              ┌──────────────────┐
│   SafetyFilter       │              │ MonitoringService│
│  ┌────────────────┐  │              │   (Real-time)    │
│  │ Risk Analysis  │  │              └──────────────────┘
│  │ Whitelist/     │  │
│  │ Blacklist      │  │
│  └────────────────┘  │
└───┬──────────────────┘
    │
    ▼
┌──────────────────────┐
│ UserConsentManager   │
│  (تایید کاربر)      │
└───┬──────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│              SystemToolAdapter                       │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │ProcessLaunch│ │PackageInstall│ │HardwareQuery │ │
│  └─────────────┘ └──────────────┘ └──────────────┘ │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
           ┌───────────────────┐
           │  Windows OS API   │
           │ (psutil/subprocess│
           │    /win32api)     │
           └───────────────────┘
```

## 🚨 نکات مهم

### ⚠️ امنیت
- **همیشه در محیط تست**: قبل از استفاده در محیط واقعی، تست کنید
- **بررسی audit logs**: همه اقدامات را بررسی کنید
- **Dry-run اول**: برای اقدامات جدید، ابتدا dry-run کنید

### ⚠️ محدودیت‌ها
- **فقط ویندوز**: برخی قابلیت‌ها ویندوز-محور هستند
- **دسترسی‌ها**: برخی اقدامات نیاز به Admin دارند
- **نصب psutil**: برای نظارت و مدیریت فرآیند ضروری است

### ⚠️ بهترین روش‌ها
- **سطح ریسک**: همیشه سطح ریسک را چک کنید
- **Timeout**: برای اقدامات طولانی timeout تنظیم کنید
- **Error handling**: خطاها را مدیریت کنید
- **Resource cleanup**: منابع را پاکسازی کنید

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION

---

**ساخته شده با ❤️ توسط تیم Shahin**
