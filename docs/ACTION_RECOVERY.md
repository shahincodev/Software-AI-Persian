# سیستم بازیابی اقدامات (Action Recovery)

## نمای کلی

سیستم بازیابی اقدامات یک مکانیزم هوشمند برای مدیریت خطاها و شکست‌های اقدامات است. این سیستم به صورت خودکار اقدامات ناموفق را تکرار کرده، زمان‌بندی را تنظیم می‌کند و در صورت لزوم عملیات rollback انجام می‌دهد.

## ویژگی‌ها

### 🔄 استراتژی‌های بازیابی

- **RETRY**: تلاش مجدد ساده
- **RETRY_WITH_DELAY**: تلاش مجدد با تاخیر
- **ROLLBACK**: بازگشت به حالت قبل
- **SKIP**: رد کردن اقدام
- **ABORT**: لغو کل عملیات

### 📊 طبقه‌بندی خطا

- **CRITICAL**: خطاهای بحرانی (FileNotFoundError، PermissionError)
- **HIGH**: خطاهای مهم (TimeoutError، ConnectionError)
- **MEDIUM**: خطاهای متوسط (ValueError، TypeError)
- **LOW**: خطاهای جزئی (سایر خطاها)

### ⚙️ قابلیت‌های پیشرفته

- **Exponential Backoff**: افزایش تاخیر به صورت نمایی
- **Linear Backoff**: افزایش تاخیر خطی
- **Timeout Management**: مدیریت زمان‌های timeout
- **History Tracking**: ذخیره تاریخچه تلاش‌ها
- **Statistics**: آمار موفقیت/شکست

## نحوه استفاده

### استفاده ساده

```python
from core import ActionRecovery

# ایجاد سیستم recovery
recovery = ActionRecovery()

# اجرای اقدام با recovery
async def my_action():
    # انجام کاری
    return result

action = {"type": "MyAction", "params": {...}}
result = await recovery.execute_with_recovery(my_action, action)

if result.success:
    print(f"موفق شد بعد از {result.attempts} تلاش")
else:
    print(f"شکست خورد: {result.error}")
```

### پیکربندی سفارشی

```python
from core import ActionRecovery, RecoveryConfig

# تنظیمات سفارشی
config = RecoveryConfig(
    max_retries=5,           # حداکثر 5 تلاش
    retry_delay=2.0,         # تاخیر 2 ثانیه
    exponential_backoff=True, # افزایش نمایی
    enable_rollback=True,    # فعال کردن rollback
    timeout=30.0             # حداکثر 30 ثانیه
)

recovery = ActionRecovery(config)
```

## RecoveryConfig

### پارامترها

```python
@dataclass
class RecoveryConfig:
    max_retries: int = 3          # حداکثر تعداد تلاش‌های مجدد
    retry_delay: float = 1.0      # تاخیر اولیه (ثانیه)
    exponential_backoff: bool = True  # افزایش نمایی تاخیر
    enable_rollback: bool = False # فعال‌سازی rollback
    timeout: float = 30.0         # حداکثر زمان اجرا (ثانیه)
```

### مثال‌های پیکربندی

#### پیکربندی تهاجمی (Aggressive)
```python
config = RecoveryConfig(
    max_retries=10,
    retry_delay=0.5,
    exponential_backoff=False,  # خطی
    timeout=60.0
)
```

#### پیکربندی محافظه‌کارانه (Conservative)
```python
config = RecoveryConfig(
    max_retries=2,
    retry_delay=5.0,
    exponential_backoff=True,
    enable_rollback=True,
    timeout=10.0
)
```

## استراتژی‌های بازیابی

### 1. RETRY (تلاش مجدد)
**استفاده:** خطاهای موقت که احتمال موفقیت در تلاش بعدی زیاد است

```python
# مثال: خطای شبکه موقت
async def download_file():
    # ممکن است موقتاً شبکه قطع باشد
    return await http.get(url)

result = await recovery.execute_with_recovery(download_file, action)
```

**خطاهای مناسب:**
- خطاهای شبکه موقت
- Resource busy
- خطاهای تصادفی

### 2. RETRY_WITH_DELAY (تلاش مجدد با تاخیر)
**استفاده:** خطاهایی که نیاز به زمان برای حل شدن دارند

```python
# مثال: منتظر آزاد شدن فایل
async def write_file():
    # ممکن است فایل توسط برنامه دیگری باز باشد
    with open(path, 'w') as f:
        f.write(data)

result = await recovery.execute_with_recovery(write_file, action)
```

**تاخیرها:**
- **Exponential**: 1s → 2s → 4s → 8s
- **Linear**: 1s → 1s → 1s → 1s

### 3. ROLLBACK (بازگشت)
**استفاده:** خطاهای جدی که نیاز به برگشت تغییرات دارند

```python
config = RecoveryConfig(enable_rollback=True)
recovery = ActionRecovery(config)

async def critical_operation():
    # عملیات حیاتی
    await modify_database()

# در صورت خطای HIGH، rollback انجام می‌شود
result = await recovery.execute_with_recovery(critical_operation, action)
```

**شرایط rollback:**
- خطای HIGH یا CRITICAL
- `enable_rollback=True` در config
- تابع `rollback_func` فراهم شده

### 4. SKIP (رد کردن)
**استفاده:** خطاهای کوچک که می‌توان نادیده گرفت

```python
async def optional_logging():
    # لاگ کردن اختیاری
    await log_to_server(data)

# اگر لاگ کردن شکست خورد، مهم نیست
result = await recovery.execute_with_recovery(optional_logging, action)
```

### 5. ABORT (لغو)
**استفاده:** خطاهای بحرانی که ادامه کار بی‌معنی است

```python
async def critical_check():
    if not file_exists(required_file):
        raise FileNotFoundError("فایل ضروری یافت نشد")

# خطای CRITICAL → ABORT
result = await recovery.execute_with_recovery(critical_check, action)
```

## طبقه‌بندی خطا

### CRITICAL (بحرانی)
```python
FileNotFoundError
PermissionError
MemoryError
SystemExit
KeyboardInterrupt
```

**استراتژی:** ABORT (لغو فوری)

### HIGH (بالا)
```python
TimeoutError
ConnectionError
OSError
```

**استراتژی:** ROLLBACK (اگر فعال باشد) یا RETRY_WITH_DELAY

### MEDIUM (متوسط)
```python
ValueError
TypeError
KeyError
IndexError
AttributeError
```

**استراتژی:** RETRY_WITH_DELAY

### LOW (پایین)
```python
# سایر خطاها
Exception
RuntimeError
# ...
```

**استراتژی:** RETRY

## ActionResult

### ساختار

```python
@dataclass
class ActionResult:
    success: bool              # موفقیت یا شکست
    action: Dict[str, Any]     # اقدام اجرا شده
    error: Optional[str]       # پیام خطا (اگر شکست خورد)
    attempts: int              # تعداد تلاش‌ها
    duration: float            # مدت زمان اجرا (ثانیه)
    recovery_strategy: Optional[RecoveryStrategy]  # استراتژی استفاده شده
```

### مثال

```python
result = await recovery.execute_with_recovery(my_action, action)

print(f"موفقیت: {result.success}")
print(f"تلاش‌ها: {result.attempts}")
print(f"مدت: {result.duration:.2f}s")
print(f"استراتژی: {result.recovery_strategy}")

if not result.success:
    print(f"خطا: {result.error}")
```

## تاریخچه و آمار

### دریافت تاریخچه

```python
history = recovery.get_history()

for result in history:
    print(f"{result.action['type']}: {result.success}")
```

### دریافت آمار

