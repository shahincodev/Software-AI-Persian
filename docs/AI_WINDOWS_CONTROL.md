# استفاده از سیستم اتوماسیون هوشمند ویندوز

## 🎯 مقدمه

سیستم Software-AI حالا می‌تواند **به صورت هوشمند** کامپیوتر ویندوز شما را کنترل کند!
دیگر نیازی به یادگیری دستورات خاص نیست - فقط به زبان طبیعی (فارسی یا انگلیسی) بگویید چه می‌خواهید.

## ✨ امکانات

### 1. **باز کردن برنامه‌ها**
```
باز کردن Notepad
open Photoshop
launch Visual Studio Code
```

### 2. **نصب نرم‌افزار**
```
نصب Git
install Python 3.11
setup Node.js با npm
```

### 3. **دریافت اطلاعات سیستم**
```
چقدر RAM دارم؟
show CPU usage
مشخصات کامل سیستم رو بده
```

### 4. **مدیریت فرآیندها**
```
بستن Chrome
kill all notepad processes
```

## 🚀 نحوه استفاده

### روش 1: از طریق CLI اصلی

```bash
python main.py --input-mode text
```

سپس درخواست‌های خود را بنویسید:

```
> باز کردن calculator
🤖 Processing system request with AI...

نتایج اجرا:
✅ اقدام 1: موفق

📊 آمار: 1 موفق، 0 ناموفق
```

### روش 2: با ورودی صوتی

```bash
python main.py --input-mode voice
```

فقط بگویید:
- "باز کردن Notepad"
- "Install Git"
- "Show me system info"

### روش 3: استفاده مستقیم از API

```python
from core.intelligent_agent import IntelligentSystemAgent
import asyncio

async def main():
    agent = IntelligentSystemAgent(dry_run=False)
    
    # درخواست طبیعی
    result = await agent.process_request("باز کردن Notepad")
    print(result)

asyncio.run(main())
```

## 🧠 چگونه کار می‌کند؟

1. **تشخیص هوشمند**: سیستم خودش تشخیص می‌دهد درخواست شما مربوط به:
   - اتوماسیون ویندوز 🪟
   - مرورگر وب 🌐
   - کدنویسی 💻

2. **تحلیل با AI**: اگر درخواست سیستمی بود:
   - از مدل Gemini استفاده می‌کند
   - درخواست را به اقدامات قابل اجرا تبدیل می‌کند
   - اولویت‌بندی می‌کند

3. **بررسی امنیت**: قبل از اجرا:
   - فیلتر امنیتی بررسی می‌کند
   - در صورت نیاز، تأیید می‌گیرد
   - خطرات را ارزیابی می‌کند

4. **اجرا**: اقدامات به ترتیب اولویت اجرا می‌شوند

5. **گزارش**: نتایج ذخیره و گزارش می‌شود

## 📋 مثال‌های کاربردی

### مثال 1: راه‌اندازی محیط توسعه

```
نصب Visual Studio Code، نصب Git، و باز کردن VS Code
```

سیستم خودش:
1. Git را از winget نصب می‌کند
2. VS Code را نصب می‌کند
3. VS Code را اجرا می‌کند

### مثال 2: بررسی وضعیت سیستم

```
مشخصات کامل سیستم من چیه؟
```

خروجی:
```
💻 مشخصات سیستم:
- CPU: 8 هسته، استفاده: 23%
- RAM: 16 GB، در دسترس: 8.5 GB
- Disk: 512 GB SSD، آزاد: 245 GB
- GPU: NVIDIA RTX 3060
```

### مثال 3: مدیریت برنامه‌ها

```
بستن همه برنامه‌های Chrome که بیش از 500MB RAM مصرف می‌کنند
```

## ⚙️ تنظیمات

### حالت Dry Run (ایمن)

برای تست بدون اجرای واقعی:

```bash
python main.py --debug
```

در این حالت:
- هیچ برنامه‌ای واقعاً باز نمی‌شود
- هیچ نرم‌افزاری نصب نمی‌شود
- فقط نشان می‌دهد چه اتفاقی می‌افتد

### سطح لاگ

```python
# در main.py
setup_logging(level=logging.DEBUG)  # جزئیات کامل
setup_logging(level=logging.INFO)   # عادی
setup_logging(level=logging.WARNING) # فقط هشدارها
```

## 🔒 امنیت

### فیلترهای امنیتی پیش‌فرض:

1. **لیست سفید برنامه‌ها**: فقط برنامه‌های شناخته‌شده
2. **فرآیندهای محافظت‌شده**: نمی‌توان بست:
   - `system`, `registry`, `winlogon`, `csrss`
3. **الگوهای مشکوک**: رد می‌شود:
   - دستورات PowerShell خطرناک
   - دسترسی به رجیستری حیاتی
   - حذف فایل‌های سیستمی

### سطوح خطر:

- 🟢 **SAFE**: اجرای خودکار
- 🟡 **LOW**: بررسی سریع
- 🟠 **MEDIUM**: تأیید کاربر
- 🔴 **HIGH**: هشدار + تأیید
- ⛔ **CRITICAL**: مسدود به طور پیش‌فرض

## 🐛 رفع مشکلات

### مشکل: "برنامه یافت نشد"

راه‌حل:
```python
from core.system_capabilities import SystemCapabilityRegistry

registry = SystemCapabilityRegistry()
registry.scan_system()  # اسکن مجدد
print(registry.get_summary())
```

### مشکل: "دسترسی رد شد"

راه‌حل: اجرا با دسترسی Administrator:
```bash
# PowerShell (Administrator)
python main.py
```

### مشکل: "AI نمی‌تواند درخواست را بفهمد"

راه‌حل: واضح‌تر بنویسید:
- ❌ "برنامه رو باز کن"
- ✅ "باز کردن Notepad"

## 📚 مثال‌های بیشتر

فایل `examples/intelligent_system_demo.py` را اجرا کنید:

```bash
python examples/intelligent_system_demo.py
```

این نمایش:
- ✅ درخواست‌های طبیعی
- ✅ سناریوهای ترکیبی
- ✅ سوالات سخت‌افزاری
- ✅ خلاصه سیستم

## 🎓 نکات پیشرفته

### استفاده از اولویت

```python
# در JSON تولید شده توسط AI
{
  "priority": "high",  # low, normal, high, critical
  "type": "LaunchApp",
  "params": {...}
}
```

### هوک‌های سفارشی

```python
from core.execution_manager import ExecutionManager

def my_audit_hook(action, result):
    print(f"اقدام {action} انجام شد: {result}")

executor = ExecutionManager()
executor.add_audit_hook(my_audit_hook)
```

### مانیتورینگ زنده

```python
from core.monitoring_service import MonitoringService

def alert_handler(snapshot):
    if snapshot.cpu_percent > 80:
        print("⚠️  CPU زیاد است!")

monitor = MonitoringService(
    interval_seconds=5,
    alert_callback=alert_handler
)
monitor.start()
```

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: November 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION