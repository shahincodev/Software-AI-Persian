# 🎯 راهنمای استفاده بهینه از سیستم لاگ‌گیری
## Best Practices Guide for Advanced Logging System

---

## 📌 پاسخ سوالات مهم

### ✅ آیا با Kill کردن Terminal لاگ‌ها ذخیره می‌شن؟

**بله! کاملاً ذخیره می‌شن.** 

**چرا؟**
1. **Auto-Flush**: هر لاگ بلافاصله روی دیسک نوشته می‌شه
2. **No Buffering**: بافر کردن وجود نداره
3. **Atomic Writes**: هر خط به صورت مستقل نوشته می‌شه

**تست کنید:**
```bash
# Terminal 1
python main.py --input-mode text

# بعد از چند دستور، Terminal رو Kill کنید (Ctrl+C یا بستن پنجره)

# Terminal 2  
python tools/log_analyzer.py recent -n 10
```

✅ همه لاگ‌ها ثبت شدن!

---

## 🎓 استفاده بهینه - سطح مبتدی

### 1. استفاده خودکار (توصیه می‌شه!)

فقط برنامه رو اجرا کنید - **همه چیز خودکار لاگ می‌شه:**

```bash
python main.py --input-mode text
```

**چی لاگ می‌شه؟**
- ✅ تمام دستورات شما
- ✅ تمام درخواست‌های AI
- ✅ تمام خطاها
- ✅ تمام عملیات سیستمی

**کاری لازم نیست!** سیستم همه چیز رو خودکار ثبت می‌کنه.

### 2. مشاهده لاگ‌های اخیر

```bash
# آخرین 20 لاگ
python tools/log_analyzer.py recent -n 20

# فقط خطاها
python tools/log_analyzer.py errors

# آمار کلی
python tools/log_analyzer.py stats
```

### 3. جستجوی مشکل خاص

```bash
# پیدا کردن لاگ‌های مربوط به Notepad
python tools/log_analyzer.py search "notepad"

# پیدا کردن خطای خاص
python tools/log_analyzer.py search "FileNotFoundError"
```

---

## 🚀 استفاده بهینه - سطح پیشرفته

### 1. لاگ دستی در کد خودتان

```python
from core.advanced_logging import get_advanced_logger

logger = get_advanced_logger()

# لاگ عملیات معمولی
logger.log_system("Starting backup process")

# لاگ اقدام کاربر
logger.log_user_action("save_file", {
    "filename": "test.txt",
    "size": 1024
}, success=True)

# لاگ خطا
try:
    risky_operation()
except Exception as e:
    logger.log_exception(e, "Failed to backup", {
        "user": "admin",
        "path": "/backup"
    })
```

### 2. استفاده از Decorators (بهترین روش!)

```python
from core.logging_decorators import log_function_call, log_user_action

# لاگ خودکار تابع
@log_function_call(log_args=True, log_result=True)
def process_data(data):
    """این تابع خودکار لاگ می‌شه - کد اضافی نمی‌خواد!"""
    result = data * 2
    return result

# لاگ اقدام کاربر
@log_user_action("delete_file")
def delete_file(filename):
    """هر بار که فایل حذف شه، لاگ می‌شه"""
    os.remove(filename)
```

**مزیت:** صفر خط کد اضافی! فقط decorator اضافه کنید.

### 3. Context Manager برای بلوک‌های کد

```python
from core.logging_decorators import LogContext

# زمان‌سنجی خودکار
with LogContext("image_processing", {"image_count": 100}):
    for img in images:
        process_image(img)
    # اگر خطا رخ بده، خودکار لاگ می‌شه
    # زمان اجرا هم خودکار ثبت می‌شه
```

**مزیت:** خطاها و زمان اجرا خودکار ثبت می‌شه.

---

## 📊 بهترین روش‌ها (Best Practices)

### ✅ DO (این کارها رو بکنید)

#### 1. از Decorators استفاده کنید
```python
# ✅ GOOD - خودکار
@log_function_call()
def important_function():
    pass
```

