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

## تست کردن

### اجرای تست‌های اتوماتیک

```powershell
pytest test_desktop_vision.py -v
```

### اجرای دموهای تعاملی

```powershell
python test_desktop_vision.py
```

این دستور دموهای زیر را اجرا می‌کند:
- گرفتن اسکرین‌شات
- لیست پنجره‌ها
- تست OCR
- تشخیص تغییرات

## عیب‌یابی (Troubleshooting)

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
```

## Roadmap

### ✅ Week 1: Desktop Vision (فعلی)
- Screenshot
- OCR با pytesseract
- Window Management
- Change Detection

### 📋 Week 2: Action Layer
- Click با موقعیت دقیق
- Type با شبیه‌سازی keyboard
- Smart Wait با retry logic
- یکپارچه‌سازی با ExecutionManager

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
- تست‌های جامع

## کمک‌های بیشتر

برای سوالات و مشکلات:
- [GitHub Issues](https://github.com/tahanilishahin/Sofware-AI-Persian/issues)
- [QUICKSTART.md](QUICKSTART.md)
- [AI_WINDOWS_CONTROL.md](AI_WINDOWS_CONTROL.md)

---
**نکته:** این سیستم هنوز در Week 1 است. قابلیت‌های پیشرفته‌تر در هفته‌های آینده اضافه خواهند شد.
