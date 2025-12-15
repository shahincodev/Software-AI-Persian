<div dir="rtl">

# 🤖 Software-AI - سیستم هوشمند کنترل ویندوز

<div align="center">

![Python Version](https://img.shields.io/badge/Python-3.13%2B-blue)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Tests](https://img.shields.io/badge/Tests-249%20Passing-success)
![License](https://img.shields.io/badge/License-Proprietary-red)

**سیستم کنترل خودکار ویندوز با هوش مصنوعی - بدون کدنویسی، فقط با گفتن!**

[نصب سریع](#-نصب-و-راه‌اندازی) • [مستندات](#-مستندات-کامل) • [نمونه‌ها](#-نمونه-کدها) • [ویژگی‌ها](#-قابلیت‌های-پیشرفته)

</div>

---

## 📖 معرفی

**Software-AI** یک سیستم انقلابی برای کنترل کامپیوتر با هوش مصنوعی است. این پروژه به شما امکان می‌دهد که با زبان طبیعی (فارسی یا انگلیسی) با کامپیوترتان صحبت کنید و تمام کارها را به صورت خودکار انجام دهید.

### 💡 چرا این پروژه متفاوت است؟

برخلاف سیستم‌های سنتی که نیاز به دستورات خاص دارند، **Software-AI**:
- ✨ **۱۰۰٪ هوشمند**: تمام تصمیمات توسط AI گرفته می‌شود
- 🧠 **Master AI Controller**: مسیریابی هوشمند و پاسخ‌های انسانی
- 🌍 **چندزبانه واقعی**: پشتیبانی کامل از فارسی و انگلیسی
- 🎯 **بدون محدودیت**: هر برنامه‌ای را می‌شناسد (نه فقط لیست محدود!)
- 👁️ **بینایی رایانه**: صفحه را می‌بیند و تصمیم می‌گیرد
- 🔒 **امن**: سیستم امنیتی چندلایه برای محافظت از سیستم

### 💬 حالت پیش‌فرض: Copilot Chat
- اجرا کنید: `python main.py` → حالت چت آزاد چندزبانه
- درخواست‌های طبیعی بپرسید؛ سیستم در صورت نیاز به‌طور هوشمند ماژول‌های وب/اتوماسیون/عامل خودکار را فعال می‌کند
- حالت پروژه/تسک: فلگ `--task-mode` یا دستور چت «task mode on»؛ برای خروج «task mode off».

---

## 🎯 کاربردها

این سیستم برای چه کارهایی مناسب است؟

### 🎮 بازی‌ها و سرگرمی
```
"باز کن استیم"                    # اجرای Steam
"اجرا کن Counter-Strike"         # شروع بازی
"برو تو بازی و راه برو"          # کنترل خودکار بازی
```

### 💼 کارهای اداری
```
"باز کن Excel و یه جدول بساز"    # اتوماسیون آفیس
"از پوشه Documents بکاپ بگیر"    # مدیریت فایل
"همه عکس‌ها رو به PNG تبدیل کن" # پردازش دسته‌ای
```

### 👨‍💻 برنامه‌نویسی
```
"نصب کن Visual Studio Code"     # نصب ابزار توسعه
"اجرا کن تست‌ها"                # اجرای دستورات
"باز کن GitHub Desktop"          # مدیریت Git
```

### 🎨 طراحی و ویرایش
```
"باز کن Photoshop"               # نرم‌افزارهای گرافیکی
"ذخیره کن عکس با نام MyPhoto"   # عملیات فایل
"تبدیل کن به فرمت JPG"          # تبدیل فرمت
```

---

## ⚡ شروع سریع (۵ دقیقه)

### پیش‌نیازها

- **سیستم عامل**: Windows 10/11
- **پایتون**: نسخه 3.11 یا بالاتر
- **حافظه**: حداقل 4GB RAM
- **اینترنت**: برای دسترسی به APIهای هوش مصنوعی

### نصب و راه‌اندازی

#### 🪟 ویندوز (PowerShell)

```powershell
# ۱. کلون کردن پروژه
git clone https://github.com/shahincodev/Software-AI-Persian.git
cd Software-AI-Persian

# ۲. ساخت محیط مجازی
python -m venv .venv

# ۳. فعال‌سازی محیط مجازی
.\.venv\Scripts\Activate.ps1

# ۴. نصب وابستگی‌ها
pip install -r requirements.txt

# ۵. تنظیم API Keys
Copy-Item .env.example .env
# فایل .env را باز کنید و کلیدهای API را وارد کنید

# ۶. نصب Tesseract (برای OCR)
# دانلود از: https://github.com/UB-Mannheim/tesseract/wiki
# و افزودن مسیر به PATH یا تنظیم در .env

# ۷. اجرای برنامه
python main.py
```

#### 🐧 لینوکس / macOS

```bash
# ۱. کلون کردن پروژه
git clone https://github.com/shahincodev/Software-AI-Persian.git
cd Software-AI-Persian

# ۲. ساخت محیط مجازی
python3 -m venv .venv

# ۳. فعال‌سازی محیط مجازی
source .venv/bin/activate

# ۴. نصب وابستگی‌ها
pip install -r requirements.txt

# ۵. تنظیم API Keys
cp .env.example .env
# فایل .env را ویرایش کنید

# ۶. نصب Tesseract
# Ubuntu/Debian: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract

# ۷. اجرای برنامه
python main.py
```

### استفاده با اسکریپت‌های آماده

برای راحتی کار، می‌توانید از اسکریپت‌های آماده استفاده کنید:

**ویندوز:**
```cmd
run.bat
```

**لینوکس/macOS:**
```bash
chmod +x run.sh
./run.sh
```

این اسکریپت‌ها تمام مراحل بالا را به صورت خودکار انجام می‌دهند.

---

## 🚀 نحوه استفاده

### حالت متنی (پیش‌فرض)

```bash
python main.py --input-mode text

# تعامل:
> باز کن نوت‌پد
✅ نوت‌پد با موفقیت باز شد

> نصب کن Git
🤖 در حال نصب Git...
✅ Git نصب شد

> چقدر RAM دارم؟
💾 حافظه سیستم: 16GB (در دسترس: 8GB)
```

### حالت صوتی (Voice)

```bash
python main.py --input-mode voice

🎤 در حال گوش دادن...
شما: "باز کن اسپاتیفای"
✅ Spotify در حال اجرا...
```

### حالت خودکار دسکتاپ (Desktop Automation)

```bash
python main.py --enable-automation

# دستورات موس
> mouse position
🖱️ موقعیت موس: (640, 480)

> mouse click
🖱️ کلیک در (640, 480)

# دستورات کیبورد
> type سلام دنیا
⌨️ در حال تایپ: سلام دنیا

# انتظار هوشمند
> wait idle
⏳ منتظر آزاد شدن سیستم...
✅ سیستم آزاد شد (۵.۲ ثانیه)
```

### 🤖 حالت عامل خودمختار (Autonomous Agent)

قدرتمندترین قابلیت - کنترل هدف‌محور با بینایی!

```bash
python main.py --enable-autonomous

# تعامل ساده
> goal برو This PC، باز کن E:، فولدر MyDocs بساز

🎯 هدف دریافت شد: برو This PC، باز کن E:، فولدر MyDocs بساز
📋 برنامه ایجاد شد: ۷ مرحله
🔧 اجرای مرحله ۱: گرفتن اسکرین‌شات
🔧 اجرای مرحله ۲: کلیک روی This PC
✅ کلیک شد در (۳۲۰, ۱۸۰)
🔧 اجرای مرحله ۳: انتظار برای باز شدن
...
✅ هدف با موفقیت انجام شد!
```

**مقایسه با روش سنتی:**

| روش سنتی (Action-Based) | عامل خودمختار (Goal-Based) |
|---|---|
| ❌ `LaunchApp notepad.exe` | ✅ `goal باز کن نوت‌پد` |
| ❌ `Wait 2 seconds` | ✅ خودکار |
| ❌ `Click at (500, 300)` | ✅ AI خودش می‌فهمد |
| ❌ ۱۰ خط کد | ✅ ۱ خط پرامپت |

📖 [راهنمای عامل خودمختار](docs/AUTONOMOUS_AGENT.md)

### 🧠 سیستم تحلیل نیت (Intent Planning System)

**🆕 NEW - در حال توسعه فعلی**

سیستم هوشمند برای درک درخواست‌های پیچیده و تبدیل آن‌ها به پلان‌های قابل اجرا:

```bash
python main.py --with-intent-planning

# مثال 1: درخواست ساده
> بازی کن تا برگردم

🧠 تحلیل Intent...
💬 Dialog Manager سوال می‌پرسد: کدام بازی رو باز کنم؟
💡 پیشنهادات: Counter-Strike, Dota 2, Minecraft
📝 جواب کاربر: Counter-Strike
✓ تایید: پاسخ‌ها درست هستند؟ → بله

📋 پلن ایجاد شد:
   1. باز کردن Steam
   2. پیدا کردن Counter-Strike
   3. شروع بازی
   4. بازی تا زمان بازگشت

# مثال 2: درخواست پیچیده
> دیتای هوای تهران رو دریافت کن و در Excel ذخیره کن

🧠 تحلیل Intent...
💬 Dialog Manager: مرورگر چه باشه؟ محل ذخیره چه باشه؟
📋 پلن ایجاد شد:
   1. باز کردن مرورگر (Chrome)
   2. جستجوی دیتای هوای تهران
   3. استخراج داده‌ها
   4. باز کردن Excel
   5. درج داده‌ها
   6. ذخیره فایل (E:\Data\Weather.xlsx)

✅ پلان تایید شد و آماده اجراست!
```

**اجزای سیستم Intent Planning:**

1. **[Intent Analyzer](docs/INTENT_ANALYZER.md)** ✅ - تشخیص هدف و درک نیت کاربر
   - ✅ ۴۱ تست واحد، 611 خط کد
   
2. **[Dialog Manager](docs/DIALOG_MANAGER.md)** ✅ - مکالمه برای جمع‌آوری اطلاعات ناگزیر
   - ✅ ۴۲ تست واحد، 487 خط کد، 100% دوزبانه
   
3. **[Plan Generator](docs/PLAN_GENERATOR.md)** ✅ **NEW** - تولید پلان مرحله‌به‌مرحله
   - ✅ ۳۲ تست واحد، 887 خط کد، 100% دوزبانه، مستندات جامع
   
4. **[Plan Validator](docs/PLAN_VALIDATOR.md)** ✅ **NEW** - بررسی صحت و امنیت پلان
   - ✅ ۲۵ تست واحد، 742 خط کد، 100% دوزبانه، مستندات جامع
   
5. **Memory Integrator** (به زودی) - یادگیری و بهبود مستمر

**مزایا:**
- 🎯 درک درخواست‌های پیچیده و چند‌مرحله‌ای
- 💬 مکالمه خودکار برای جزئیات ناگزیر
- 📋 پلان‌های قابل اجرا و تحقق‌پذیر
- 🔄 بازیابی و بهبود مستمر
- 📚 یادگیری از تجربیات قبلی

📖 [نقشه راه Intent Planning System](docs/INTENT_SYSTEM_PLAN.md) - **خواندن اجباری برای مساهمین!**

---

## 🎨 قابلیت‌های پیشرفته

### 👁️ بینایی رایانه (Desktop Vision)

سیستم بینایی هوشمند که صفحه را می‌بیند و تحلیل می‌کند:

```python
from core.desktop_vision import DesktopVision

vision = DesktopVision()

# گرفتن اسکرین‌شات
screenshot = vision.capture_screen()

# خواندن متن از صفحه (OCR)
texts = vision.read_screen_ocr()
print(f"متن‌های پیدا شده: {[t.text for t in texts]}")

# پیدا کردن دکمه با متن
position = vision.find_text("OK")
if position:
    print(f"دکمه OK در موقعیت {position} پیدا شد")

# لیست پنجره‌ها
windows = vision.list_windows()
for window in windows:
    print(f"پنجره: {window['title']}")
```

**قابلیت‌ها:**
- 📸 اسکرین‌شات (تمام صفحه یا ناحیه خاص)
- 📝 OCR (خواندن متن با Tesseract)
- 🪟 مدیریت پنجره‌ها
- 🔍 تشخیص عناصر
- 🔄 تشخیص تغییرات
- ⏱️ انتظار هوشمند

📖 [راهنمای کامل بینایی رایانه](docs/DESKTOP_VISION.md)

### 🖱️ کنترل موس (Mouse Control)

کنترل کامل و دقیق موس:

```python
from core.mouse_control import MouseController

mouse = MouseController()

# حرکت موس
mouse.move(500, 300, duration=0.5)  # با انیمیشن نرم

# کلیک
mouse.click(x=500, y=300)            # کلیک چپ
mouse.right_click(x=500, y=300)      # کلیک راست
mouse.double_click(x=500, y=300)     # دوبل کلیک

# Drag & Drop
mouse.drag(start_x=100, start_y=100, end_x=300, end_y=300)

# اسکرول
mouse.scroll(clicks=5, direction='down')

# دریافت موقعیت
x, y = mouse.get_position()
```

✅ **آمار تست**: ۳۳/۳۴ موفق (۹۷٪)

📖 [راهنمای کنترل موس](docs/MOUSE_CONTROL.md)

### ⌨️ کنترل کیبورد (Keyboard Control)

تایپ و کنترل کیبورد:

```python
from core.keyboard_control import KeyboardController

keyboard = KeyboardController()

# تایپ متن (فارسی و انگلیسی)
keyboard.type_text("سلام دنیا")
keyboard.type_text("Hello World")

# فشار دادن کلید
keyboard.press_key('enter')
keyboard.press_key('esc')

# Hotkeys
keyboard.hotkey('ctrl', 'c')        # کپی
keyboard.hotkey('ctrl', 'v')        # پیست
keyboard.hotkey('win', 'r')         # Run dialog

# نگه داشتن کلید
keyboard.hold_key('shift')
keyboard.type_text("hello")
keyboard.release_key('shift')
```

✅ **آمار تست**: ۴۲/۴۲ موفق (۱۰۰٪)

📖 [راهنمای کنترل کیبورد](docs/KEYBOARD_CONTROL.md)

### ⏳ سیستم انتظار هوشمند (Smart Wait)

انتظار هوشمند برای شرایط مختلف:

```python
from core.smart_wait import SmartWaiter

waiter = SmartWaiter()

# انتظار برای ظاهر شدن متن
result = waiter.wait_for_text("OK", timeout=10)

# انتظار برای تغییر صفحه
result = waiter.wait_for_screen_change(timeout=5)

# انتظار برای پنجره
result = waiter.wait_for_window("Notepad", timeout=10)

# انتظار برای آزاد شدن CPU
result = waiter.wait_for_idle(cpu_threshold=10.0, timeout=30)

# Retry با Backoff
result = waiter.retry_with_backoff(
    func=my_function,
    max_attempts=5,
    strategy='exponential'  # linear, exponential, fibonacci
)
```

✅ **آمار تست**: ۳۸/۳۸ موفق (۱۰۰٪)

📖 [راهنمای انتظار هوشمند](docs/SMART_WAIT.md)

### 🎮 کنترلر اکشن (Action Controller)

اقدامات سطح بالا و کارهای پیچیده:

```python
from core.action_controller import ActionController

controller = ActionController(vision, mouse, keyboard)

# کلیک روی متن
success = await controller.click_on_text("OK")

# تایپ در فیلد
success = await controller.type_in_field("username", "myuser")

# پر کردن فرم
form_data = {
    "name": "علی احمدی",
    "email": "ali@example.com",
    "age": "25"
}
success = await controller.fill_form(form_data)

# Drag & Drop
success = await controller.drag_and_drop(
    source_text="File.txt",
    target_text="Folder"
)

# ذخیره وضعیت
checkpoint_id = await controller.save_state("before_action")

# بازگرداندن وضعیت
success = await controller.restore_state(checkpoint_id)
```

✅ **آمار تست**: ۴۱/۴۱ موفق (۱۰۰٪)

📖 [راهنمای کنترلر اکشن](docs/ACTION_CONTROLLER.md)

---

## 🛡️ سیستم‌های امنیتی و بازیابی

### 🔒 سیستم ایمنی اقدامات (Action Safety)


محافظت از سیستم در برابر اقدامات خطرناک:

```python
from core.action_safety import ActionSafetyFilter

safety = ActionSafetyFilter()

# بررسی امنیت اقدام
safe, reason = safety.is_action_safe(
    action_type="delete_file",
    target="C:\\Windows\\System32\\important.dll"
)

if not safe:
    print(f"❌ اقدام ناامن: {reason}")
```

**حفاظت‌ها:**
- 🚫 جلوگیری از حذف فایل‌های سیستمی
- 🚫 محافظت از پوشه‌های حیاتی (Windows, System32)
- 🚫 جلوگیری از بستن فرآیندهای مهم (explorer.exe)
- 🚫 فیلتر دستورات مخرب
- ✅ تأیید کاربر برای اقدامات حساس

📖 [راهنمای سیستم ایمنی](docs/ACTION_SAFETY.md)

### 🔄 سیستم بازیابی (Action Recovery)

بازیابی خودکار در صورت خطا:

```python
from core.action_recovery import ActionRecovery

recovery = ActionRecovery()

# اجرای اقدام با بازیابی خودکار
result = await recovery.execute_with_recovery(
    action=my_action,
    rollback_func=undo_action,
    max_retries=3
)

if result.success:
    print("✅ اقدام موفق")
else:
    print(f"❌ خطا: {result.error}")
    print(f"🔄 تلاش‌های انجام شده: {result.retry_count}")
```

**قابلیت‌ها:**
- 🔄 Retry هوشمند با Exponential Backoff
- ↩️ Rollback خودکار
- 📊 تشخیص شدت خطا (LOW, MEDIUM, HIGH, CRITICAL)
- 📈 آمار و تاریخچه اجراها

📖 [راهنمای سیستم بازیابی](docs/ACTION_RECOVERY.md)

### ⚡ حلقه زمان‌واقعی هوشمند (Realtime Loop with Intelligent Interpretation)

سیستم سبک برای مشاهده و تفسیر پیوسته صفحه با OCR و تشخیص تغییرات:

```python
from core.realtime_interpreter import RealtimeInterpreter

interpreter = RealtimeInterpreter(
    vision=vision,
    ocr_enabled=True,        # فعال‌سازی OCR
    text_threshold=3,        # حداقل طول متن
    max_texts=10            # حداکثر متن‌های ثبت شده
)

# تفسیر وضعیت صفحه
result = await interpreter.interpret(
    safety_mode="power",
    risk_threshold=70.0
)

print(f"اقدام: {result.action}")           # "noop" | "hint" | "act"
print(f"ریسک: {result.risk_score:.0f}")    # 0-100
print(f"اعتماد: {result.confidence:.1f}") # 0-1
print(f"تغییر: {result.changed}")          # True/False
```

**ویژگی‌های تفسیرکننده:**
- 👁️ **OCR هوشمند**: خواندن متن‌های مهم صفحه (فقط متن‌های درشت)
- 🪟 **تشخیص پنجره**: شناسایی پنجره‌های فعال و تغییرات آن
- 🔍 **تشخیص تغییرات**: مقایسه پیوسته دو snapshot متوالی
- 📊 **نمره ریسک**: ارزیابی ریسک بر اساس نوع تغییر و حالت ایمنی
- 🔒 **حالت Safety/Power**: رفتار مختلف در حالت‌های ایمنی مختلف

**پارامترها:**
- `ocr_enabled`: فعال‌سازی استخراج متن (پیش‌فرض: True)
- `text_threshold`: حداقل طول متن برای ثبت (پیش‌فرض: 3)
- `max_texts`: حداکثر متن‌های ثبت شده (پیش‌فرض: 10)
- `safety_mode`: "safe" یا "power"
- `risk_threshold`: آستانه ریسک برای اقدام (پیش‌فرض: 70.0)

**مثال: استفاده در حلقه زمان‌واقعی**

```bash
# راه‌اندازی حلقه با تفسیر هوشمند
python main.py --full --realtime --realtime-fps 1.0

# استفاده در حالت Power با ریسک بالاتر
python main.py --safety-mode power --realtime --risk-threshold 80
```

✅ **آمار تست**: ۱۱/۱۱ موفق (۱۰۰٪)

📖 [راهنمای تفسیرکننده زمان‌واقعی](docs/REALTIME_INTERPRETER.md)

---

## 🖥️ قابلیت‌های سطح سیستم

### 🔧 مدیریت چند مانیتور (Multi-Monitor)

پشتیبانی کامل از چند صفحه‌نمایش:

```python
from core.multi_monitor import MultiMonitorManager

monitor_manager = MultiMonitorManager()

# لیست مانیتورها
monitors = monitor_manager.get_monitors()
for i, mon in enumerate(monitors):
    print(f"مانیتور {i}: {mon.width}x{mon.height} در ({mon.x}, {mon.y})")

# کلیک در مانیتور خاص
monitor_manager.click_on_monitor(monitor_index=1, x=500, y=300)

# تبدیل مختصات بین مانیتورها
global_x, global_y = monitor_manager.convert_to_global(
    monitor_index=0,
    local_x=100,
    local_y=100
)
```

📖 [راهنمای چند مانیتور](docs/MULTI_MONITOR.md)

### 🧠 اقدامات هوشمند بر اساس Context

تصمیم‌گیری هوشمند بر اساس وضعیت سیستم:

```python
from core.context_aware_actions import ContextAwareActionExecutor

executor = ContextAwareActionExecutor(vision, mouse, keyboard)

# تشخیص وضعیت سیستم
context = executor.get_current_context()
print(f"وضعیت: {context.state}")  # IDLE, BUSY, GAMING, WORKING

# اجرای اقدام با توجه به Context
result = await executor.execute_action_with_context(
    action=my_action,
    priority="high"
)
```

**حالت‌های تشخیص داده شده:**
- 🟢 IDLE: سیستم آزاد
- 🟡 BUSY: مشغول کار
- 🎮 GAMING: در حال بازی
- 💼 WORKING: در حال کار (برنامه‌نویسی، طراحی)

📖 [راهنمای Context-Aware](docs/CONTEXT_AWARE.md)

---

## 🤖 هوش مصنوعی و پردازش

### 🧠 Master AI Controller - مغز اصلی سیستم

**جدید!** کنترلر اصلی هوش مصنوعی که تمام درخواست‌ها را هوشمندانه مدیریت می‌کند:

```python
from core.master_controller import MasterAIController

# مقداردهی اولیه
master = MasterAIController(
    system_agent=system_agent,
    autonomous_agent=autonomous_agent
)

# پردازش درخواست
result = await master.process_request(
    user_request="CPU چقدره؟",
    context={"lang": "fa"}
)

print(result.human_response)
# "پردازنده شما ۴۵٪ مشغول است، وضعیت خوبی دارید!"
```

**قابلیت‌های Master Controller:**

1. **🎯 Intelligent Routing** - تشخیص خودکار نوع درخواست:
   ```
   "باز کن نوت‌پد" → Desktop Actions
   "CPU چقدره؟" → System Info
   "هوا چطوره؟" → Browser Automation
   "هوش مصنوعی چیست؟" → AI Chat
   ```

2. **💬 Response Humanizer** - تبدیل پاسخ‌های فنی به زبان انسانی:
   ```python
   # خام:
   {"cpu": 45.2, "ram_free": 8192}
   
   # انسانی:
   "پردازنده شما ۴۵٪ مشغول است و ۸ گیگابایت رم آزاد دارید. 
   وضعیت سیستم خوب است!"
   ```

3. **🔄 Smart Fallback** - اگر AI در دسترس نباشد، از الگوریتم‌های ساده استفاده می‌کند

4. **📊 Multi-Tool Integration** - یکپارچه‌سازی کامل با تمام ابزارها:
   - Desktop Actions (Mouse, Keyboard, Vision)
   - System Tools (CPU, RAM, Disk)
   - Browser Automation (به زودی)
   - Autonomous Agent
   - AI Chat

**مثال استفاده:**

```python
# درخواست اطلاعات سیستم
result = await master.process_request("چقدر RAM دارم؟")
# پاسخ: "شما ۶۴ گیگابایت حافظه دارید که ۳۰ گیگابایت آن آزاد است."

# درخواست اجرای برنامه
result = await master.process_request("باز کن Calculator")
# پاسخ: "ماشین‌حساب با موفقیت باز شد!"

# سوال عمومی
result = await master.process_request("هوش مصنوعی چیست؟")
# پاسخ: "هوش مصنوعی شاخه‌ای از علوم کامپیوتر است که..."
```

📖 **[مستندات کامل Master Controller](docs/MASTER_CONTROLLER.md)** *(به زودی)*

---

### 🧠 مغز هوش مصنوعی (AI Brain)

سیستم چندلایه برای پردازش هوشمند:

```python
from core.ai_brain import AIBrain

brain = AIBrain()

# درخواست ساده
response = await brain.ask("چطوری فایل PDF بسازم؟")

# با Fallback خودکار (Gemini → OpenAI → Groq)
response = await brain.ask_with_fallback(
    prompt="تحلیل کن این کد را",
    mode="smart",
    max_tokens=1000
)
```

**مدل‌های پشتیبانی شده:**
- 🌟 Google Gemini 2.0 Flash (اولویت اول)
- 🤖 OpenAI GPT-4
- ⚡ Groq (سریع و کارآمد)
- 🧮 Reasoning Mode (استدلال پیچیده)

**Fallback Chain:**
```
Gemini Flash → OpenAI GPT-4 → Groq → Local Reasoning
```

### 💾 سیستم حافظه (Memory System)

ذخیره و بازیابی هوشمند اطلاعات:

```python
from core.memory_system import MemoryManager

memory = MemoryManager()

# ذخیره در حافظه کوتاه‌مدت
memory.remember_short(
    content="کاربر درخواست کرد فایل backup.zip ساخته شود",
    ttl=3600,  # یک ساعه
    metadata={"type": "user_task"}
)

# ذخیره در حافظه بلندمدت
memory.remember_long(
    content="کاربر ترجیح می‌دهد فایل‌های بکاپ در E:\\Backups ذخیره شوند",
    category="user_preferences"
)

# جستجو در حافظه
results = memory.search_long(query="بکاپ")
```

**ویژگی‌ها:**
- ⚡ حافظه کوتاه‌مدت با TTL
- 💾 حافظه بلندمدت با SQLite
- 🔍 جستجوی هوشمند
- 🏷️ دسته‌بندی و Metadata
- 🧹 پاکسازی خودکار

---

## 📊 آمار و عملکرد

### ✅ نتایج تست‌ها

| ماژول | تعداد تست | موفق | درصد موفقیت |
|---|---|---|---|
| **Mouse Control** | 34 | 33 | 97% |
| **Keyboard Control** | 42 | 42 | 100% |
| **Smart Wait** | 38 | 38 | 100% |
| **Desktop Vision** | 27 | 27 | 100% |
| **Action Controller** | 41 | 41 | 100% |
| **Autonomous Agent** | 15 | 15 | 100% |
| **Safety & Recovery** | 24 | 24 | 100% |
| **مجموع** | **221** | **220** | **99.5%** |

### 📈 خطوط کد نوشته شده

| هفته | ماژول | خطوط کد | تست |
|---|---|---|---|
| هفته ۱ | پایه و اساس | ~2,000 | 35 |
| هفته ۲ (روز ۱-۴) | Mouse, Keyboard, Vision | ~3,500 | 140 |
| هفته ۲ (روز ۵-۹) | Safety, Recovery, Context | ~3,500 | 46 |
| هفته ۳ (روز ۱) | Master AI Controller | ~500 | - |
| **مجموع** | **۱۳ ماژول اصلی** | **~9,500** | **221** |

---

## 📚 مستندات کامل

### 🎯 راهنماهای اصلی

1. **[شروع سریع](docs/QUICKSTART.md)** - نصب و اجرای اولیه (۱۰ دقیقه)
2. **[راهنمای خودکارسازی](docs/AUTOMATION_GUIDE.md)** - نحوه استفاده از قابلیت‌های اتوماسیون
3. **[راهنمای کنترل ویندوز](docs/WINDOWS_AUTOMATION.md)** - معماری و API
4. **[نقشه راه توسعه Intent System](docs/INTENT_SYSTEM_PLAN.md)** - 🆕 **خواندن اجباری برای توسعه‌دهندگان!**

### 🧠 Intent Planning System - ماژول‌ها (NEW!)

5. **[Intent Analyzer](docs/INTENT_ANALYZER.md)** - تشخیص نیت و هدف کاربر
   - ✅ ۴۱ تست واحد
   - ✅ 611 خط کد
   - ✅ پشتیبانی دوزبانه
   - ✅ مستندات کامل

6. **[Dialog Manager](docs/DIALOG_MANAGER.md)** - مکالمه برای جمع‌آوری اطلاعات ناگزیر
   - ✅ ۴۲ تست واحد
   - ✅ 487 خط کد
   - ✅ پشتیبانی 100% دوزبانه
   - ✅ مستندات جامع

7. **[Plan Generator](docs/PLAN_GENERATOR.md)** - تولید پلان مرحله‌به‌مرحله
   - ✅ ۳۲ تست واحد
   - ✅ 887 خط کد
   - ✅ پشتیبانی 100% دوزبانه
   - ✅ مستندات کامل

8. **[Plan Validator](docs/PLAN_VALIDATOR.md)** - اعتبارسنجی و امتیازدهی پلان
   - ✅ ۲۵ تست واحد
   - ✅ 742 خط کد
   - ✅ سیستم امنیتی 8 مرحله‌ای
   - ✅ مستندات جامع

9. **[Memory Integrator](docs/MEMORY_INTEGRATOR.md)** - یادگیری از تاریخچه (تازه تکمیل!)
   - ✅ ۲۸ تست واحد
   - ✅ 505 خط کد
   - ✅ دیتابیس SQLite
   - ✅ مستندات کامل

### 👁️ بینایی و تشخیص

10. **[Desktop Vision](docs/DESKTOP_VISION.md)** - سیستم بینایی رایانه
11. **[OCR و تشخیص متن](docs/DESKTOP_VISION.md#ocr)** - خواندن متن از صفحه

### 🖱️⌨️ کنترل ورودی

12. **[Mouse Control](docs/MOUSE_CONTROL.md)** - کنترل کامل موس
13. **[Keyboard Control](docs/KEYBOARD_CONTROL.md)** - کنترل کیبورد و تایپ
14. **[Smart Wait](docs/SMART_WAIT.md)** - انتظار هوشمند

### 🎮 اقدامات پیشرفته

15. **[Action Controller](docs/ACTION_CONTROLLER.md)** - کنترلر اکشن‌های سطح بالا
16. **[Autonomous Agent](docs/AUTONOMOUS_AGENT.md)** - عامل خودمختار

### 🛡️ امنیت و بازیابی

17. **[Action Safety](docs/ACTION_SAFETY.md)** - سیستم ایمنی
18. **[Action Recovery](docs/ACTION_RECOVERY.md)** - سیستم بازیابی
19. **[Context-Aware Actions](docs/CONTEXT_AWARE.md)** - اقدامات هوشمند

### 🧠 هوش مصنوعی و کنترل

20. **[Master AI Controller](docs/MASTER_CONTROLLER.md)** - مغز اصلی سیستم
21. **[Intent Planning System](docs/INTENT_SYSTEM_PLAN.md)** - درک پیچیده درخواست‌ها

### 🔧 پیشرفته

22. **[Multi-Monitor](docs/MULTI_MONITOR.md)** - پشتیبانی چند مانیتور
23. **[Logging Best Practices](docs/LOGGING_BEST_PRACTICES.md)** - بهترین روش‌های لاگ‌گیری

### 📋 گزارش‌ها و برنامه‌ریزی

24. **[Week 2 Plan](docs/WEEK2_ACTION_LAYER_PLAN.md)** - برنامه هفته دوم
25. **[Week 2 Summary](docs/WEEK2_EXECUTIVE_SUMMARY.md)** - خلاصه مدیریتی
26. **[Integration Guide](docs/INTEGRATION_GUIDE.md)** - راهنمای ادغام

---

## 💻 نمونه کدها

### مثال ۱: کنترل کامل دسکتاپ

```python
import asyncio
from core.desktop_vision import DesktopVision
from core.mouse_control import MouseController
from core.keyboard_control import KeyboardController
from core.smart_wait import SmartWaiter

async def automate_notepad():
    """باز کردن نوت‌پد و نوشتن متن"""
    
    vision = DesktopVision()
    mouse = MouseController()
    keyboard = KeyboardController()
    waiter = SmartWaiter()
    
    # ۱. باز کردن نوت‌پد
    keyboard.hotkey('win', 'r')  # Run dialog
    await waiter.wait(1.0)
    
    keyboard.type_text('notepad')
    keyboard.press_key('enter')
    
    # ۲. انتظار برای باز شدن
    result = waiter.wait_for_window('Notepad', timeout=5)
    if not result.success:
        print("❌ نوت‌پد باز نشد")
        return
    
    # ۳. نوشتن متن
    text = """
    سلام دنیا!
    
    این متن توسط سیستم خودکار نوشته شده است.
    تاریخ: 2025-12-06
    """
    
    keyboard.type_text(text)
    
    # ۴. ذخیره فایل
    keyboard.hotkey('ctrl', 's')
    await waiter.wait(1.0)
    
    keyboard.type_text('test_automation.txt')
    keyboard.press_key('enter')
    
    print("✅ فایل با موفقیت ذخیره شد!")

if __name__ == "__main__":
    asyncio.run(automate_notepad())
```

### مثال ۲: عامل خودمختار

```python
import asyncio
from core.autonomous_agent import AutonomousAgent

async def demo_autonomous():
    """نمایش قابلیت‌های عامل خودمختار"""
    
    agent = AutonomousAgent()
    
    # مثال ۱: مدیریت فایل
    result = await agent.execute_goal("""
        برو به درایو E:
        یک پوشه به نام MyProjects بساز
        داخل آن یک فایل README.txt ایجاد کن
    """)
    
    if result['success']:
        print("✅ مثال ۱ موفق:")
        for step in result['steps']:
            print(f"   {step['number']}. {step['description']}")
    
    # مثال ۲: اجرای برنامه
    result = await agent.execute_goal(
        "باز کن Calculator و حساب کن ۲۵ + ۳۷"
    )
    
    print(f"\n{'✅' if result['success'] else '❌'} مثال ۲: {result['goal']}")

if __name__ == "__main__":
    asyncio.run(demo_autonomous())
```

### مثال ۳: پردازش دسته‌ای فایل‌ها

```python
import asyncio
from pathlib import Path
from core.action_controller import ActionController
from core.desktop_vision import DesktopVision
from core.mouse_control import MouseController
from core.keyboard_control import KeyboardController

async def batch_rename_files():
    """تغییر نام دسته‌ای فایل‌ها"""
    
    vision = DesktopVision()
    mouse = MouseController()
    keyboard = KeyboardController()
    controller = ActionController(vision, mouse, keyboard)
    
    # پوشه مقصد
    folder = Path("E:/Photos")
    files = list(folder.glob("*.jpg"))
    
    print(f"📁 تعداد فایل: {len(files)}")
    
    for i, file in enumerate(files, start=1):
        new_name = f"Photo_{i:03d}.jpg"
        
        # پیدا کردن فایل در File Explorer
        success = await controller.click_on_text(file.name)
        if not success:
            print(f"❌ فایل {file.name} پیدا نشد")
            continue
        
        # تغییر نام
        keyboard.press_key('f2')  # Rename
        await asyncio.sleep(0.5)
        
        keyboard.hotkey('ctrl', 'a')  # Select all
        keyboard.type_text(new_name)
        keyboard.press_key('enter')
        
        print(f"✅ {i}/{len(files)}: {file.name} → {new_name}")
    
    print("✨ تغییر نام کامل شد!")

if __name__ == "__main__":
    asyncio.run(batch_rename_files())
```

### مثال ۴: مانیتورینگ سیستم

```python
import asyncio
from core.intelligent_agent import IntelligentSystemAgent

async def system_monitoring():
    """نمایش اطلاعات سیستم"""
    
    agent = IntelligentSystemAgent()
    
    # اطلاعات سخت‌افزار
    result = await agent.process_request("نمایش مشخصات سخت‌افزار")
    print(result)
    
    # فرآیندهای در حال اجرا
    result = await agent.process_request("لیست برنامه‌های باز")
    print(result)
    
    # وضعیت دیسک
    result = await agent.process_request("چقدر فضای خالی دارم؟")
    print(result)

if __name__ == "__main__":
    asyncio.run(system_monitoring())
```

---

## 🔧 تنظیمات پیشرفته

### فایل `.env`

تنظیمات محیطی پروژه:

```bash
# API Keys
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Tesseract OCR
TESSERACT_PATH=C:\\Program Files\\Tesseract-OCR\\tesseract.exe

# Logging
LOG_LEVEL=INFO
LOG_FILE=data/logs/app.log

# Performance
MAX_CONCURRENT_TASKS=3
DEFAULT_TIMEOUT=30

# Safety
ENABLE_SAFETY_FILTER=true
REQUIRE_USER_CONFIRMATION=true
```

### آرگومان‌های خط فرمان

```bash
python main.py [OPTIONS]

گزینه‌ها:
  --mode {browser,code}         حالت اجرا (پیش‌فرض: browser)
  --input-mode {text,voice}     نوع ورودی (پیش‌فرض: text)
  --concurrency INT             تعداد تسک‌های همزمان (پیش‌فرض: 3)
  --enable-automation           فعال‌سازی خودکارسازی دسکتاپ
  --enable-autonomous           فعال‌سازی عامل خودمختار
  --safety-mode {safe,power}    حالت ایمنی (پیش‌فرض: safe)
  --risk-threshold FLOAT        آستانه ریسک (پیش‌فرض: 70.0)
  --realtime                    فعال‌سازی حلقه زمان‌واقعی با OCR هوشمند
  --realtime-fps FLOAT          نرخ فریم حلقه زمان‌واقعی (پیش‌فرض: 1.0)
  --tts-provider {gtts,google-cloud,elevenlabs}
  --debug                       حالت دیباگ
  --help                        نمایش راهنما
```

**مثال‌ها:**

```bash
# حالت صوتی با خودکارسازی
python main.py --input-mode voice --enable-automation

# حالت عامل خودمختار با دیباگ
python main.py --enable-autonomous --debug

# افزایش تعداد تسک‌های همزمان
python main.py --concurrency 10

# استفاده از حلقه زمان‌واقعی با تفسیر هوشمند
python main.py --full --realtime --realtime-fps 1.0

# حالت Power برای اکشن‌های ریسک‌بیشتر با تفسیر OCR
python main.py --safety-mode power --realtime --risk-threshold 80

# استفاده از TTS پیشرفته
python main.py --input-mode voice --tts-provider elevenlabs
```

---

## 🐛 عیب‌یابی

### مشکلات رایج و راه‌حل‌ها

#### ❌ Tesseract پیدا نمی‌شود

**علت**: مسیر Tesseract تنظیم نشده است.

**راه‌حل:**
```bash
# در فایل .env اضافه کنید:
TESSERACT_PATH=C:\\Program Files\\Tesseract-OCR\\tesseract.exe

# یا در PATH سیستم قرار دهید
```

#### ❌ API Key اشتباه

**علت**: کلید API نامعتبر یا منقضی شده.

**راه‌حل:**
1. فایل `.env` را بررسی کنید
2. کلیدهای جدید از سایت‌های مربوطه دریافت کنید:
   - Gemini: https://makersuite.google.com/app/apikey
   - OpenAI: https://platform.openai.com/api-keys
   - Groq: https://console.groq.com/

#### ❌ Import Error

**علت**: کتابخانه‌ها نصب نشده‌اند.

**راه‌حل:**
```bash
# نصب مجدد وابستگی‌ها
pip install -r requirements.txt --force-reinstall

# یا نصب تک‌تک:
pip install pillow pytesseract pyautogui opencv-python
```

#### ❌ Permission Denied

**علت**: برنامه نیاز به دسترسی Administrator دارد.

**راه‌حل:**
```powershell
# اجرا با دسترسی Administrator
# کلیک راست روی PowerShell → Run as Administrator
python main.py
```

---

## 🤝 مشارکت


این پروژه یک پروژه اختصاصی (Proprietary) است، اما از مشارکت استقبال می‌کنیم!

### چگونه مشارکت کنیم؟

1. **گزارش مشکلات (Issues)**
   - قبل از باز کردن Issue، بررسی کنید که مشکل قبلاً گزارش نشده باشد
   - عنوان واضح و توصیفی انتخاب کنید
   - جزئیات کامل ارائه دهید:
     - مراحل بازتولید مشکل
     - رفتار مورد انتظار
     - رفتار واقعی
     - لاگ‌ها یا اسکرین‌شات‌ها

2. **پیشنهاد ویژگی جدید**
   - Issue جدید با برچسب `enhancement` باز کنید
   - توضیح دهید چرا این ویژگی مفید است
   - مثال‌های کاربردی ارائه دهید

3. **ارسال Pull Request**
   - Fork کردن repository
   - ایجاد branch جدید: `git checkout -b feature/my-feature`
   - Commit با پیام‌های واضح: `git commit -m "Add: توضیح تغییرات"`
   - Push به branch: `git push origin feature/my-feature`
   - باز کردن Pull Request

4. **استانداردهای کد**
   - از PEP 8 برای کد پایتون پیروی کنید
   - کامنت‌های واضح و کافی بنویسید
   - تست‌های مناسب اضافه کنید
   - مستندات را به‌روز کنید

📖 جزئیات بیشتر: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📜 مجوز و حقوق مالکیت

### مالکیت معنوی

این پروژه تحت مجوز اختصاصی (Proprietary License) منتشر شده است.

**© 2025 Shahin - تمامی حقوق محفوظ است**

#### شناسه SPDX
```
SPDX-License-Identifier: NOASSERTION
```

این شناسه نشان می‌دهد که این پروژه تحت هیچ مجوز عمومی شناخته‌شده‌ای منتشر نشده است.

### محدودیت‌های استفاده

بدون اجازه کتبی صریح از مالک، موارد زیر **ممنوع** است:

❌ **کپی برداری و توزیع**
- کپی کردن کد منبع یا باینری
- توزیع در هر شکلی (تجاری یا غیرتجاری)
- انتشار عمومی یا خصوصی

❌ **تغییر و اشتقاق**
- ایجاد نسخه‌های تغییر یافته
- ساخت محصولات مشتق شده
- یکپارچه‌سازی در پروژه‌های دیگر

❌ **استفاده تجاری**
- فروش یا اجاره
- ارائه به عنوان سرویس
- استفاده در محصولات تجاری

### مجوز استفاده

برای دریافت مجوز استفاده از این پروژه:

#### 📧 تماس با مالک

**Shahin**
- 🐙 GitHub: [@shahincodev](https://github.com/shahincodev)
- 📮 Email: shahincodev@gmail.com
- 🌐 Repository: [Software-AI-Persian](https://github.com/shahincodev/Software-AI-Persian)

#### 📝 انواع مجوز قابل ارائه

1. **مجوز تحقیقاتی** - برای مؤسسات آموزشی و تحقیقاتی
2. **مجوز تجاری** - برای استفاده در محصولات تجاری
3. **مجوز سازمانی** - برای شرکت‌ها و سازمان‌ها
4. **مجوز توسعه‌دهنده** - برای توسعه‌دهندگان مستقل

### ضمانت‌ها و مسئولیت‌ها

```
این نرم‌افزار "همان‌طور که هست" (AS IS) ارائه می‌شود،
بدون هیچ‌گونه ضمانت صریح یا ضمنی.

در هیچ شرایطی مالک مسئول خسارات مستقیم، غیرمستقیم،
تصادفی، خاص یا تبعی ناشی از استفاده از این نرم‌افزار نخواهد بود.
```

📖 متن کامل مجوز: [LICENSE](LICENSE)

---

## 🙏 قدردانی و سپاسگزاری

### تکنولوژی‌های استفاده شده

این پروژه از کتابخانه‌ها و ابزارهای متن‌باز زیر استفاده کرده است:

#### 🤖 هوش مصنوعی
- **Google Gemini** - مدل اصلی AI
- **OpenAI GPT-4** - پشتیبان AI
- **Groq** - پردازش سریع

#### 🎨 رابط کاربری و کنترل
- **PyAutoGUI** - کنترل موس و کیبورد
- **Pillow (PIL)** - پردازش تصویر
- **Tesseract OCR** - خواندن متن از تصاویر
- **OpenCV** - بینایی رایانه

#### 🔧 ابزارهای توسعه
- **Python 3.13** - زبان برنامه‌نویسی
- **asyncio** - برنامه‌نویسی ناهمزمان
- **SQLite** - پایگاه داده
- **pytest** - تست واحد
- **colorama** - رنگ‌ها در ترمینال

### 👨‍💻 توسعه‌دهندگان

**توسعه‌دهنده اصلی و مالک پروژه:**
- Shahin ([@shahincodev](https://github.com/shahincodev))

### 🌟 حامیان و همکاران

قدردانی ویژه از:
- جامعه پایتون
- کاربران آزمایشی
- توسعه‌دهندگان کتابخانه‌های متن‌باز

---

## 📞 ارتباط با ما

### کانال‌های ارتباطی

| روش | آدرس | موضوع |
|---|---|---|
| 🐙 **GitHub Issues** | [Issues](https://github.com/shahincodev/Software-AI-Persian/issues) | گزارش باگ، پیشنهادات |
| 📧 **Email** | shahincodev@gmail.com | مجوز، همکاری، سوالات |
| 💬 **Discussions** | [Discussions](https://github.com/shahincodev/Software-AI-Persian/discussions) | گفتگو، سوالات عمومی |

### سوالات متداول (FAQ)

<details>
<summary><strong>آیا این پروژه رایگان است؟</strong></summary>

این پروژه تحت مجوز اختصاصی است. برای استفاده تجاری نیاز به مجوز دارید، اما برای مطالعه و آزمایش شخصی می‌توانید از آن استفاده کنید.
</details>

<details>
<summary><strong>چطور می‌توانم در پروژه مشارکت کنم؟</strong></summary>

می‌توانید Issue باز کنید، Pull Request ارسال کنید یا از طریق ایمیل با ما تماس بگیرید. قبل از مشارکت، لطفاً [CONTRIBUTING.md](CONTRIBUTING.md) را بخوانید.
</details>

<details>
<summary><strong>آیا پشتیبانی از macOS و Linux وجود دارد؟</strong></summary>

در حال حاضر تمرکز اصلی روی Windows است، اما بسیاری از ماژول‌ها در macOS و Linux هم کار می‌کنند. پشتیبانی کامل از این سیستم‌عامل‌ها در برنامه آینده است.
</details>

<details>
<summary><strong>چرا Tesseract نصب نمی‌شود؟</strong></summary>

Tesseract یک برنامه جداگانه است که باید جداگانه نصب شود. از [این لینک](https://github.com/UB-Mannheim/tesseract/wiki) دانلود کنید و مسیر آن را در `.env` تنظیم کنید.
</details>

<details>
<summary><strong>API Keys را از کجا دریافت کنم؟</strong></summary>

- **Gemini**: https://makersuite.google.com/app/apikey
- **OpenAI**: https://platform.openai.com/api-keys  
- **Groq**: https://console.groq.com/

همه این سرویس‌ها نسخه رایگان محدود دارند.
</details>

---

## 🗺️ نقشه راه (Roadmap)
### ✅ نسخه 1.0 (فعلی) - کامل شده

- [x] سیستم پایه AI
- [x] کنترل موس و کیبورد
- [x] بینایی رایانه (OCR)
- [x] انتظار هوشمند
- [x] عامل خودمختار
- [x] سیستم ایمنی و بازیابی
- [x] **Master AI Controller** (جدید! 🎉)
- [x] ۲۲۱ تست واحدو بازیابی
- [x] ۲۲۱ تست واحد
### 🚧 نسخه 1.1 (در دست توسعه)

- [x] **Master AI Controller** - مسیریابی هوشمند ✅
- [ ] یکپارچه‌سازی Browser-Use با Master Controller
- [ ] پشتیبانی کامل macOS
- [ ] پشتیبانی کامل Linux
- [ ] رابط گرافیکی (GUI)
- [ ] Plugin System
- [ ] مستندات به زبان انگلیسی
- [ ] مستندات به زبان انگلیسی

### 🔮 نسخه 2.0 (آینده)

- [ ] Cloud Integration
- [ ] Mobile App (Android/iOS)
- [ ] Web Dashboard
- [ ] Marketplace برای Plugins
- [ ] Multi-language Support (آلمانی، عربی، ...)

### 💡 ایده‌های آینده

- 🎮 کنترل کامل بازی‌ها
- 🖼️ پردازش تصویر پیشرفته
- 🎬 ضبط و پخش Macro
- 🧠 یادگیری ماشین برای بهبود دقت
- 📱 همگام‌سازی بین دستگاه‌ها

---

## 📊 آمار پروژه

### خطوط کد (تخمینی)

```
───────────────────────────────────────────────
زبان            فایل    خطوط      درصد
───────────────────────────────────────────────
Python            45    9,000      85%
Markdown          20    2,500      15%
───────────────────────────────────────────────
مجموع            65   11,500     100%
───────────────────────────────────────────────
```
```
Software-AI-Persian/
├── 📁 core/              # ماژول‌های اصلی (۱۳ ماژول)
│   ├── ai_brain.py
│   ├── master_controller.py  # 🆕 مغز اصلی سیستم
│   ├── autonomous_agent.py
│   ├── desktop_vision.py
│   ├── mouse_control.py
│   ├── keyboard_control.py
│   └── ...
├── 📁 docs/              # مستندات (۱۹ فایل)
│   ├── keyboard_control.py
│   └── ...
├── 📁 docs/              # مستندات (۳۷ فایل)
├── 📁 tests/             # تست‌ها (۲۲۱ تست)
├── 📁 examples/          # نمونه کدها
├── 📁 data/              # داده‌ها و لاگ‌ها
├── main.py              # نقطه ورود اصلی
├── README.md            # این فایل
└── requirements.txt     # وابستگی‌ها
| نسخه | تاریخ | تغییرات اصلی |
|---|---|---|
| **1.1.0** | دسامبر ۷، ۲۰۲۵ | 🧠 Master AI Controller - مسیریابی هوشمند |
| **1.0.0** | دسامبر ۶، ۲۰۲۵ | انتشار اولیه - تمام قابلیت‌ها |
| **0.9.0** | نوامبر ۲۰۲۵ | Week 2 Complete - Safety & Recovery |
| **0.5.0** | نوامبر ۲۰۲۵ | Desktop Automation - Mouse, Keyboard, Vision |
| **0.1.0** | نوامبر ۲۰۲۵ | Alpha - AI Brain & Base |

---

---

## 🎓 منابع یادگیری

### آموزش‌های رسمی

1. **[راهنمای شروع سریع](docs/QUICKSTART.md)** - ۱۰ دقیقه
2. **[آموزش کنترل دسکتاپ](docs/AUTOMATION_GUIDE.md)** - ۳۰ دقیقه
3. **[آموزش عامل خودمختار](docs/AUTONOMOUS_AGENT.md)** - ۴۵ دقیقه

### ویدیوهای آموزشی (به زودی)

- 🎥 معرفی پروژه (۵ دقیقه)
- 🎥 نصب و راه‌اندازی (۱۰ دقیقه)
- 🎥 اولین اتوماسیون (۱۵ دقیقه)
- 🎥 عامل خودمختار در عمل (۲۰ دقیقه)

### مقالات تخصصی

1. **معماری سیستم** - نحوه طراحی و ساختار
2. **الگوریتم‌های بینایی** - OCR و تشخیص تصویر
3. **سیستم Fallback** - مدیریت خطا در AI
4. **بهینه‌سازی عملکرد** - نکات سرعت و کارایی

---

## 🏆 موفقیت‌ها

- ✅ **۹,۵۰۰+** خط کد
- ✅ **۱۳** ماژول اصلی (+ Master AI Controller)
- ✅ **۳۷** فایل مستندات
- ✅ **۲۲۱** تست واحد (۹۹.۵٪ موفق)
### 🎖️ ویژگی‌های منحصر به فرد

1. **۱۰۰٪ AI-Powered** - تمام تصمیمات توسط AI
2. **🧠 Master AI Controller** - مسیریابی هوشمند و پاسخ‌های انسانی (جدید!)
3. **چندزبانه واقعی** - فارسی و انگلیسی
4. **بینایی هوشمند** - OCR و تحلیل تصویر
5. **عامل خودمختار** - Goal-Based Control
6. **امنیت چندلایه** - Safety + Recovery

---

<div align="center">

## ⭐ حمایت از پروژه

اگر این پروژه برایتان مفید بود، لطفاً:

[![GitHub stars](https://img.shields.io/github/stars/shahincodev/Software-AI-Persian?style=social)](https://github.com/shahincodev/Software-AI-Persian/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/shahincodev/Software-AI-Persian?style=social)](https://github.com/shahincodev/Software-AI-Persian/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/shahincodev/Software-AI-Persian?style=social)](https://github.com/shahincodev/Software-AI-Persian/watchers)

### 💝 حمایت مالی

اگر می‌خواهید از توسعه این پروژه حمایت کنید:
- منتظر انتشار پروژه باشید

📧 برای اطلاعات بیشتر: shahincodev@gmail.com

---

**ساخته شده با ❤️ در**

```
███████╗ ██████╗ ███████╗████████╗██╗    ██╗ █████╗ ██████╗ ███████╗
██╔════╝██╔═══██╗██╔════╝╚══██╔══╝██║    ██║██╔══██╗██╔══██╗██╔════╝
███████╗██║   ██║█████╗     ██║   ██║ █╗ ██║███████║██████╔╝█████╗  
╚════██║██║   ██║██╔══╝     ██║   ██║███╗██║██╔══██║██╔══██╗██╔══╝  
███████║╚██████╔╝██║        ██║   ╚███╔███╔╝██║  ██║██║  ██║███████╗
╚══════╝ ╚═════╝ ╚═╝        ╚═╝    ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
                                                                      
              A I   -   P O W E R E D   W I N D O W S   C O N T R O L
```

**© 2025 Shahin - All Rights Reserved**

[🏠 صفحه اصلی](https://github.com/shahincodev/Software-AI-Persian) • 
[📚 مستندات](docs/) • 
[🐛 گزارش مشکل](https://github.com/shahincodev/Software-AI-Persian/issues) • 
[💬 بحث و گفتگو](https://github.com/shahincodev/Software-AI-Persian/discussions)

</div>

</div>
