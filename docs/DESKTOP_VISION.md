# راهنمای Desktop Vision System

## معرفی

**Desktop Vision** یک سیستم بینایی رایانه است که به Software-AI قدرت "دیدن" صفحه را می‌دهد. این ماژول اولین قدم در ساخت اتوماسیون پیشرفته Desktop است.

## نصب و راه‌اندازی

### گام 1: نصب کتابخانه‌های Python

```powershell
pip install -r requirements.txt
```

این دستور کتابخانه‌های زیر را نصب می‌کند:
- `pillow>=10.0.0` - برای Screenshot و پردازش تصویر
- `pytesseract>=0.3.10` - موتور OCR رایگان
- `opencv-python>=4.8.0` - Computer Vision
- `pygetwindow>=0.0.9` - مدیریت پنجره‌ها
- `numpy>=1.24.0` - پردازش آرایه‌ها

### گام 2: نصب Tesseract OCR

Tesseract یک موتور OCR رایگان و open-source است که برای خواندن متن از تصاویر استفاده می‌شود.

**نصب با WinGet (توصیه می‌شود):**
```powershell
winget install UB-Mannheim.TesseractOCR
```

**نصب دستی:**
1. دانلود از: https://github.com/UB-Mannheim/tesseract/wiki
2. نصب در مسیر پیش‌فرض: `C:\Program Files\Tesseract-OCR`
3. اضافه کردن به PATH (اختیاری)

**بررسی نصب:**
```powershell
tesseract --version
```

باید خروجی مشابه زیر ببینید:
```
tesseract v5.3.0.20221214
```

## استفاده پایه

### مثال 1: گرفتن اسکرین‌شات

```python
from core.desktop_vision import DesktopVision

vision = DesktopVision()

# گرفتن اسکرین‌شات کل صفحه
screenshot = vision.capture_screen()
print(f"سایز: {screenshot.width}x{screenshot.height}")

# ذخیره در فایل
vision.save_screenshot("screenshot.png")
```

### مثال 2: خواندن متن از صفحه (OCR)

```python
from core.desktop_vision import DesktopVision

vision = DesktopVision()

# خواندن تمام متن روی صفحه
text = vision.extract_text()
print(text)

# پیدا کردن متن خاص
position = vision.find_text("OK")
if position:
    x, y = position
    print(f"دکمه OK در موقعیت ({x}, {y}) پیدا شد")
```

### مثال 3: مدیریت پنجره‌ها

```python
from core.desktop_vision import DesktopVision

vision = DesktopVision()

# دریافت پنجره فعال
active = vision.get_active_window()
print(f"پنجره فعال: {active.title}")

# لیست تمام پنجره‌ها
windows = vision.list_windows()
for win in windows:
    print(f"- {win.title}")

# فوکوس روی Notepad
vision.focus_window("Notepad")

# منتظر ماندن تا Calculator باز شود
if vision.wait_for_window("Calculator", timeout=10):
    print("Calculator باز شد!")
```

### مثال 4: تشخیص تغییرات

```python
from core.desktop_vision import DesktopVision

vision = DesktopVision()

# گرفتن تصویر اولیه
baseline = vision.capture_screen()

# انجام کاری که صفحه را تغییر می‌دهد
# ...

# بررسی تغییر
current = vision.capture_screen()
if vision.has_changed(baseline, current):
    print("صفحه تغییر کرد!")

# منتظر ماندن تا متن ظاهر شود
if vision.wait_until_text_appears("Done", timeout=30):
    print("عملیات تمام شد!")

# منتظر ماندن تا "Loading..." ناپدید شود
if vision.wait_until_text_disappears("Loading...", timeout=60):
    print("بارگذاری تمام شد!")
```

## قابلیت‌ها

### 1. Screenshot & Capture
- `capture_screen()` - گرفتن اسکرین‌شات کل صفحه
- `capture_screen(region=(x,y,w,h))` - گرفتن اسکرین‌شات ناحیه خاص
- `save_screenshot(path)` - ذخیره در فایل

### 2. OCR - خواندن متن
- `extract_text()` - استخراج تمام متن
- `get_all_text_boxes()` - دریافت تمام باکس‌های متنی با موقعیت
- `find_text(text)` - پیدا کردن متن خاص
- `find_text_fuzzy(text)` - پیدا کردن با تطابق تقریبی (fuzzy matching)

### 3. Window Management
- `get_active_window()` - دریافت پنجره فعال
- `list_windows()` - لیست تمام پنجره‌ها
- `focus_window(title)` - فوکوس روی پنجره
- `wait_for_window(title)` - منتظر ماندن برای باز شدن پنجره

### 4. Change Detection
- `has_changed(baseline, current)` - بررسی تغییر بین دو تصویر
- `wait_for_change()` - منتظر ماندن تا صفحه تغییر کند
- `wait_until_text_appears(text)` - منتظر ماندن تا متن ظاهر شود
- `wait_until_text_disappears(text)` - منتظر ماندن تا متن ناپدید شود
- `wait_for_stable_screen()` - منتظر ماندن تا صفحه stable شود

### 5. Template Matching (NEW - Week 2) 🆕
قابلیت پیدا کردن تصاویر روی صفحه با استفاده از OpenCV:
- `find_image(template_path, confidence)` - پیدا کردن تصویر template
- `find_all_images(template_path, confidence)` - پیدا کردن تمام نمونه‌ها
- `wait_for_image(template_path, timeout)` - انتظار برای ظاهر شدن تصویر

**مثال:**
```python
# پیدا کردن دکمه Submit
match = vision.find_image("submit_button.png", confidence=0.9)
if match:
    print(f"Button found at {match.center}")
    print(f"Confidence: {match.confidence:.2%}")
```

### 6. Color Detection (NEW - Week 2) 🆕
تشخیص و پیگیری رنگ‌ها روی صفحه:
- `get_pixel_color(x, y)` - دریافت رنگ یک پیکسل
- `find_color(color, tolerance)` - پیدا کردن تمام پیکسل‌های با رنگ خاص
- `wait_for_color(x, y, color, tolerance)` - انتظار برای تغییر رنگ
- `get_dominant_colors(region, num_colors)` - استخراج رنگ‌های غالب

**مثال:**
```python
# بررسی رنگ دکمه
color = vision.get_pixel_color(500, 300)
if color == (0, 255, 0):  # سبز
    print("Button is active!")

# انتظار برای سبز شدن
vision.wait_for_color(500, 300, (0, 255, 0), tolerance=20)
```

### 7. UI Recognition (NEW - Week 2) 🆕
شناسایی خودکار المان‌های رابط کاربری:
- `find_button(button_text)` - پیدا کردن دکمه با متن
- `find_input_field(label_text)` - پیدا کردن فیلد ورودی
- `classify_element(region)` - طبقه‌بندی نوع المان

**مثال:**
```python
# پیدا کردن دکمه OK
ok_button = vision.find_button("OK")
if ok_button:
    mouse.click(*ok_button)

# پیدا کردن فیلد Email
email_field = vision.find_input_field("Email:")
```

### 8. Visual Validation (NEW - Week 2) 🆕
تأیید موفقیت عملیات با بررسی بصری:
- `verify_click_success(region)` - تأیید کلیک با تشخیص تغییر
- `verify_text_typed(text, region)` - تأیید تایپ با OCR
- `verify_element_visible(element, method)` - بررسی visibility
- `compare_screenshots(img1, img2)` - مقایسه دو تصویر

**مثال:**
```python
# کلیک و تأیید
mouse.click(500, 300)
if vision.verify_click_success((450, 250, 100, 100)):
    print("Click successful!")

# تایپ و تأیید
keyboard.type_text("Hello")
if vision.verify_text_typed("Hello", region=(100, 200, 200, 50)):
    print("Text typed correctly!")
```

## مثال‌های پیشرفته (Enhanced Vision) 🆕

### مثال 1: پیدا کردن و کلیک روی تصویر

```python
from core.desktop_vision import DesktopVision
from core.mouse_control import MouseController

vision = DesktopVision()
mouse = MouseController()

# پیدا کردن دکمه Submit
match = vision.find_image("submit_button.png", confidence=0.85)

if match:
    # کلیک روی مرکز دکمه
    mouse.click(*match.center)
    
    # تأیید کلیک
    if vision.verify_click_success(
        (match.x, match.y, match.width, match.height),
        timeout=2.0
    ):
        print("✅ Click verified!")
    else:
        print("❌ Click failed!")
else:
    print("Button not found")
```

### مثال 2: پیگیری تغییر رنگ

```python
# انتظار برای فعال شدن دکمه (تغییر رنگ از خاکستری به سبز)
button_x, button_y = 400, 300

# بررسی رنگ فعلی
current_color = vision.get_pixel_color(button_x, button_y)
print(f"Current color: RGB{current_color}")

# انتظار برای سبز شدن
if vision.wait_for_color(
    x=button_x,
    y=button_y,
    target_color=(0, 255, 0),  # سبز
    tolerance=20,
    timeout=30
):
    print("Button is now active!")
    mouse.click(button_x, button_y)
```

### مثال 3: پیدا کردن تمام آیکون‌ها

```python
# پیدا کردن تمام آیکون‌های Refresh روی صفحه
matches = vision.find_all_images(
    "refresh_icon.png",
    confidence=0.8,
    max_results=10
)

print(f"Found {len(matches)} refresh icons:")
for i, match in enumerate(matches, 1):
    print(f"{i}. Position: {match.center}, Confidence: {match.confidence:.2%}")
    
# کلیک روی اولین آیکون
if matches:
    mouse.click(*matches[0].center)
```

### مثال 4: فرم Automation با Visual Validation

```python
from core.keyboard_control import KeyboardController

keyboard = KeyboardController()

# پیدا کردن فیلد Name
name_field = vision.find_input_field("Name:")
if name_field:
    mouse.click(*name_field)
    keyboard.type_text("John Doe")
    
    # تأیید تایپ
    if vision.verify_text_typed("John Doe", fuzzy=True):
        print("✅ Name entered correctly")

# پیدا کردن فیلد Email
email_field = vision.find_input_field("Email:")
if email_field:
    mouse.click(*email_field)
    keyboard.type_text("john@example.com")

# پیدا کردن و کلیک دکمه Submit
submit_pos = vision.find_button("Submit")
if submit_pos:
    mouse.click(*submit_pos)
    
    # انتظار برای پیام تأیید
    if vision.wait_until_text_appears("Thank you", timeout=10):
        print("✅ Form submitted successfully!")
```

### مثال 5: Multi-Window Automation

```python
# انتظار برای باز شدن پنجره
if vision.wait_for_window("Notepad", timeout=20):
    vision.focus_window("Notepad")
    
    # انتظار برای بارگذاری کامل (صفحه stable)
    vision.wait_for_stable_screen(duration=1.0)
    
    # پیدا کردن دکمه Save
    save_button = vision.find_image("save_icon.png", confidence=0.9)
    if save_button:
        mouse.click(*save_button.center)
        
        # تأیید باز شدن دیالوگ Save
        if vision.wait_for_window("Save As", timeout=5):
            print("Save dialog opened")
```

### مثال 6: استخراج رنگ‌های غالب

```python
# آنالیز رنگ یک ناحیه (مثلاً یک chart)
dominant_colors = vision.get_dominant_colors(
    region=(100, 100, 400, 300),  # ناحیه chart
    num_colors=5
)

print("Dominant colors in chart:")
for i, color in enumerate(dominant_colors, 1):
    print(f"{i}. RGB{color}")
```

## تست کردن

### اجرای تست‌های اتوماتیک (Updated) 🆕

#### تست‌های پایه
```powershell
pytest tests/test_desktop_vision.py -v
```

#### تست‌های Enhanced (Week 2)
```powershell
pytest tests/test_desktop_vision_enhanced.py -v
```

#### اجرای همه تست‌ها
```powershell
pytest tests/test_desktop_vision*.py -v
```

**آمار تست‌ها:**
- تست‌های پایه: 15/15 passing ✅
- تست‌های Enhanced: 27/27 passing ✅
- جمع کل: 42/42 passing (100%) ✅

### اجرای دموهای تعاملی

```powershell
python tests/test_desktop_vision.py
```

این دستور دموهای زیر را اجرا می‌کند:
- گرفتن اسکرین‌شات
- لیست پنجره‌ها
- تست OCR
- تشخیص تغییرات

## عیب‌یابی (Troubleshooting)

### خطا: "OpenCV not available" 🆕

**حل:**
```powershell
pip install opencv-python
```

اگر خطای نصب دادید، ممکن است نیاز به Visual C++ Redistributable داشته باشید:
- دانلود از: https://aka.ms/vs/17/release/vc_redist.x64.exe

### خطا: "PIL not available"

**حل:**
```powershell
pip install pillow
```

### خطا: "Tesseract not found"

**حل 1 - نصب Tesseract:**
```powershell
winget install UB-Mannheim.TesseractOCR
```

**حل 2 - تنظیم مسیر به صورت دستی:**
```python
vision = DesktopVision(tesseract_cmd=r"C:\Program Files\Tesseract-OCR\tesseract.exe")
```

### خطا: "pygetwindow not available"

**حل:**
```powershell
pip install pygetwindow
```

### OCR متن را اشتباه می‌خواند

**راه‌حل‌ها:**
1. از `find_text_fuzzy()` استفاده کنید
2. `confidence_threshold` را پایین‌تر ببرید
3. از تصاویر با کیفیت بالاتر استفاده کنید

### پنجره‌ها پیدا نمی‌شوند

**بررسی کنید:**
```python
windows = vision.list_windows()
for win in windows:
    print(win.title)
```

