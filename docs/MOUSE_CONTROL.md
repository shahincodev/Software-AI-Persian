# راهنمای MouseController

کنترل هوشمند موس با یکپارچگی AI برای Software-AI (Persian Version).

## 📋 فهرست مطالب

- [معرفی](#معرفی)
- [نصب](#نصب)
- [استفاده سریع](#استفاده-سریع)
- [معماری](#معماری)
- [API Reference](#api-reference)
- [مثال‌های کاربردی](#مثالهای-کاربردی)
- [ویژگی‌های پیشرفته](#ویژگیهای-پیشرفته)
- [امنیت](#امنیت)
- [عیب‌یابی](#عیبیابی)

---

## 🎯 معرفی

`MouseController` فراتر از یک wrapper ساده برای `pyautogui` است. این یک **سیستم هوشمند کنترل موس** است که با AI یکپارچه شده و قابلیت‌های زیر را دارد:

### ویژگی‌های کلیدی

✅ **Safety Validation**: جلوگیری از کلیک‌های خطرناک در مناطق حساس  
✅ **Human Behavior Simulation**: تقلید از رفتار انسانی با Bezier curves و تاخیرهای تصادفی  
✅ **Vision-Guided Operations**: کلیک روی متن/تصویر با استفاده از AI  
✅ **Stats & Audit Trail**: ردیابی کامل تمام عملیات برای تحلیل  
✅ **Persian Language Support**: پشتیبانی کامل از متن فارسی در OCR

### چرا MouseController؟

| ویژگی | pyautogui معمولی | MouseController (AI-Powered) |
|-------|-------------------|------------------------------|
| کنترل موس | ✅ | ✅ |
| اعتبارسنجی امنیتی | ❌ | ✅ |
| رفتار انسانی | ❌ | ✅ (Bezier curves) |
| کلیک روی متن | ❌ | ✅ (با Vision AI) |
| کلیک روی تصویر | محدود | ✅ (template matching) |
| آمارگیری | ❌ | ✅ |
| Audit Trail | ❌ | ✅ |

---

## 📦 نصب

### پیش‌نیازها

```bash
# کتابخانه‌های ضروری
pip install pyautogui pynput

# برای Vision-guided operations (اختیاری)
pip install pillow opencv-python pytesseract
```

### نصب Tesseract OCR (برای متن فارسی)

**Windows:**
```bash
# دانلود از:
# https://github.com/UB-Mannheim/tesseract/wiki

# نصب و اضافه کردن به PATH
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-fas
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

---

## 🚀 استفاده سریع

### مثال ساده

```python
from core.mouse_control import MouseController, MouseButton, ClickPattern

# ساخت کنترلر
mouse = MouseController()

# حرکت و کلیک
mouse.move(500, 300, duration=0.5)
mouse.click(500, 300)

# دوبل کلیک
mouse.click(500, 300, clicks=2)

# کلیک راست
mouse.click(500, 300, button=MouseButton.RIGHT)

# اسکرول
mouse.scroll(5)  # اسکرول به بالا
mouse.scroll(-5)  # اسکرول به پایین
```

### مثال با رفتار انسانی

```python
# فعال‌سازی رفتار انسانی
mouse = MouseController(human_behavior=True)

# کلیک با سرعت طبیعی انسان
mouse.click_human(500, 300, pattern=ClickPattern.HUMAN_NORMAL)

# کلیک کند (برای دقت بیشتر)
mouse.click_human(500, 300, pattern=ClickPattern.HUMAN_SLOW)

# حرکت هموار با منحنی Bezier
mouse.move(800, 400, duration=2.0, smooth=True)
```

### مثال با Vision AI

```python
from core.desktop_vision import DesktopVision

# ساخت سیستم Vision
vision = DesktopVision()
mouse = MouseController(vision_system=vision)

# کلیک روی دکمه "OK"
mouse.click_on_text("OK")

# کلیک روی دکمه "تایید" (فارسی)
mouse.click_on_text("تایید")

# کلیک روی آیکن
mouse.click_on_image("assets/close_button.png", confidence=0.8)
```

---

## 🏗️ معماری

### ساختار کلاس

```
MouseController
├── Safety & Validation
│   ├── is_safe_position()
│   └── validate_coordinates()
│
├── Human Behavior Simulation
│   ├── _add_human_variation()
│   ├── _get_human_delay()
│   └── _bezier_curve()
│
├── Core Mouse Operations
│   ├── get_position()
│   ├── move()
│   ├── click()
│   ├── click_human()
│   ├── drag()
│   └── scroll()
│
├── Vision-Guided Operations (AI)
│   ├── click_on_text()
│   └── click_on_image()
│
└── Utility & Stats
    ├── get_stats()
    └── reset_stats()
```

### Data Classes

```python
@dataclass
class MouseAction:
    """ذخیره اطلاعات هر اقدام برای Audit Trail."""
    action_type: str
    x: Optional[int]
    y: Optional[int]
    button: Optional[str]
    timestamp: datetime
    duration: float
    success: bool
```

### Enums

```python
class MouseButton(Enum):
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"

class ClickPattern(Enum):
    INSTANT = "instant"           # بدون تاخیر
    HUMAN_FAST = "human_fast"     # 0.05-0.1s
    HUMAN_NORMAL = "human_normal" # 0.1-0.2s
    HUMAN_SLOW = "human_slow"     # 0.2-0.5s
    DOUBLE_CLICK = "double_click"
    TRIPLE_CLICK = "triple_click"
```

---

## 📚 API Reference

### ساخت MouseController

```python
MouseController(
    safety_enabled: bool = True,
    human_behavior: bool = True,
    vision_system: Optional[DesktopVision] = None
)
```

**پارامترها:**
- `safety_enabled`: فعال‌سازی بررسی‌های امنیتی (محدوده صفحه)
- `human_behavior`: تقلید از رفتار انسانی (تاخیر، نویز، منحنی)
- `vision_system`: سیستم بینایی برای عملیات هوشمند

---

### متدهای اصلی

#### `get_position() -> tuple[int, int]`

دریافت موقعیت فعلی موس.

```python
x, y = mouse.get_position()
print(f"Mouse at ({x}, {y})")
```

---

#### `move(x, y, duration=0.5, smooth=True) -> bool`

حرکت موس به موقعیت مشخص.

**پارامترها:**
- `x`, `y`: موقعیت هدف
- `duration`: مدت زمان حرکت (ثانیه)
- `smooth`: استفاده از منحنی Bezier

**مثال:**
```python
# حرکت سریع
mouse.move(500, 300, duration=0.2, smooth=False)

# حرکت هموار و طبیعی
mouse.move(500, 300, duration=1.0, smooth=True)
```

---

#### `click(x=None, y=None, button=MouseButton.LEFT, clicks=1, interval=0.1) -> bool`

کلیک موس در موقعیت مشخص.

**پارامترها:**
- `x`, `y`: موقعیت (None = موقعیت فعلی)
- `button`: دکمه موس
- `clicks`: تعداد کلیک‌ها
- `interval`: فاصله بین کلیک‌ها

**مثال:**
```python
# کلیک چپ
mouse.click(100, 100)

# دوبل کلیک
mouse.click(100, 100, clicks=2)

# کلیک راست
mouse.click(100, 100, button=MouseButton.RIGHT)

# کلیک میانی
mouse.click(100, 100, button=MouseButton.MIDDLE)
```

---

#### `click_human(x, y, button=MouseButton.LEFT, pattern=ClickPattern.HUMAN_NORMAL) -> bool`

کلیک با الگوی رفتاری انسانی.

**پارامترها:**
- `x`, `y`: موقعیت هدف
- `button`: دکمه موس
- `pattern`: الگوی کلیک

**مثال:**
```python
# کلیک طبیعی انسانی
mouse.click_human(500, 300)

# کلیک سریع
mouse.click_human(500, 300, pattern=ClickPattern.HUMAN_FAST)

# کلیک کند (برای دقت)
mouse.click_human(500, 300, pattern=ClickPattern.HUMAN_SLOW)

# کلیک فوری (بدون تاخیر)
mouse.click_human(500, 300, pattern=ClickPattern.INSTANT)
```

**مقایسه الگوها:**

| الگو | تاخیر | کاربرد |
|------|-------|--------|
| INSTANT | 0s | عملیات سریع، تست |
| HUMAN_FAST | 0.05-0.1s | کاربر حرفه‌ای |
| HUMAN_NORMAL | 0.1-0.2s | کاربر عادی |
| HUMAN_SLOW | 0.2-0.5s | دقت بالا، فرم‌ها |

---

#### `drag(start_x, start_y, end_x, end_y, duration=0.5, button=MouseButton.LEFT) -> bool`

کشیدن از یک نقطه به نقطه دیگر.

**مثال:**
```python
# کشیدن فایل
mouse.drag(100, 100, 500, 300)

# انتخاب متن با drag
mouse.drag(100, 200, 300, 200, duration=0.3)
```

---

#### `scroll(clicks, x=None, y=None) -> bool`

اسکرول صفحه.

**مثال:**
```python
# اسکرول به بالا
mouse.scroll(5)

# اسکرول به پایین
mouse.scroll(-5)

# اسکرول در موقعیت مشخص
mouse.scroll(3, x=500, y=300)
```

---

### Vision-Guided Operations (AI)

#### `click_on_text(text, button=MouseButton.LEFT, pattern=ClickPattern.HUMAN_NORMAL) -> bool`

کلیک روی متن با استفاده از OCR.

**نیازمندیها:**
- Vision system باید تنظیم شده باشد
- Tesseract OCR نصب باشد

**مثال:**
```python
from core.desktop_vision import DesktopVision

vision = DesktopVision()
mouse = MouseController(vision_system=vision)

# کلیک روی دکمه انگلیسی
mouse.click_on_text("OK")
mouse.click_on_text("Submit")

# کلیک روی دکمه فارسی
mouse.click_on_text("تایید")
mouse.click_on_text("ذخیره")

# کلیک راست روی متن
mouse.click_on_text("File", button=MouseButton.RIGHT)
```

**خطاها:**
- `ValueError`: اگر Vision system تنظیم نشده
- `RuntimeError`: اگر متن پیدا نشود

---

#### `click_on_image(image_path, confidence=0.8, button=MouseButton.LEFT, pattern=ClickPattern.HUMAN_NORMAL) -> bool`

کلیک روی تصویر با template matching.

**پارامترها:**
- `image_path`: مسیر تصویر template
- `confidence`: آستانه اطمینان (0.0-1.0)

**مثال:**
```python
# کلیک روی آیکن
mouse.click_on_image("assets/icons/close.png")

# کلیک با اطمینان بالا
mouse.click_on_image("button_ok.png", confidence=0.9)

# کلیک راست روی تصویر
mouse.click_on_image("icon.png", button=MouseButton.RIGHT)
```

**نکات:**
- تصویر باید واضح و با کیفیت باشد
- `confidence=0.8` معمولاً مناسب است
- برای تصاویر مشابه، confidence را افزایش دهید

---

### امنیت و اعتبارسنجی

#### `is_safe_position(x, y) -> bool`

بررسی امن بودن موقعیت.

```python
if mouse.is_safe_position(500, 300):
    mouse.click(500, 300)
else:
    print("Unsafe position!")
```

**محدوده‌های امن پیش‌فرض:**
```python
{
    'min_x': 10,
    'max_x': screen_width - 10,
    'min_y': 10,
    'max_y': screen_height - 50  # فضا برای taskbar
}
```

---

#### `validate_coordinates(x, y) -> tuple[int, int]`

اعتبارسنجی و تصحیح مختصات.

```python
try:
    x, y = mouse.validate_coordinates(500, 300)
    # موقعیت معتبر است
except ValueError as e:
    print(f"Invalid position: {e}")
```

---

### آمار و تحلیل

#### `get_stats() -> dict`

دریافت آمار استفاده.

```python
stats = mouse.get_stats()
print(f"Total clicks: {stats['total_clicks']}")
print(f"Success rate: {stats['success_rate']}")
```

**خروجی:**
```python
{
    'total_clicks': 42,
    'total_moves': 38,
    'total_drags': 5,
    'total_scrolls': 12,
    'failed_actions': 2,
    'total_actions': 97,
    'success_rate': '97.94%',
    'recent_actions': 50
}
```

---

#### `reset_stats()`

بازنشانی آمار.

```python
mouse.reset_stats()
```

---

## 💡 مثال‌های کاربردی

### مثال 1: فرم‌ پُر کردن

```python
from core.mouse_control import MouseController, ClickPattern

mouse = MouseController(human_behavior=True)

# کلیک روی فیلد نام
mouse.click_human(200, 100, pattern=ClickPattern.HUMAN_NORMAL)
# تایپ نام (با keyboard_control)

# کلیک روی فیلد ایمیل
mouse.click_human(200, 150, pattern=ClickPattern.HUMAN_NORMAL)
# تایپ ایمیل

# کلیک روی دکمه Submit
mouse.click_human(300, 250, pattern=ClickPattern.HUMAN_SLOW)
```

---

### مثال 2: خودکارسازی با Vision

```python
from core.desktop_vision import DesktopVision
from core.mouse_control import MouseController

vision = DesktopVision()
mouse = MouseController(vision_system=vision, human_behavior=True)

# باز کردن منو File
mouse.click_on_text("File")
time.sleep(0.5)

# کلیک روی Save
mouse.click_on_text("Save")
time.sleep(0.5)

# تایید دیالوگ
mouse.click_on_text("OK")
```

---

### مثال 3: اسکریپت تکرارپذیر

```python
def click_sequence(mouse, positions, delay=0.5):
    """کلیک روی لیستی از موقعیت‌ها."""
    for x, y in positions:
        mouse.click_human(x, y)
        time.sleep(delay)
    
    # نمایش آمار
    stats = mouse.get_stats()
    print(f"Completed {stats['total_clicks']} clicks")
    print(f"Success rate: {stats['success_rate']}")

# استفاده
positions = [(100, 100), (200, 200), (300, 300)]
click_sequence(mouse, positions)
```

---

### مثال 4: انتخاب و کپی متن

```python
# انتخاب متن با drag
mouse.drag(100, 200, 400, 200, duration=0.5)

# کلیک راست
mouse.click(250, 200, button=MouseButton.RIGHT)

# کلیک روی Copy
mouse.click_on_text("Copy")
```

---

## 🎨 ویژگی‌های پیشرفته

### 1. Bezier Curve Movement

حرکت طبیعی موس با منحنی‌های Bezier:

```python
# حرکت هموار با 20 نقطه میانی
mouse = MouseController(human_behavior=True)
mouse.move(800, 400, duration=2.0, smooth=True)
```

**مزایا:**
- رفتار طبیعی‌تر
- جلوگیری از تشخیص ربات
- قابل تنظیم

---

### 2. Human Variation

نویز تصادفی برای شبیه‌سازی دقت انسان:

```python
# هر کلیک کمی متفاوت است (±2 پیکسل)
for _ in range(10):
    mouse.click_human(500, 300)
    # هر بار مختصات کمی تغییر می‌کند
```

---

### 3. Audit Trail

ردیابی تمام عملیات:

```python
# بعد از چند عملیات
for action in mouse.action_history:
    print(f"{action.timestamp}: {action.action_type} at ({action.x}, {action.y})")
    print(f"  Duration: {action.duration:.3f}s, Success: {action.success}")
```

---

### 4. Custom Safe Bounds

تنظیم محدوده‌های امن سفارشی:

```python
mouse = MouseController()

# تنظیم محدوده سفارشی
mouse.safe_bounds = {
    'min_x': 50,
    'max_x': 1200,
    'min_y': 50,
    'max_y': 800,
}

# حالا فقط در این محدوده کار می‌کند
```

---

## 🔒 امنیت

### محدودیت‌های پیش‌فرض

```python
# خودکار از کلیک در مناطق خطرناک جلوگیری می‌کند:
# - گوشه‌های صفحه (FAILSAFE)
# - نزدیک taskbar
# - خارج از صفحه
```

### غیرفعال کردن امنیت

⚠️ **فقط برای تست!**

```python
mouse = MouseController(safety_enabled=False)
# حالا تمام موقعیت‌ها مجاز است
```

### FAILSAFE Mode

```python
# حرکت به گوشه بالا چپ برای توقف اضطراری
pyautogui.FAILSAFE = True  # پیش‌فرض فعال است
```

---

## 🐛 عیب‌یابی

### خطای Import

```python
ImportError: pyautogui is required
```

**راه‌حل:**
```bash
pip install pyautogui pynput
```

---

### Vision System خطا

```python
ValueError: Vision system not configured
```

**راه‌حل:**
```python
from core.desktop_vision import DesktopVision

vision = DesktopVision()
mouse = MouseController(vision_system=vision)
```

---

### متن پیدا نمی‌شود

```python
RuntimeError: Text not found: 'OK'
```

**راه‌حل:**
1. بررسی صحت املایی متن
2. اطمینان از نمایش متن روی صفحه
3. تنظیم زبان OCR (فارسی/انگلیسی)

---

### عملیات خیلی کند است

```python
# غیرفعال کردن رفتار انسانی برای سرعت
mouse = MouseController(human_behavior=False)

# یا استفاده از INSTANT pattern
mouse.click_human(x, y, pattern=ClickPattern.INSTANT)
```

---

### Logging برای دیباگ

```python
import logging

logging.basicConfig(level=logging.DEBUG)
# حالا تمام عملیات لاگ می‌شوند
```

---

## 📊 تست و کیفیت

### اجرای تست‌ها

```bash
# تمام تست‌ها
pytest tests/test_mouse_control.py -v

# فقط تست‌های سریع
pytest tests/test_mouse_control.py -v -m "not slow"

# با coverage
pytest tests/test_mouse_control.py --cov=core.mouse_control
```

### نتایج تست

```
✅ 33 passed
⏭️  1 skipped (integration test)
⚠️  2 warnings (custom markers)

Coverage: 97%
```

---

## 🔗 منابع مرتبط

- [Desktop Vision Guide](./DESKTOP_VISION.md) - سیستم بینایی
- [Keyboard Control](./KEYBOARD_CONTROL.md) - کنترل کیبورد (Week 2)
- [Smart Wait](./SMART_WAIT.md) - انتظار هوشمند (Week 2)
- [Week 2 Plan](./WEEK2_ACTION_LAYER_PLAN.md) - نقشه راه کامل

---

## 🤝 مشارکت

برای گزارش باگ یا پیشنهاد ویژگی:
- GitHub Issues: [Software-AI Issues](https://github.com/tahanilishahin/Software-AI-Persian/issues)

---

## 📄 مجوز

SPDX-License-Identifier: NOASSERTION  
Copyright (c) 2025 Shahin

---

**Software-AI (Persian Version)** - AI on Windows Screen 🖱️🤖
