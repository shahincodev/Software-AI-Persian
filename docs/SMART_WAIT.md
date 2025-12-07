# 🕐 Smart Wait - سیستم انتظار هوشمند

> راهنمای جامع سیستم انتظار هوشمند برای خودکارسازی Desktop

---

## 📋 فهرست مطالب

1. [معرفی](#معرفی)
2. [نصب و راه‌اندازی](#نصب-و-راهاندازی)
3. [استراتژی‌های انتظار](#استراتژیهای-انتظار)
4. [API Reference](#api-reference)
5. [مثال‌های کاربردی](#مثالهای-کاربردی)
6. [بهترین شیوه‌ها](#بهترین-شیوهها)
7. [عیب‌یابی](#عیبیابی)
8. [یادداشت‌های فنی](#یادداشتهای-فنی)

---

## معرفی

### چیست؟
`SmartWaiter` یک سیستم انتظار هوشمند است که به برنامه‌های خودکارسازی Desktop اجازه می‌دهد تا به صورت هوشمند منتظر بمانند تا شرایط خاصی برقرار شود. این سیستم با استفاده از استراتژی‌های مختلف انتظار، قابلیت اطمینان و پایداری اسکریپت‌های اتوماسیون را به طور چشمگیری افزایش می‌دهد.

### چرا نیاز است؟
در اتوماسیون Desktop، عملیات‌ها زمان‌های متفاوتی برای اجرا دارند:
- باز شدن برنامه‌ها
- بارگذاری صفحات
- ظاهر شدن دکمه‌ها
- پردازش داده‌ها
- Idle شدن سیستم

استفاده از `time.sleep()` ثابت:
- ❌ اتلاف زمان (اگر خیلی طولانی باشد)
- ❌ شکست اسکریپت (اگر خیلی کوتاه باشد)
- ❌ عدم انعطاف‌پذیری

`SmartWaiter` این مشکلات را حل می‌کند! ✅

### قابلیت‌ها
- ✅ 8 استراتژی انتظار مختلف
- ✅ Timeout قابل تنظیم
- ✅ Retry با Backoff (Linear/Exponential/Fibonacci)
- ✅ آمارگیری و تاریخچه
- ✅ Error handling کامل
- ✅ Integration با DesktopVision

---

## نصب و راه‌اندازی

### پیش‌نیازها
```bash
pip install psutil pillow
```

### استفاده ساده
```python
from core.smart_wait import SmartWaiter

# ایجاد instance
waiter = SmartWaiter()

# انتظار برای Idle شدن سیستم
result = waiter.wait_for_idle(cpu_threshold=10.0, timeout=30)

if result.success:
    print(f"System is idle! (waited {result.duration:.1f}s)")
else:
    print(f"Timeout after {result.duration:.1f}s")
```

---

## استراتژی‌های انتظار

### 1️⃣ انتظار برای عنصر (Element)

منتظر می‌ماند تا متن مشخصی روی صفحه ظاهر شود (با استفاده از OCR).

```python
result = waiter.wait_for_element(
    target="Submit",
    timeout=10,
    confidence=0.8
)
```

**پارامترها:**
- `target` (str): متن مورد نظر
- `timeout` (float): حداکثر زمان انتظار (ثانیه)
- `confidence` (float): حداقل اطمینان OCR (0.0-1.0)
- `check_interval` (float): فاصله بررسی‌ها (پیش‌فرض: 0.5s)

**کاربرد:**
- انتظار برای ظاهر شدن دکمه
- تأیید بارگذاری صفحه
- تشخیص تغییر وضعیت

**مثال:**
```python
# انتظار برای دکمه "OK"
result = waiter.wait_for_element("OK", timeout=15)

if result.success:
    print(f"Button found at: {result.result}")
else:
    print("Button not found within timeout")
```

---

### 2️⃣ انتظار برای تغییر (Change Detection)

منتظر می‌ماند تا صفحه یا ناحیه‌ای از آن تغییر کند.

```python
result = waiter.wait_for_change(
    region=(0, 0, 800, 600),
    threshold=0.95,
    timeout=15
)
```

**پارامترها:**
- `region` (tuple): ناحیه برای بررسی (x, y, width, height)
- `threshold` (float): حداقل شباهت برای تغییر (0.0-1.0)
- `timeout` (float): حداکثر زمان انتظار
- `check_interval` (float): فاصله بررسی‌ها

**کاربرد:**
- انتظار برای بارگذاری محتوا
- تشخیص انیمیشن‌ها
- تأیید تغییرات صفحه

**مثال:**
```python
# انتظار برای تغییر ناحیه مرکزی
result = waiter.wait_for_change(
    region=(300, 200, 800, 600),
    threshold=0.90,
    timeout=20
)

print(f"Change detected after {result.duration:.2f}s")
```

---

### 3️⃣ انتظار برای پنجره (Window)

منتظر می‌ماند تا پنجره با عنوان مشخص باز شود.

```python
result = waiter.wait_for_window(
    title="Notepad",
    timeout=30,
    partial_match=True
)
```

**پارامترها:**
- `title` (str): عنوان پنجره
- `timeout` (float): حداکثر زمان انتظار
- `partial_match` (bool): تطابق جزئی یا دقیق
- `check_interval` (float): فاصله بررسی‌ها

**کاربرد:**
- انتظار برای باز شدن برنامه
- تشخیص دیالوگ‌ها
- Multi-window automation

**مثال:**
```python
# انتظار برای باز شدن Chrome
result = waiter.wait_for_window(
    title="Chrome",
    partial_match=True,
    timeout=20
)

if result.success:
    print(f"Window found: {result.result}")
```

---

### 4️⃣ انتظار برای پروسه (Process)

منتظر می‌ماند تا پروسه شروع یا متوقف شود.

```python
# انتظار برای شروع پروسه
result = waiter.wait_for_process(
    name="chrome.exe",
    wait_for_exit=False,
    timeout=20
)

# انتظار برای توقف پروسه
result = waiter.wait_for_process(
    name="notepad.exe",
    wait_for_exit=True,
    timeout=30
)
```

**پارامترها:**
- `name` (str): نام پروسه
- `wait_for_exit` (bool): انتظار برای توقف یا شروع
- `timeout` (float): حداکثر زمان انتظار
- `check_interval` (float): فاصله بررسی‌ها

**کاربرد:**
- مدیریت چرخه حیات برنامه
- Cleanup operations
- Dependency management

**مثال:**
```python
# شروع برنامه و انتظار برای اجرا
import subprocess
subprocess.Popen(["notepad.exe"])

result = waiter.wait_for_process("notepad.exe", timeout=10)
print("Notepad started!" if result.success else "Failed to start")
```

---

### 5️⃣ انتظار برای Idle (CPU)

منتظر می‌ماند تا CPU کمتر از آستانه مشخص شود.

```python
result = waiter.wait_for_idle(
    cpu_threshold=10.0,
    duration=2.0,
    timeout=60
)
```

**پارامترها:**
- `cpu_threshold` (float): حداکثر درصد CPU (0-100)
- `duration` (float): مدت زمان ثابت بودن در آستانه
- `timeout` (float): حداکثر زمان انتظار
- `check_interval` (float): فاصله بررسی‌ها

**کاربرد:**
- انتظار برای اتمام پردازش
- بهینه‌سازی منابع
- Batch processing

**مثال:**
```python
# انتظار برای Idle شدن قبل از شروع تسک سنگین
result = waiter.wait_for_idle(
    cpu_threshold=15.0,
    duration=3.0,
    timeout=120
)

if result.success:
    # شروع تسک سنگین
    perform_heavy_task()
```

---

### 6️⃣ انتظار برای رنگ (Color)

منتظر می‌ماند تا پیکسل مشخصی به رنگ خاصی تبدیل شود.

```python
result = waiter.wait_for_color(
    x=100,
    y=200,
    color=(255, 0, 0),  # قرمز
    tolerance=10,
    timeout=10
)
```

**پارامترها:**
- `x` (int): مختصات X
- `y` (int): مختصات Y
- `color` (tuple): رنگ RGB مورد نظر
- `tolerance` (int): تلرانس رنگ (0-255)
- `timeout` (float): حداکثر زمان انتظار
- `check_interval` (float): فاصله بررسی‌ها

**کاربرد:**
- تشخیص تغییر وضعیت دکمه‌ها
- شناسایی نوتیفیکیشن‌ها
- بررسی LED ها

**مثال:**
```python
# انتظار برای سبز شدن دکمه
result = waiter.wait_for_color(
    x=500,
    y=300,
    color=(0, 255, 0),  # سبز
    tolerance=20,
    timeout=15
)

print("Button ready!" if result.success else "Button not ready")
```

---

### 7️⃣ Retry با Backoff

اجرای مجدد عملیات با فاصله‌های رو به افزایش.

```python
def risky_operation():
    # عملیاتی که ممکن است شکست بخورد
    return api_call()

result = waiter.retry_with_backoff(
    action=risky_operation,
    max_retries=5,
    initial_delay=1.0,
    strategy=RetryStrategy.EXPONENTIAL,
    max_delay=30.0
)
```

**پارامترها:**
- `action` (Callable): تابع برای اجرا
- `max_retries` (int): حداکثر تعداد تلاش
- `initial_delay` (float): تأخیر اولیه (ثانیه)
- `strategy` (RetryStrategy): LINEAR, EXPONENTIAL, FIBONACCI
- `max_delay` (float): حداکثر تأخیر بین تلاش‌ها

**استراتژی‌ها:**

```python
from core.smart_wait import RetryStrategy

# LINEAR: 1s, 2s, 3s, 4s, 5s
RetryStrategy.LINEAR

# EXPONENTIAL: 1s, 2s, 4s, 8s, 16s
RetryStrategy.EXPONENTIAL

# FIBONACCI: 1s, 1s, 2s, 3s, 5s, 8s
RetryStrategy.FIBONACCI
```

**مثال:**
```python
# Retry با Exponential Backoff
def connect_to_api():
    response = requests.get("https://api.example.com")
    response.raise_for_status()
    return response.json()

result = waiter.retry_with_backoff(
    action=connect_to_api,
    max_retries=5,
    initial_delay=2.0,
    strategy=RetryStrategy.EXPONENTIAL
)

if result.success:
    data = result.result
    print(f"Connected after {result.attempts} attempts")
```

---

### 8️⃣ Polling شرط (Condition)

بررسی مکرر یک شرط تا برقرار شود.

```python
result = waiter.poll_until(
    condition_func=lambda: check_file_exists("output.txt"),
    timeout=30,
    interval=2
)
```

**پارامترها:**
- `condition_func` (Callable): تابع شرط (باید True/False برگرداند)
- `timeout` (float): حداکثر زمان انتظار
- `interval` (float): فاصله بررسی‌ها

**کاربرد:**
- انتظار برای ایجاد فایل
- بررسی وضعیت سرویس
- شرایط سفارشی

**مثال:**
```python
# انتظار برای ایجاد فایل خروجی
def check_output_ready():
    import os
    return os.path.exists("output.txt") and os.path.getsize("output.txt") > 0

result = waiter.poll_until(
    condition_func=check_output_ready,
    timeout=60,
    interval=3
)

if result.success:
    print("Output file is ready!")
```

---

## API Reference

### کلاس SmartWaiter

```python
class SmartWaiter:
    """سیستم انتظار هوشمند برای خودکارسازی Desktop."""
    
    def __init__(
        self,
        vision: Optional[DesktopVision] = None,
        default_timeout: float = 30.0,
        default_interval: float = 0.5
    ):
        """مقداردهی اولیه SmartWaiter.
        
        Args:
            vision: نمونه DesktopVision (اختیاری)
            default_timeout: Timeout پیش‌فرض (ثانیه)
            default_interval: فاصله بررسی پیش‌فرض (ثانیه)
        """
```

### کلاس WaitResult

```python
@dataclass
class WaitResult:
    """نتیجه یک عملیات انتظار."""
    
    success: bool              # موفقیت عملیات
    strategy: str              # استراتژی استفاده شده
    duration: float            # مدت زمان واقعی (ثانیه)
    attempts: int              # تعداد تلاش‌ها
    result: Optional[Any]      # نتیجه (در صورت موفقیت)
    error: Optional[str]       # پیام خطا (در صورت شکست)
    timestamp: datetime        # زمان اجرا
```

### Enum ها

```python
class WaitStrategy(Enum):
    """استراتژی‌های انتظار."""
    ELEMENT = "element"
    CHANGE = "change"
    WINDOW = "window"
    PROCESS = "process"
    IDLE = "idle"
    COLOR = "color"
    CONDITION = "condition"

class RetryStrategy(Enum):
    """استراتژی‌های Retry."""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIBONACCI = "fibonacci"
```

---

## مثال‌های کاربردی

### 1. اتوماسیون نصب نرم‌افزار

```python
from core.smart_wait import SmartWaiter
from core.mouse_control import MouseController
from core.keyboard_control import KeyboardController

waiter = SmartWaiter()
mouse = MouseController()
keyboard = KeyboardController()

# شروع Installer
import subprocess
subprocess.Popen(["setup.exe"])

# انتظار برای پنجره نصب
waiter.wait_for_window("Setup", timeout=30)

# انتظار برای دکمه Next
waiter.wait_for_element("Next", timeout=10)
mouse.click(500, 400)

# انتظار برای اتمام نصب (CPU Idle)
waiter.wait_for_idle(cpu_threshold=5.0, duration=3.0, timeout=300)

# تأیید نصب موفق
result = waiter.wait_for_element("Installation Complete", timeout=10)
print("Installation successful!" if result.success else "Installation failed")
```

### 2. اتوماسیون فرم

```python
# باز کردن فرم
waiter.wait_for_window("Registration Form")

# فیلد نام
waiter.wait_for_element("Name:", timeout=5)
mouse.click(300, 150)
keyboard.type_text("John Doe")

# رفتن به فیلد بعدی
keyboard.press_key('tab')
waiter.wait_for_change(region=(200, 100, 400, 300), threshold=0.9)

# فیلد ایمیل
keyboard.type_text("john@example.com")

# انتظار برای فعال شدن دکمه Submit (تغییر رنگ)
waiter.wait_for_color(
    x=400,
    y=500,
    color=(0, 120, 215),  # آبی
    tolerance=20,
    timeout=5
)

# کلیک Submit
mouse.click(400, 500)

# انتظار برای تأیید
waiter.wait_for_element("Thank you", timeout=15)
```

### 3. Batch Processing با Retry

```python
def process_file(filename):
    """پردازش فایل با احتمال خطا."""
    # ... پردازش ...
    if random.random() < 0.3:  # 30% احتمال خطا
        raise Exception("Processing failed")
    return f"Processed: {filename}"

files = ["file1.txt", "file2.txt", "file3.txt"]

for file in files:
    # انتظار برای Idle شدن قبل از پردازش
    waiter.wait_for_idle(cpu_threshold=20.0, timeout=60)
    
    # پردازش با Retry
    result = waiter.retry_with_backoff(
        action=lambda: process_file(file),
        max_retries=3,
        initial_delay=1.0,
        strategy=RetryStrategy.EXPONENTIAL
    )
    
    if result.success:
        print(result.result)
    else:
        print(f"Failed to process {file}: {result.error}")
```

### 4. مانیتورینگ و انتظار سفارشی

```python
def check_download_complete():
    """بررسی اتمام دانلود."""
    import os
    download_file = "downloads/large_file.zip"
    
    if not os.path.exists(download_file):
        return False
    
    # بررسی اندازه (باید ثابت باشد)
    size1 = os.path.getsize(download_file)
    time.sleep(2)
    size2 = os.path.getsize(download_file)
    
    return size1 == size2 and size1 > 0

# انتظار برای اتمام دانلود
result = waiter.poll_until(
    condition_func=check_download_complete,
    timeout=600,  # 10 دقیقه
    interval=5
)

if result.success:
    print(f"Download completed in {result.duration:.1f}s")
else:
    print("Download timeout!")
```

### 5. Multi-Step Workflow

```python
def automated_workflow():
    """یک جریان کاری کامل خودکار."""
    
    # گام 1: باز کردن برنامه
    subprocess.Popen(["application.exe"])
    if not waiter.wait_for_window("Application", timeout=20).success:
        return "Failed to open application"
    
    # گام 2: انتظار برای بارگذاری کامل
    if not waiter.wait_for_element("Ready", timeout=30).success:
        return "Application not ready"
    
    # گام 3: کلیک روی منو
    waiter.wait_for_element("File")
    mouse.click(50, 30)
    
    # گام 4: انتظار برای باز شدن منو
    waiter.wait_for_change(region=(0, 0, 200, 400))
    
    # گام 5: انتخاب گزینه
    waiter.wait_for_element("Open")
    mouse.click(80, 100)
    
    # گام 6: انتظار برای دیالوگ
    waiter.wait_for_window("Open File", timeout=10)
    
    # گام 7: انتظار برای Idle
    waiter.wait_for_idle(cpu_threshold=10.0, timeout=30)
    
    return "Workflow completed successfully"

# اجرای Workflow با Retry
result = waiter.retry_with_backoff(
    action=automated_workflow,
    max_retries=3,
    initial_delay=5.0,
    strategy=RetryStrategy.LINEAR
)

print(result.result if result.success else result.error)
```

---

## بهترین شیوه‌ها

### ✅ انتخاب استراتژی مناسب

```python
# ❌ اشتباه: استفاده از time.sleep()
time.sleep(10)  # شاید زیادی طولانی یا کوتاه باشد

# ✅ درست: استفاده از wait_for_element
waiter.wait_for_element("Button", timeout=10)
```

### ✅ تنظیم Timeout مناسب

```python
# عملیات سریع
waiter.wait_for_element("OK", timeout=5)

# عملیات متوسط
waiter.wait_for_window("Chrome", timeout=20)

# عملیات سنگین
waiter.wait_for_idle(cpu_threshold=10.0, timeout=300)
```

### ✅ بررسی نتیجه

```python
result = waiter.wait_for_window("App")

if result.success:
    print(f"Success! Duration: {result.duration:.2f}s")
    print(f"Result: {result.result}")
else:
    print(f"Failed after {result.duration:.2f}s")
    print(f"Error: {result.error}")
```

### ✅ استفاده از آمار

```python
# انجام چند عملیات
waiter.wait_for_window("App1")
waiter.wait_for_element("Button")
waiter.wait_for_idle()

# دریافت آمار
stats = waiter.get_statistics()
print(f"Total operations: {stats['total_operations']}")
print(f"Success rate: {stats['success_rate']:.1%}")
print(f"Average duration: {stats['avg_duration']:.2f}s")
```

### ✅ Cleanup و Resource Management

```python
try:
    waiter = SmartWaiter()
    result = waiter.wait_for_window("App", timeout=30)
    # ... operations ...
finally:
    # آزادسازی منابع
    if hasattr(waiter, 'cleanup'):
        waiter.cleanup()
```

---

## عیب‌یابی

### مشکل: Element پیدا نمی‌شود

**علت‌های احتمالی:**
1. OCR نمی‌تواند متن را بخواند
2. Confidence خیلی بالا است
3. Element هنوز ظاهر نشده

**راه‌حل:**
```python
# کاهش confidence
result = waiter.wait_for_element("Submit", confidence=0.6)

# افزایش timeout
result = waiter.wait_for_element("Submit", timeout=30)

# بررسی دستی
from core.desktop_vision import DesktopVision
vision = DesktopVision()
text = vision.read_text_from_screen()
print(f"Detected text: {text}")
```

### مشکل: پنجره پیدا نمی‌شود

**راه‌حل:**
```python
# استفاده از partial_match
result = waiter.wait_for_window("Chrome", partial_match=True)

# بررسی پنجره‌های موجود
vision = DesktopVision()
windows = vision.list_windows()
print(f"Available windows: {windows}")
```

### مشکل: Timeout خیلی زود رخ می‌دهد

**راه‌حل:**
```python
# افزایش check_interval برای عملیات سنگین
result = waiter.wait_for_change(
    region=(0, 0, 800, 600),
    check_interval=2.0,  # بجای 0.5s
    timeout=60
)
```

### مشکل: CPU هیچ‌وقت Idle نمی‌شود

**راه‌حل:**
```python
# افزایش cpu_threshold
result = waiter.wait_for_idle(
    cpu_threshold=20.0,  # بجای 10.0
    duration=1.0,        # کاهش duration
    timeout=60
)
```

### Debug Mode

```python
import logging

# فعال‌سازی لاگ‌های debug
logging.basicConfig(level=logging.DEBUG)

# حالا تمام عملیات لاگ می‌شوند
waiter = SmartWaiter()
result = waiter.wait_for_element("Button")
```

---

## یادداشت‌های فنی

### Performance

```python
# عملیات سنگین: Check interval بیشتر
waiter.wait_for_change(
    region=(0, 0, 1920, 1080),  # تمام صفحه
    check_interval=1.0,          # کاهش بار CPU
    timeout=30
)

# عملیات سبک: Check interval کمتر
waiter.wait_for_color(
    x=100,
    y=200,
    color=(255, 0, 0),
    check_interval=0.1,  # پاسخ سریع‌تر
    timeout=5
)
```

### Memory Management

```python
# برای عملیات طولانی‌مدت
waiter = SmartWaiter()

# ... عملیات زیاد ...

# پاکسازی تاریخچه برای آزاد کردن حافظه
waiter.history.clear()
```

### Threading Considerations

```python
# SmartWaiter thread-safe نیست
# برای استفاده چندنخی، instance جداگانه بسازید

import threading

def worker():
    waiter = SmartWaiter()  # یک instance برای هر thread
    waiter.wait_for_element("Button")

threads = [threading.Thread(target=worker) for _ in range(5)]
for t in threads:
    t.start()
```

---

## مثال جامع

```python
"""اتوماسیون کامل یک فرآیند پیچیده."""

from core.smart_wait import SmartWaiter, RetryStrategy
from core.mouse_control import MouseController
from core.keyboard_control import KeyboardController
from core.desktop_vision import DesktopVision
import subprocess

def main():
    # راه‌اندازی
    waiter = SmartWaiter()
    mouse = MouseController()
    keyboard = KeyboardController()
    vision = DesktopVision()
    
    try:
        # 1. باز کردن برنامه
        print("Opening application...")
        subprocess.Popen(["notepad.exe"])
        
        result = waiter.wait_for_window("Notepad", timeout=10)
        if not result.success:
            raise Exception("Failed to open Notepad")
        
        # 2. انتظار برای آماده شدن
        print("Waiting for application to be ready...")
        waiter.wait_for_idle(cpu_threshold=10.0, timeout=30)
        
        # 3. تایپ متن
        print("Typing text...")
        keyboard.type_text("Hello from Smart Wait!")
        
        # 4. ذخیره فایل
        print("Saving file...")
        keyboard.hotkey('ctrl', 's')
        
        # انتظار برای دیالوگ Save
        waiter.wait_for_window("Save As", timeout=5)
        
        # تایپ نام فایل
        keyboard.type_text("test_output.txt")
        keyboard.press_key('enter')
        
        # 5. انتظار برای ذخیره
        def check_file_saved():
            import os
            return os.path.exists("test_output.txt")
        
        result = waiter.poll_until(
            condition_func=check_file_saved,
            timeout=10,
            interval=1
        )
        
        if result.success:
            print("✅ File saved successfully!")
        else:
            print("❌ Failed to save file")
        
        # 6. آمار
        stats = waiter.get_statistics()
        print(f"\nStatistics:")
        print(f"  Total operations: {stats['total_operations']}")
        print(f"  Success rate: {stats['success_rate']:.1%}")
        print(f"  Average duration: {stats['avg_duration']:.2f}s")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Cleanup
        print("\nCompleted!")

if __name__ == "__main__":
    main()
```

---

## منابع بیشتر

- [Mouse Control Guide](MOUSE_CONTROL.md) - کنترل موس
- [Keyboard Control Guide](KEYBOARD_CONTROL.md) - کنترل کیبورد
- [Desktop Vision Guide](DESKTOP_VISION.md) - بینایی رایانه
- [Automation Guide](../AUTOMATION_GUIDE.md) - راهنمای جامع

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: December 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