اگر لیست خالی است، ممکن است `pygetwindow` به درستی نصب نشده باشد.

## مثال‌های کاربردی

### سناریو 1: باز کردن Notepad و نوشتن متن

```python
import pyautogui
from core.desktop_vision import DesktopVision

vision = DesktopVision()

# باز کردن Notepad (با استفاده از اتوماسیون موجود)
# ... کد باز کردن Notepad ...

# منتظر ماندن تا Notepad باز شود
if vision.wait_for_window("Notepad", timeout=10):
    print("✓ Notepad باز شد")
    
    # فوکوس روی Notepad
    vision.focus_window("Notepad")
    
    # نوشتن متن
    pyautogui.write("Hello from Software-AI!")
    
    # بررسی که متن نوشته شده
    text = vision.extract_text()
    if "Hello from Software-AI" in text:
        print("✓ متن با موفقیت نوشته شد")
```

### سناریو 2: کلیک روی دکمه با OCR

```python
import pyautogui
from core.desktop_vision import DesktopVision

vision = DesktopVision()

# پیدا کردن دکمه "OK"
position = vision.find_text("OK")

if position:
    x, y = position
    print(f"دکمه OK پیدا شد در ({x}, {y})")
    
    # کلیک روی دکمه
    pyautogui.click(x, y)
    print("✓ کلیک شد")
else:
    print("⚠ دکمه OK پیدا نشد")
```

### سناریو 3: منتظر ماندن برای نتیجه عملیات

```python
from core.desktop_vision import DesktopVision

vision = DesktopVision()

# انجام عملیاتی که زمان‌بر است
# ... کد اجرای عملیات ...

# منتظر ماندن تا "Loading..." ناپدید شود
print("⏳ در حال انتظار...")
if vision.wait_until_text_disappears("Loading...", timeout=60):
    print("✓ عملیات تمام شد")
    
    # بررسی موفقیت
    if vision.find_text("Success"):
        print("✓ عملیات موفقیت‌آمیز بود")
    elif vision.find_text("Error"):
        print("✗ خطا رخ داد")
```

## معماری

```
DesktopVision
├── Screenshot & Capture
│   ├── capture_screen()
│   └── save_screenshot()
├── OCR
│   ├── extract_text()
│   ├── get_all_text_boxes()
│   ├── find_text()
│   └── find_text_fuzzy()
├── Window Management
│   ├── get_active_window()
│   ├── list_windows()
│   ├── focus_window()
│   └── wait_for_window()
└── Change Detection
    ├── has_changed()
    ├── wait_for_change()
    ├── wait_until_text_appears()
    ├── wait_until_text_disappears()
    └── wait_for_stable_screen()
5. Template Matching (Week 2) 🆕
    ├── find_image()
    ├── find_all_images()
    └── wait_for_image()
6. Color Detection (Week 2) 🆕
    ├── get_pixel_color()
    ├── find_color()
    ├── wait_for_color()
    └── get_dominant_colors()
7. UI Recognition (Week 2) 🆕
    ├── find_button()
    ├── find_input_field()
    └── classify_element()
8. Visual Validation (Week 2) 🆕
    ├── verify_click_success()
    ├── verify_text_typed()
    ├── verify_element_visible()
    └── compare_screenshots()
```

## Roadmap

### ✅ Week 1: Desktop Vision (کامل)
- Screenshot ✅
- OCR با pytesseract ✅
- Window Management ✅
- Change Detection ✅

### ✅ Week 2 (Days 1-3): Action Layer - Enhanced Vision (کامل)
- **Days 1-2**: Mouse + Keyboard + Smart Wait ✅
- **Day 3**: Enhanced Desktop Vision ✅
  * Template Matching ✅
  * Color Detection ✅
  * UI Recognition ✅
  * Visual Validation ✅

### 📋 Week 2 (Days 4-10): Remaining
- **Day 4**: Action Controller (High-level actions)
- **Days 5-6**: Action Schema & Integration
- **Days 7-8**: Advanced Features
- **Days 9-10**: Testing & Polish

### 📋 Week 3: App Controllers
- NotepadController
- CalculatorController
- FileExplorerController
- Pattern‌های تکرارشونده

### 📋 Week 4: Task Decomposition
- تجزیه تسک‌ها به گام‌های کوچک
- یکپارچه‌سازی با AIBrain
- خطایابی خودکار

### 📋 Week 5-6: Integration
- Desktop + Web یکپارچه
- Multi-step workflows
- بهینه‌سازی performance

### 📋 Week 7-8: Polish
- Error handling پیشرفته
- Logging کامل
- Documentation کامل
-

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: November 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