```python
# ❌ BAD - دستی و طولانی
def important_function():
    logger = get_advanced_logger()
    logger.log_system("Function started")
    try:
        # code
        logger.log_system("Function completed")
    except Exception as e:
        logger.log_exception(e)
```

#### 2. Context اضافه کنید
```python
# ✅ GOOD - با جزئیات
logger.log_error("Failed to save", "IOError", {
    "filename": file_path,
    "user_id": user.id,
    "timestamp": datetime.now()
})
```

```python
# ❌ BAD - بدون جزئیات
logger.log_error("Error happened")
```

#### 3. از log_exception برای خطاها استفاده کنید
```python
# ✅ GOOD - Stack trace کامل
try:
    risky_operation()
except Exception as e:
    logger.log_exception(e, "Operation failed", {"param": value})
```

```python
# ❌ BAD - Stack trace نداریم
except Exception as e:
    logger.log_error(str(e))
```

#### 4. لاگ‌های مهم رو بررسی کنید
```bash
# ✅ روزانه چک کنید
python tools/log_analyzer.py errors
python tools/log_analyzer.py stats
```

### ❌ DON'T (این کارها رو نکنید)

#### 1. Log Spam نکنید
```python
# ❌ BAD - خیلی زیاد لاگ می‌کنه
for i in range(1000000):
    logger.log_system(f"Processing {i}")  # 1 میلیون لاگ!
```

```python
# ✅ GOOD - فقط مهم‌ها
with LogContext("batch_processing", {"count": 1000000}):
    for i in range(1000000):
        process(i)  # فقط 1 لاگ برای کل batch
```

#### 2. اطلاعات حساس لاگ نکنید
```python
# ❌ BAD - رمز عبور در لاگ!
logger.log_user_action("login", {"password": user_password})
```

```python
# ✅ GOOD - بدون اطلاعات حساس
logger.log_user_action("login", {"username": username})
```

#### 3. لاگ‌ها رو نادیده نگیرید
```python
# ❌ BAD - خطا رو ignore می‌کنه
try:
    important_operation()
except:
    pass  # هیچی لاگ نمی‌شه!
```

```python
# ✅ GOOD - همه خطاها لاگ می‌شن
try:
    important_operation()
except Exception as e:
    logger.log_exception(e, "Important operation failed")
    # یا حتی بهتر:
    raise  # خطا رو هم throw کن
```

---

## 🎯 الگوهای استفاده (Usage Patterns)

### Pattern 1: API Request/Response Logging

```python
@log_ai_interaction("gpt-4")
async def call_ai_api(prompt: str):
    """خودکار هم request و هم response لاگ می‌شه"""
    response = await ai_client.chat(prompt)
    return response
```

**لاگ شده:**
- ✅ زمان شروع
- ✅ Prompt
- ✅ Model
- ✅ Response
- ✅ Token count
- ✅ مدت زمان

### Pattern 2: Error Recovery with Logging

```python
from core.logging_decorators import LogContext

def safe_operation():
    """عملیات با error recovery"""
    with LogContext("file_operation"):
        try:
            # Main operation
            result = risky_operation()
            return result
        except FileNotFoundError as e:
            logger.log_exception(e, "File not found, using default")
            return default_value()
        except PermissionError as e:
            logger.log_exception(e, "Permission denied, retrying")
            return retry_with_sudo()
```

### Pattern 3: Performance Monitoring

```python
import time
from core.logging_decorators import LogContext

def monitored_operation():
    """عملیات با performance tracking"""
    with LogContext("database_query", {"table": "users"}):
        # Query
        results = db.query("SELECT * FROM users")
        # زمان اجرا خودکار لاگ می‌شه
        return results
```

**یا با decorator:**

```python
@log_function_call(log_args=True, log_result=True)
def query_database(table: str):
    """خودکار timing می‌شه"""
    return db.query(f"SELECT * FROM {table}")
```

### Pattern 4: User Action Audit Trail

```python
from core.logging_decorators import log_user_action

@log_user_action("file_delete")
def delete_file(user_id: int, file_path: str):
    """تمام حذف‌های فایل لاگ می‌شه برای Audit"""
    os.remove(file_path)

@log_user_action("settings_change")
def update_settings(user_id: int, settings: dict):
    """تمام تغییرات تنظیمات لاگ می‌شه"""
    save_settings(settings)
```

---

## 📂 ساختار فایل‌های لاگ

### لاگ‌های روزمره که باید چک کنید:

```
data/logs/
├── errors.log              ← روزانه چک کنید
├── user_actions.jsonl      ← برای Audit
└── app.log                 ← Overview کلی
```

### لاگ‌های Debugging:

```
data/logs/
├── debug.log              ← تمام جزئیات
├── full_trace.jsonl       ← برای تحلیل برنامه‌نویسی
└── session_*.jsonl        ← لاگ این اجرا
```

### لاگ‌های تخصصی:

```
data/logs/
├── ai_interactions.jsonl  ← برای بررسی هزینه AI
└── security.jsonl         ← برای Security Audit
```

---

## 🔧 تنظیمات بهینه

### تنظیمات پیش‌فرض (توصیه می‌شه):

```python
# در core/advanced_logging.py
maxBytes=10 * 1024 * 1024  # 10MB - مناسب برای اکثر موارد
backupCount=10              # 10 backup - ~100MB total
```

### برای پروژه‌های بزرگ:

```python
maxBytes=50 * 1024 * 1024  # 50MB
backupCount=20              # 20 backup - ~1GB total
```

### برای پروژه‌های کوچک:

```python
maxBytes=1 * 1024 * 1024   # 1MB
backupCount=5               # 5 backup - ~5MB total
```

---

## 🚨 عیب‌یابی (Troubleshooting)

### مشکل: لاگ‌ها ذخیره نمی‌شن

```bash
# بررسی دسترسی
ls -la data/logs/

# اجازه نوشتن داره؟
# Windows:
icacls "data\logs"

# اگر نه:
mkdir -p data/logs
chmod 755 data/logs
```

### مشکل: لاگ‌ها خیلی بزرگ شدن

```bash
# حذف لاگ‌های قدیمی
rm data/logs/*.log.*
rm data/logs/session_*.jsonl

# نگه داشتن فقط امروز
python -c "
from pathlib import Path
from datetime import datetime
today = datetime.now().strftime('%Y%m%d')
for f in Path('data/logs').glob('session_*.jsonl'):
    if today not in f.name:
        f.unlink()
"
```

### مشکل: نمی‌تونم لاگ‌ها رو بخونم

```bash
# JSON خراب شده؟
python tools/log_analyzer.py recent -n 5

# فایل قفل شده؟
# برنامه رو ببندید و دوباره تلاش کنید
```

---

## 📈 تحلیل عملکرد

### روزانه (Daily):

```bash
# چک خطاها
python tools/log_analyzer.py errors

# آمار کلی
python tools/log_analyzer.py stats
```

### هفتگی (Weekly):

```bash
# تحلیل Session ها
python tools/log_analyzer.py sessions

# Export برای تحلیل بیشتر
python tools/log_analyzer.py export -o weekly_report.json
```

### ماهیانه (Monthly):

```bash
# پاک‌سازی لاگ‌های قدیمی
find data/logs -name "session_*.jsonl" -mtime +30 -delete

# Backup
tar -czf logs_backup_$(date +%Y%m).tar.gz data/logs/
```

---

## 💡 نکات حرفه‌ای

### 1. استفاده در Production

```python
# در main.py
from core.advanced_logging import get_advanced_logger
import atexit

logger = get_advanced_logger()

# اطمینان از ذخیره لاگ‌ها هنگام خروج
def cleanup():
    logger.log_system("Application shutting down")
    from core.advanced_logging import close_advanced_logger
    close_advanced_logger()

atexit.register(cleanup)
```

### 2. Integration با Monitoring Tools

```python
# Export برای Datadog/Splunk
python tools/log_analyzer.py export -o /var/log/app/metrics.json

# یا در کد:
import json
from tools.log_analyzer import LogAnalyzer

analyzer = LogAnalyzer()
logs = analyzer.load_logs("data/logs/full_trace.jsonl")
with open("/var/log/app/export.json", "w") as f:
    json.dump(logs, f)
```

### 3. Custom Alerts

```python
# چک کردن تعداد خطاها
from tools.log_analyzer import LogAnalyzer

analyzer = LogAnalyzer()
analyzer.load_logs("data/logs/full_trace.jsonl")
errors = analyzer.filter_logs(level="ERROR")

if len(errors) > 100:
    send_alert("Too many errors!")
```

---

## 🎯 Checklist استفاده بهینه

### قبل از شروع پروژه:
- [ ] سیستم لاگ تست شده؟ (`python test_system.py`)
- [ ] دایرکتوری `data/logs` وجود داره؟
- [ ] دسترسی نوشتن داریم؟

### در حین توسعه:
- [ ] توابع مهم با `@log_function_call` دکوریت شدن؟
- [ ] خطاها با `log_exception` لاگ می‌شن؟
- [ ] اقدامات کاربر با `@log_user_action` ثبت می‌شن؟

### قبل از Release:
- [ ] همه خطاها رفع شدن؟ (`python tools/log_analyzer.py errors`)
- [ ] لاگ‌های اضافی حذف شدن؟
- [ ] Performance مشکلی نداره؟ (چک کردن `log_performance`)

### بعد از Deploy:
- [ ] لاگ‌ها دارن ذخیره می‌شن؟
- [ ] Rotation کار می‌کنه؟
- [ ] فضای دیسک کافیه؟

---

## 📚 مثال‌های واقعی

### Example 1: Web Scraper با Logging

```python
from core.advanced_logging import get_advanced_logger
from core.logging_decorators import log_function_call, LogContext

logger = get_advanced_logger()

@log_function_call(log_args=True)
def scrape_website(url: str):
    """Scrape با لاگ کامل"""
    with LogContext("web_scraping", {"url": url}):
        try:
            response = requests.get(url)
            data = parse_html(response.text)
            logger.log_system(f"Scraped {len(data)} items")
            return data
        except requests.RequestException as e:
            logger.log_exception(e, "Scraping failed", {"url": url})
            return []
```

### Example 2: File Processor با Error Recovery

```python
@log_user_action("batch_process")
def process_files(directory: str):
    """پردازش فایل‌ها با logging و recovery"""
    files = Path(directory).glob("*.txt")
    
    with LogContext("batch_processing", {"dir": directory}):
        for file_path in files:
            try:
                process_file(file_path)
            except Exception as e:
                logger.log_exception(e, f"Failed: {file_path}")
                continue  # ادامه با فایل بعدی
```

### Example 3: AI Assistant با Full Logging

```python
from core.logging_decorators import log_ai_interaction

@log_ai_interaction("gpt-4")
def ai_chat(user_message: str):
    """تمام AI interaction ها لاگ می‌شه"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_message}]
    )
    return response.choices[0].message.content
```

---

## 🎉 نتیجه‌گیری

### سیستم لاگ شما:
- ✅ خودکار همه چیز رو ثبت می‌کنه
- ✅ حتی با Kill کردن Terminal ذخیره می‌شه
- ✅ ابزار تحلیل قدرتمند داره
- ✅ Production-ready هست

### یادتون باشه:
1. **از Decorators استفاده کنید** → کد تمیزتر
2. **لاگ‌ها رو چک کنید** → مشکلات رو زودتر پیدا کنید
3. **Context اضافه کنید** → Debugging راحت‌تر
4. **لاگ‌های قدیمی رو پاک کنید** → فضا صرفه‌جویی

---

**موفق باشید! 🚀**

هر سوالی داشتید، لاگ‌ها پاسخ دارن! 😊

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: December 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
