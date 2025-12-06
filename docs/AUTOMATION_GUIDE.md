# 🤖 راهنمای استفاده از قابلیت‌های خودکارسازی AI-Powered

## 🧠 تفاوت اصلی: 100% AI-Powered

**قبلاً (Hard-Coded):**
- ❌ فقط 13 برنامه شناخته شده
- ❌ لیست ثابت: Notepad, Chrome, Calculator...
- ❌ نمی‌توانست Steam یا Discord را باز کند

**الان (AI-Powered):**
- ✅ **هر برنامه‌ای** را می‌شناسد
- ✅ AI نام برنامه را استخراج می‌کند
- ✅ Steam, Discord, Telegram، هر چیزی!
- ✅ فارسی کامل: "استیم" → steam.exe

## نصب و راه‌اندازی

### نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

## حالت‌های اجرا

### 1. حالت معمولی (بدون خودکارسازی)
```bash
python main.py --input-mode text
```

### 2. حالت با خودکارسازی دسکتاپ
```bash
python main.py --input-mode text --enable-automation
```

### 3. حالت صوتی با خودکارسازی
```bash
python main.py --input-mode voice --enable-automation
```

### 4. رابط گرافیکی نمایشی
```bash
python main.py --demo-gui
```

یا به صورت مستقیم:
```bash
python demo_gui.py
```

## دستورات خودکارسازی

### 🖱️ کنترل موس (Mouse Control)

#### دریافت موقعیت موس
```
mouse position
```
یا به فارسی:
```
موس موقعیت
```

**خروجی:**
```
🖱️ Mouse position: (640, 480)
```

#### کلیک در موقعیت فعلی
```
mouse click
```
یا به فارسی:
```
موس کلیک
```

**توضیح:** موس در موقعیت فعلی کلیک می‌کند.

---

### ⌨️ کنترل کیبورد (Keyboard Control)

#### تایپ متن
```
type Hello World!
```
یا به فارسی:
```
تایپ سلام دنیا!
```

**توضیح:** 
- سیستم 3 ثانیه صبر می‌کند
- سپس متن را در محل فعال تایپ می‌کند
- از زبان‌های فارسی و انگلیسی پشتیبانی می‌کند

#### اجرای کلید میانبر
```
keyboard hotkey
```

**مثال‌های کلید میانبر:**
- `Ctrl+C` - کپی
- `Ctrl+V` - پیست
- `Alt+Tab` - تعویض پنجره
- `Win+R` - اجرای برنامه

---

### ⏳ انتظار هوشمند (Smart Wait)

#### انتظار برای Idle بودن سیستم
```
wait idle
```
یا به فارسی:
```
صبر بیکار
```

**توضیح:** منتظر می‌ماند تا CPU کمتر از 10% باشد (حداکثر 30 ثانیه).

**خروجی موفق:**
```
✅ System is idle (waited 5.2s)
```

#### انتظار برای پنجره خاص
```
wait window Notepad
```
یا:
```
wait window Visual Studio Code
```

به فارسی:
```
صبر پنجره یادداشت
```

**توضیح:** منتظر می‌ماند تا پنجره با نام مشخص باز شود (حداکثر 30 ثانیه).

---

## سناریوهای کاربردی

### 1️⃣ باز کردن برنامه و تایپ متن
```bash
# گام 1: باز کردن Notepad
open notepad

# گام 2: انتظار برای باز شدن پنجره
wait window Notepad

# گام 3: تایپ متن
type This is a test message!
```

### 2️⃣ اتوماسیون فرم
```bash
# باز کردن مرورگر
open chrome

# انتظار برای باز شدن
wait window Chrome

# تایپ آدرس
type https://example.com

# فشار دادن Enter
keyboard hotkey
```

### 3️⃣ کار با چند پنجره
```bash
# دریافت موقعیت برای کلیک
mouse position

# کلیک روی دکمه
mouse click

# انتظار برای پردازش
wait idle

# تایپ در فیلد بعدی
type Next input here
```

---

## قابلیت‌های پیشرفته

### 🎯 Smart Wait Strategies

#### 1. انتظار برای عنصر (Element)
```python
from core.smart_wait import SmartWaiter

waiter = SmartWaiter()
result = waiter.wait_for_element("Submit", timeout=10)
```

#### 2. انتظار برای تغییر صفحه (Change Detection)
```python
result = waiter.wait_for_change(
    region=(0, 0, 800, 600),
    threshold=0.95,
    timeout=15
)
```

#### 3. انتظار برای پروسه (Process)
```python
result = waiter.wait_for_process("chrome.exe", timeout=20)
```

#### 4. انتظار برای رنگ خاص (Color)
```python
result = waiter.wait_for_color(
    x=100,
    y=200,
    color=(255, 0, 0),  # قرمز
    tolerance=10,
    timeout=10
)
```

#### 5. Retry با Backoff
```python
def risky_operation():
    # عملیات ممکن است شکست بخورد
    return some_api_call()

result = waiter.retry_with_backoff(
    action=risky_operation,
    max_retries=5,
    strategy=RetryStrategy.EXPONENTIAL
)
```

#### 6. Polling شرط
```python
result = waiter.poll_until(
    condition_func=lambda: check_file_exists("output.txt"),
    timeout=30,
    interval=2
)
```

