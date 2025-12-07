# 📊 راهنمای جامع سیستم لاگ‌گیری

این راهنما نحوه استفاده از سیستم لاگ‌گیری پیشرفته Software-AI را توضیح می‌دهد.

---

## 🎯 هدف

سیستم لاگ‌گیری طراحی شده تا:
- ✅ **همه چیز را ثبت کند** - از شروع تا پایان هر session
- ✅ **در یک فایل قرار دهد** - آسان برای ارسال و تحلیل
- ✅ **قابل خواندن باشد** - برای انسان و ماشین
- ✅ **تاریخچه کامل** - تمام session ها در master log

---

## 📁 ساختار فایل‌های لاگ

```
data/logs/
├── app.log                      # لاگ چرخشی (10 MB max, 10 backups)
├── master.log                   # 🌟 لاگ اصلی - همه session ها
├── sessions/                    # پوشه session logs
│   ├── session_20251207_143025.log   # Session 1
│   ├── session_20251207_145130.log   # Session 2
│   └── session_20251207_151245.log   # Session 3
└── quick_test_TIMESTAMP.log     # لاگ‌های تست
```

---

## 🌟 انواع فایل‌های لاگ

### 1. **Session Log** (جلسه کاری)
📝 **مسیر:** `data/logs/sessions/session_YYYYMMDD_HHMMSS.log`

**ویژگی‌ها:**
- ✅ یک فایل برای هر بار اجرای برنامه
- ✅ شامل کل لاگ از ابتدا تا انتها
- ✅ Timestamp دقیق در نام فایل
- ✅ **این فایل را برای GitHub Copilot ارسال کنید**

**مثال نام:**
```
session_20251207_143025.log  → 2025/12/07 ساعت 14:30:25
```

**محتوا:**
```
2025-12-07 14:30:25 | INFO    | [__main__:752] | Application started with mode=browser
2025-12-07 14:30:26 | INFO    | [core.intelligent_agent:45] | Intelligent system agent initialized
2025-12-07 14:30:30 | INFO    | [core.master_controller:89] | 🧠 Master AI Controller initialized
...
2025-12-07 14:45:12 | INFO    | [__main__:752] | 🏁 SESSION ENDED: 2025-12-07 14:45:12
```

---

### 2. **Master Log** (لاگ جامع)
📊 **مسیر:** `data/logs/master.log`

**ویژگی‌ها:**
- ✅ **همه session ها** در یک فایل
- ✅ بدون محدودیت حجم
- ✅ تاریخچه کامل پروژه
- ✅ برای تحلیل بلندمدت

**استفاده:**
- بررسی الگوهای خطا در طول زمان
- مقایسه session های مختلف
- Debug مشکلات تکراری

---

### 3. **App Log** (لاگ چرخشی)
🔄 **مسیر:** `data/logs/app.log`

**ویژگی‌ها:**
- ✅ محدودیت: 10 MB
- ✅ Backup: 10 فایل (app.log.1, app.log.2, ...)
- ✅ مناسب برای monitoring روزانه

---

## 🚀 نحوه استفاده

### روش 1: اجرای عادی

```powershell
python main.py
```

**خروجی:**
```
📝 Logging Information:
   Session Log: data\logs\sessions\session_20251207_143025.log
   Master Log:  data\logs\master.log
   ✓ All outputs will be saved to these files
```

---

### روش 2: حالت Debug (لاگ بیشتر)

```powershell
python main.py --debug
```

**تفاوت:**
- ✅ تمام DEBUG messages نمایش داده می‌شوند
- ✅ Traceback کامل برای خطاها
- ✅ اطلاعات داخلی سیستم

---

### روش 3: با Automation

```powershell
python main.py --enable-automation
```

**لاگ اضافی:**
- Mouse movements
- Keyboard inputs
- Screen captures
- Action Controller decisions

---

## 📤 ارسال لاگ به GitHub Copilot

### مرحله 1: پیدا کردن آخرین Session Log

```powershell
# لیست تمام session logs
Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending

# باز کردن آخرین فایل
code (Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
```

---

### مرحله 2: کپی کردن محتوا

**گزینه A: باز کردن در VS Code**
```powershell
code data\logs\sessions\session_20251207_143025.log
```

**گزینه B: کپی به Clipboard**
```powershell
Get-Content data\logs\sessions\session_20251207_143025.log | Set-Clipboard
```

---

### مرحله 3: ارسال به Copilot

در GitHub Copilot Chat بنویسید:
```
من لاگ کامل اجرای برنامه را می‌فرستم. لطفاً تحلیل کن و مشکلات را شناسایی کن:

[محتوای فایل لاگ را اینجا paste کنید]
```

---

## 🔍 تحلیل لاگ‌ها

### یافتن خطاها

**PowerShell:**
```powershell
# تمام خطاها
Select-String "ERROR" data\logs\sessions\session_20251207_143025.log

# تمام هشدارها
Select-String "WARNING" data\logs\sessions\session_20251207_143025.log

# Exception های مهم
Select-String "exception|traceback" data\logs\sessions\session_20251207_143025.log -CaseSensitive:$false
```

---

### آمار Session

**PowerShell:**
```powershell
$log = Get-Content data\logs\sessions\session_20251207_143025.log
$errors = ($log | Select-String "ERROR").Count
$warnings = ($log | Select-String "WARNING").Count
$info = ($log | Select-String "INFO").Count

Write-Host "📊 Session Statistics:"
Write-Host "   Errors:   $errors"
Write-Host "   Warnings: $warnings"
Write-Host "   Info:     $info"
```

---

### مقایسه دو Session

```powershell
# فرق بین دو session
$session1 = Get-Content data\logs\sessions\session_20251207_143025.log
$session2 = Get-Content data\logs\sessions\session_20251207_145130.log

Compare-Object $session1 $session2
```

---

## 📋 فرمت لاگ

### ساختار یک خط لاگ

```
[Timestamp] | [Level] | [Logger:Line] | [Message]
```

**مثال:**
```
2025-12-07 14:30:25 | INFO    | [core.ai_brain:120] | 🤖 Trying model 1/3: normal
```

**توضیحات:**
- `2025-12-07 14:30:25` - زمان دقیق
- `INFO` - سطح لاگ (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `core.ai_brain:120` - فایل و شماره خط
- `🤖 Trying model 1/3: normal` - پیام

---

### سطوح لاگ

| Level | استفاده | مثال |
|-------|---------|------|
| `DEBUG` | اطلاعات تفصیلی | متغیرهای داخلی، flow برنامه |
| `INFO` | رویدادهای عادی | راه‌اندازی، اتمام کار |
| `WARNING` | هشدارها | Fallback به مدل دیگر |
| `ERROR` | خطاهای قابل بازیابی | API call failed |
| `CRITICAL` | خطاهای جدی | سیستم متوقف شد |

---

## 🛠️ عیب‌یابی مشکلات لاگ

### مشکل: فایل لاگ ساخته نمی‌شود

**بررسی:**
```powershell
# آیا پوشه logs وجود دارد؟
Test-Path data\logs

# اگر نه، بساز
New-Item -ItemType Directory -Force -Path data\logs\sessions
```

---

### مشکل: لاگ‌ها خیلی زیاد هستند

**راه حل 1: فقط خطاها**
```powershell
# فیلتر کردن
Select-String "ERROR|CRITICAL" data\logs\sessions\session_*.log > errors_only.txt
```

**راه حل 2: پاک کردن لاگ‌های قدیمی**
```powershell
# حذف session های قدیمی‌تر از 7 روز
Get-ChildItem data\logs\sessions\ | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | Remove-Item
```

---

### مشکل: نمی‌توانم لاگ را باز کنم (خیلی بزرگ است)

**راه حل:**
```powershell
# فقط 100 خط اول
Get-Content data\logs\sessions\session_20251207_143025.log -Head 100

# فقط 100 خط آخر
Get-Content data\logs\sessions\session_20251207_143025.log -Tail 100

# جستجوی خطاها
Select-String "ERROR" data\logs\sessions\session_20251207_143025.log | Select-Object -First 20
```

---

## 💡 نکات مهم

### ✅ بهترین روش‌ها

1. **همیشه session log را نگه دارید**
   - قبل از گزارش مشکل
   - برای مقایسه نسخه‌های مختلف
   - به عنوان مدرک عملکرد

2. **از --debug در صورت مشکل استفاده کنید**
   ```powershell
   python main.py --debug
   ```

3. **لاگ‌های قدیمی را آرشیو کنید**
   ```powershell
   # فشرده‌سازی session های قدیمی
   Compress-Archive -Path data\logs\sessions\session_2025120*.log -DestinationPath logs_archive_Dec2025.zip
   ```

4. **master.log را هر از گاهی بررسی کنید**
   - الگوهای تکراری
   - روندهای مشکل
   - بهبودهای ممکن

---

### ⚠️ خطرات

1. **لاگ‌ها حجیم می‌شوند**
   - Master log محدودیت ندارد
   - هر چند وقت یکبار پاک کنید یا آرشیو کنید

2. **اطلاعات حساس**
   - API keys در exception ها ممکن است لاگ شوند
   - قبل از اشتراک‌گذاری بررسی کنید

3. **Performance**
   - لاگ زیاد = کندی
   - در production از INFO یا WARNING استفاده کنید

---

## 🎯 خلاصه سریع

**برای ارسال به Copilot:**
```powershell
# 1. اجرای برنامه
python main.py

# 2. پیدا کردن آخرین لاگ
code (Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName

# 3. کپی و ارسال به Copilot
```

**برای debug:**
```powershell
python main.py --debug
```

**برای تحلیل:**
```powershell
Select-String "ERROR|WARNING" data\logs\sessions\session_*.log
```

---

## 📚 منابع بیشتر

- `data/logs/app.log` - لاگ روزانه
- `data/logs/master.log` - تاریخچه کامل
- `data/logs/sessions/` - لاگ هر اجرا

**موفق باشید! 🎉**

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: November 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