```python
stats = recovery.get_statistics()

print(f"کل تلاش‌ها: {stats['total_attempts']}")
print(f"موفق: {stats['successful']}")
print(f"ناموفق: {stats['failed']}")
print(f"نرخ موفقیت: {stats['success_rate']:.1f}%")
print(f"میانگین تلاش: {stats['avg_attempts']:.1f}")
print(f"میانگین زمان: {stats['avg_duration']:.2f}s")
```

### پاک کردن تاریخچه

```python
recovery.clear_history()
```

## مثال‌های کامل

### مثال 1: دانلود فایل با retry

```python
from core import ActionRecovery, RecoveryConfig
import aiohttp

config = RecoveryConfig(
    max_retries=5,
    retry_delay=2.0,
    exponential_backoff=True,
    timeout=30.0
)

recovery = ActionRecovery(config)

async def download_file(url: str, path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            with open(path, 'wb') as f:
                f.write(await response.read())
    return True

action = {
    "type": "DownloadFile",
    "params": {"url": "https://example.com/file.zip", "path": "file.zip"}
}

result = await recovery.execute_with_recovery(
    lambda: download_file(action["params"]["url"], action["params"]["path"]),
    action
)

if result.success:
    print("دانلود موفق!")
else:
    print(f"دانلود ناموفق: {result.error}")
```

### مثال 2: عملیات دیتابیس با rollback

```python
from core import ActionRecovery, RecoveryConfig

config = RecoveryConfig(
    max_retries=3,
    enable_rollback=True,
    timeout=10.0
)

recovery = ActionRecovery(config)

# State اولیه
original_data = []

async def modify_database():
    # ذخیره state قبلی
    global original_data
    original_data = db.get_all()
    
    # تغییرات
    db.insert(new_data)
    db.update(modified_data)
    
    return True

async def rollback():
    # بازگشت به state قبلی
    global original_data
    db.restore(original_data)
    print("Rollback انجام شد")

action = {"type": "DatabaseModify"}

result = await recovery.execute_with_recovery(
    modify_database,
    action,
    rollback_func=rollback
)
```

### مثال 3: عملیات با timeout

```python
from core import ActionRecovery, RecoveryConfig
import asyncio

config = RecoveryConfig(
    max_retries=2,
    timeout=5.0  # حداکثر 5 ثانیه
)

recovery = ActionRecovery(config)

async def slow_operation():
    # عملیات کند
    await asyncio.sleep(10)  # بیش از timeout
    return True

action = {"type": "SlowOperation"}

result = await recovery.execute_with_recovery(slow_operation, action)

if not result.success:
    print(f"Timeout: {result.error}")
```

## بهترین شیوه‌ها

1. **پیکربندی مناسب انتخاب کنید**
   - عملیات سریع: retry کم، timeout کوتاه
   - عملیات کند: retry بیشتر، timeout بلند

2. **از exponential backoff استفاده کنید**
   - برای جلوگیری از فشار به سرویس‌ها
   - زمان کافی برای بازیابی

3. **rollback را برای عملیات حیاتی فعال کنید**
   - عملیات دیتابیس
   - تغییرات فایل سیستم
   - تغییرات پیکربندی

4. **تاریخچه را مانیتور کنید**
   - شناسایی الگوهای خطا
   - بهینه‌سازی پیکربندی

5. **خطاها را لاگ کنید**
   - برای عیب‌یابی
   - تحلیل عملکرد

## عیب‌یابی

### مشکل: همیشه timeout می‌شود

**علت:** timeout خیلی کوتاه است

**راه‌حل:**
```python
config = RecoveryConfig(timeout=60.0)  # افزایش timeout
```

### مشکل: خیلی زیاد retry می‌کند

**علت:** max_retries زیاد است

**راه‌حل:**
```python
config = RecoveryConfig(max_retries=2)  # کاهش تعداد
```

### مشکل: rollback کار نمی‌کند

**علت 1:** `enable_rollback=False`
```python
config = RecoveryConfig(enable_rollback=True)
```

**علت 2:** `rollback_func` داده نشده
```python
await recovery.execute_with_recovery(action, func, rollback_func=my_rollback)
```

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: December 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