---

## 🖥️ رابط گرافیکی (Demo GUI)

رابط گرافیکی شامل:

### بخش‌ها:
1. **Voice Control** 🎤
   - دکمه Listen - شنیدن دستور
   - دکمه Process - پردازش دستور

2. **Desktop Vision** 👁️
   - Screenshot - گرفتن تصویر
   - OCR Scan - خواندن متن

3. **Mouse Control** 🖱️
   - Get Position - موقعیت موس
   - Click Demo - نمایش کلیک

4. **Keyboard Control** ⌨️
   - Type Text - تایپ متن
   - Hotkey Demo - کلید میانبر

5. **Intelligent Agent** 🤖
   - Analyze Desktop - تحلیل محیط
   - Execute Task - اجرای تسک

6. **Activity Log** 📋
   - نمایش تمام فعالیت‌ها
   - پاک کردن لاگ

### اجرا:
```bash
python demo_gui.py
```

---

## 📊 آمار و گزارش

### مشاهده آمار Smart Wait
```python
from core.smart_wait import SmartWaiter

waiter = SmartWaiter()

# انجام چند عملیات...
waiter.wait_for_idle()
waiter.wait_for_window("Chrome")

# دریافت آمار
stats = waiter.get_statistics()
print(f"Total operations: {stats['total_operations']}")
print(f"Success rate: {stats['success_rate']:.1%}")
print(f"Average duration: {stats['avg_duration']:.2f}s")
```

### مشاهده تاریخچه
```python
history = waiter.get_history(limit=10)
for entry in history:
    print(f"{entry['strategy']}: {entry['success']} - {entry['duration']:.2f}s")
```

---

## ⚙️ تنظیمات و بهینه‌سازی

### تنظیم سطح لاگ
```bash
python main.py --debug --enable-automation
```

### تنظیم همزمانی تسک‌ها
```bash
python main.py --concurrency 5 --enable-automation
```

### انتخاب ارائه‌دهنده TTS
```bash
python main.py --tts-provider gtts --input-mode voice --enable-automation
```

گزینه‌های TTS:
- `gtts` - Google TTS (رایگان)
- `google-cloud` - Google Cloud TTS (پولی، کیفیت بالا)
- `elevenlabs` - ElevenLabs (پولی، کیفیت بسیار بالا)

---

## 🔒 نکات امنیتی

### خطرات احتمالی:
1. **کنترل موس و کیبورد** - می‌تواند بر روی تمام برنامه‌ها تأثیر بگذارد
2. **دسترسی صفحه** - اسکرین‌شات از تمام محتویات
3. **اجرای دستورات** - امکان اجرای برنامه‌ها

### توصیه‌های امنیتی:
- همیشه قبل از اجرا دستورات را بررسی کنید
- در حالت `--debug` برای تست استفاده کنید
- از قابلیت‌های خودکارسازی فقط در محیط امن استفاده کنید
- لاگ‌ها را برای بررسی فعالیت‌ها مانیتور کنید

---

## 🐛 عیب‌یابی

### مشکل: خودکارسازی فعال نمی‌شود
**حل:**
```bash
# نصب وابستگی‌ها
pip install pyautogui pynput pyperclip psutil pillow
```

### مشکل: موس کار نمی‌کند
**حل:**
- بررسی کنید `--enable-automation` فعال باشد
- مجوزهای Accessibility در سیستم‌عامل را چک کنید

### مشکل: OCR متن را نمی‌خواند
**حل:**
```bash
# نصب Tesseract OCR
# Windows: choco install tesseract
# Mac: brew install tesseract
# Linux: apt-get install tesseract-ocr
```

### مشکل: Demo GUI باز نمی‌شود
**حل:**
```bash
# نصب tkinter
# Windows: به صورت پیش‌فرض نصب است
# Linux: apt-get install python3-tk
```

---

## 📚 مستندات کامل

برای جزئیات بیشتر:
- [`docs/MOUSE_CONTROL.md`](docs/MOUSE_CONTROL.md) - کنترل موس
- [`docs/KEYBOARD_CONTROL.md`](docs/KEYBOARD_CONTROL.md) - کنترل کیبورد
- [`docs/SMART_WAIT.md`](docs/SMART_WAIT.md) - انتظار هوشمند (در حال تکمیل)
- [`WEEK2_TODO.md`](WEEK2_TODO.md) - برنامه توسعه هفته 2

---

## 🎓 مثال‌های پیشرفته

### اتوماسیون کامل یک فرم
```python
from core.mouse_control import MouseController
from core.keyboard_control import KeyboardController
from core.smart_wait import SmartWaiter

# مقداردهی
mouse = MouseController()
keyboard = KeyboardController()
waiter = SmartWaiter()

# باز کردن فرم
mouse.click(100, 200)
waiter.wait_for_window("Registration Form")

# پر کردن فیلد نام
mouse.click(300, 150)
keyboard.type_text("John Doe")

# رفتن به فیلد بعدی
keyboard.press_key('tab')

# پر کردن ایمیل
keyboard.type_text("john@example.com")

# کلیک روی Submit
mouse.click(400, 500)

# انتظار برای تأیید
waiter.wait_for_element("Success", timeout=10)
```

---

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: November 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION