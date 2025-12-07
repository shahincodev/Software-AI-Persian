# 📊 راهنمای سیستم لاگ‌گیری پیشرفته

## 🎯 معرفی

سیستم لاگ‌گیری پیشرفته Software-AI یک سیستم کامل و جامع برای ثبت، تحلیل و گزارش‌گیری از تمام رویدادها است.

## ✨ ویژگی‌ها

- ✅ **ثبت خودکار همه اقدامات**: هر کاری که انجام می‌دهید، ثبت می‌شود
- ✅ **دسته‌بندی لاگ‌ها**: System, User Action, AI Request/Response, Error, Security, Performance
- ✅ **لاگ‌های جداگانه**: هر نوع رویداد در فایل مخصوص خود
- ✅ **Session Tracking**: هر اجرا یک session جداگانه دارد
- ✅ **فرمت JSON**: امکان تحلیل و پردازش خودکار
- ✅ **گزارش خطاها**: تولید خودکار گزارش خطاها
- ✅ **آمار و تحلیل**: ابزار قدرتمند برای تحلیل لاگ‌ها

## 📁 ساختار فایل‌های لاگ

```
data/logs/
├── app.log                      # لاگ اصلی (text format)
├── errors.log                   # فقط خطاها (text format)
├── debug.log                    # تمام جزئیات (text format)
├── user_actions.jsonl           # اقدامات کاربر (JSON Lines)
├── ai_interactions.jsonl        # تعاملات با AI (JSON Lines)
├── security.jsonl               # رویدادهای امنیتی (JSON Lines)
├── full_trace.jsonl             # همه چیز (JSON Lines)
├── session_YYYYMMDD_HHMMSS.jsonl  # لاگ session خاص
└── error_report_*.txt           # گزارش خطاها
```

## 🚀 استفاده در کد

### 1. فعال‌سازی لاگ‌گیری پیشرفته

```python
from core.advanced_logging import get_advanced_logger

# دریافت logger
logger = get_advanced_logger()
```

### 2. ثبت رویدادهای مختلف

```python
# رویداد سیستمی
logger.log_system("Application started", {"version": "1.0.0"})

# اقدام کاربر
logger.log_user_action("open_notepad", {"file": "test.txt"}, success=True)

# درخواست AI
logger.log_ai_request("سلام", "gpt-4", {"temperature": 0.7})

# پاسخ AI
logger.log_ai_response("سلام! چطور می‌تونم کمکت کنم؟", "gpt-4", success=True)

# خطا
logger.log_error("Failed to open file", "FileNotFoundError", {"path": "/test.txt"})

# استثنا
try:
    # کد شما
    pass
except Exception as e:
    logger.log_exception(e, "Error processing request", {"user_id": 123})

# امنیت
logger.log_security("Unauthorized access attempt", "high", {"ip": "1.2.3.4"})

# عملکرد
logger.log_performance("database_query", 0.156, {"query": "SELECT ..."})
```

### 3. استفاده از Decorator ها (پیشنهادی)

```python
from core.logging_decorators import (
    log_function_call,
    log_async_function_call,
    log_user_action,
    log_ai_interaction,
    LogContext
)

# لاگ خودکار تابع
@log_function_call(log_args=True, log_result=True)
def process_data(data):
    return data.upper()

# لاگ تابع async
@log_async_function_call()
async def fetch_data():
    return await some_async_function()

# لاگ اقدام کاربر
@log_user_action("save_file")
def save_file(filename):
    with open(filename, 'w') as f:
        f.write("content")

# لاگ تعامل AI
@log_ai_interaction("gpt-4")
async def ask_ai(prompt):
    return await ai.ask(prompt)

# استفاده از Context Manager
with LogContext("processing_large_file", {"file": "data.csv"}):
    # کد شما
    process_file("data.csv")
```

## 🔍 تحلیل لاگ‌ها

### استفاده از ابزار log_analyzer

```bash
# نمایش 20 لاگ اخیر
python tools/log_analyzer.py recent -n 20

# نمایش فقط خطاها
python tools/log_analyzer.py errors -n 50

# نمایش آمار
python tools/log_analyzer.py stats

# جستجو در لاگ‌ها
python tools/log_analyzer.py search "notepad"

# صادرات خطاها
python tools/log_analyzer.py export -o my_errors.json

# لیست تمام session ها
python tools/log_analyzer.py sessions

# فیلتر بر اساس دسته
python tools/log_analyzer.py recent -n 50 -c user_action
```

### استفاده از Python

```python
from tools.log_analyzer import LogAnalyzer

# ایجاد analyzer
analyzer = LogAnalyzer()

# بارگذاری لاگ‌ها
analyzer.load_logs("full_trace.jsonl")

# نمایش آمار
analyzer.show_statistics()

# نمایش خطاها
analyzer.show_errors()

# جستجو
analyzer.search("error")

# فیلتر
filtered = analyzer.filter_logs(
    category="user_action",
    level="ERROR",
    search="notepad"
)

# صادرات
analyzer.export_errors("errors.json")
```

## 📊 گزارش خطاها

گزارش خطاها به طور خودکار در پایان هر session تولید می‌شود:

```python
from core.advanced_logging import get_advanced_logger

logger = get_advanced_logger()

# تولید گزارش
report_path = logger.generate_error_report()
print(f"Error report: {report_path}")
```

فایل گزارش شامل:
- آمار کلی
- لیست تمام خطاها
- Stack trace ها
- جزئیات کامل

## 🎨 فرمت لاگ‌های JSON

### User Action
```json
{
  "timestamp": "2025-12-02T16:30:45.123456",
  "session_id": "20251202_163000",
  "category": "user_action",
  "action": "open_notepad",
  "success": true,
  "details": {
    "file": "test.txt",
    "duration": 0.15
  }
}
```

### AI Request
```json
{
  "timestamp": "2025-12-02T16:30:46.123456",
  "session_id": "20251202_163000",
  "category": "ai_request",
  "prompt": "سلام چطوری؟",
  "prompt_length": 12,
  "model": "gpt-4",
  "parameters": {
    "temperature": 0.7
  }
}
```

### Error
```json
{
  "timestamp": "2025-12-02T16:30:47.123456",
  "session_id": "20251202_163000",
  "category": "error",
  "exception_type": "ValueError",
  "exception_message": "Invalid input",
  "stack_trace": "Traceback ...",
  "context": "Processing user input",
  "extra": {
    "user_input": "xyz"
  }
}
```

## 💡 نکات و توصیه‌ها

### 1. حجم لاگ‌ها
- فایل‌های لاگ به طور خودکار rotate می‌شوند
- حداکثر حجم هر فایل: 10 MB
- تعداد نسخه backup: 10

### 2. عملکرد
- لاگ‌گیری async و غیرمسدودکننده است
- تأثیر کمی روی performance دارد
- فقط در DEBUG mode جزئیات کامل ثبت می‌شود

### 3. حریم خصوصی
- رمزهای عبور لاگ نمی‌شوند
- اطلاعات حساس فیلتر می‌شوند
- متن‌های طولانی به 500 کاراکتر محدود می‌شوند

### 4. بهترین روش‌ها
```python
# ✅ خوب - استفاده از decorator
@log_user_action("save_file")
def save_file(filename):
    pass

# ✅ خوب - Context manager
with LogContext("batch_process"):
    process_batch()

# ❌ بد - لاگ دستی زیاد
logger.log_system("start")
logger.log_system("processing")
logger.log_system("done")

# ✅ بهتر
with LogContext("operation"):
    # کد شما
    pass
```

## 🔧 تنظیمات پیشرفته

### تغییر سطح لاگ‌گیری

```python
# در main.py یا هر جای دیگر
import logging
logging.getLogger("debug").setLevel(logging.DEBUG)  # همه جزئیات
logging.getLogger("main").setLevel(logging.INFO)    # عادی
```

### تغییر مسیر لاگ‌ها

```python
from pathlib import Path
from core.advanced_logging import AdvancedLogger

logger = AdvancedLogger()
logger.base_dir = Path("custom/log/path")
```

## 📧 ارسال گزارش خطا

برای ارسال گزارش خطا به توسعه‌دهنده:

1. اجرای برنامه تا خطا رخ دهد
2. پیدا کردن فایل `error_report_*.txt` در `data/logs/`
3. ارسال این فایل

همچنین می‌توانید فایل session کامل را ارسال کنید:
```
data/logs/session_YYYYMMDD_HHMMSS.jsonl
```

## 🎯 مثال کامل

```python
from core.advanced_logging import get_advanced_logger, close_advanced_logger
from core.logging_decorators import log_user_action, LogContext

# دریافت logger
logger = get_advanced_logger()

try:
    # شروع برنامه
    logger.log_system("Application started", {"version": "1.0.0"})
    
    # اقدام کاربر
    with LogContext("user_workflow"):
        @log_user_action("process_data")
        def process_data():
            # کد شما
            logger.log_system("Processing data")
            return "result"
        
        result = process_data()
        logger.log_system("Workflow completed", {"result": result})

except Exception as e:
    # ثبت خطا
    logger.log_exception(e, "Application error")

finally:
    # بستن و تولید گزارش
    logger.generate_error_report()
    close_advanced_logger()
```

## 🆘 عیب‌یابی

### لاگ‌ها ثبت نمی‌شوند؟
```python
# بررسی مسیر
logger = get_advanced_logger()
print(logger.base_dir)

# بررسی مجوزها
import os
print(os.access("data/logs", os.W_OK))
```

### حجم لاگ‌ها زیاد است؟
```bash
# پاک کردن لاگ‌های قدیمی
cd data/logs
rm *.log.* *.jsonl.*
```

### جستجوی سریع
```bash
# grep در فایل‌های لاگ
grep -i "error" data/logs/app.log

# جستجو در JSON Lines
cat data/logs/full_trace.jsonl | grep "error"
```

## 📚 مستندات بیشتر

- [core/advanced_logging.py](../core/advanced_logging.py) - کد اصلی
- [core/logging_decorators.py](../core/logging_decorators.py) - Decorator ها
- [tools/log_analyzer.py](../tools/log_analyzer.py) - ابزار تحلیل

---

**نکته:** این سیستم لاگ‌گیری کامل برای debugging، monitoring، و troubleshooting طراحی شده است. هر مشکلی که دارید، در لاگ‌ها قابل ردیابی است! 🚀

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: December 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
