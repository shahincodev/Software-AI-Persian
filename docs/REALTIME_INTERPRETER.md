# Realtime Interpreter (تفسیرکننده زمان‌واقعی)

تفسیرکننده سبک برای حلقه زمان‌واقعی. قابلیت تفسیر snapshot‌های صفحه و شناسایی تغییرات state را فراهم می‌کند.

## اهداف

- **استخراج OCR سبک**: متن‌های درشت و عنوان پنجره (تنها متن‌های مهم)
- **شناسایی تغییرات**: تشخیص آیا صفحه تغییر کرده یا ثابت
- **حفظ سیاق**: ذخیره state قبلی برای مقایسه و یادگیری
- **کم مصرف**: برای نرخ پایین (1–2 fps)

## ساختار

### کلاس‌ها

**`StateSnapshot`**
- `timestamp`: زمان snapshot
- `active_window`: پنجره فعال (WindowInfo)
- `screen_texts`: متن‌های شناسایی شده
- `detected_elements`: عناصر UI تشخیص‌شده
- `raw_metadata`: داده‌های خام (title، تعداد متن)

**`InterpretationResult`**
- `action`: تصمیم ("noop" | "hint" | "act")
- `risk_score`: امتیاز ریسک (0–100)
- `confidence`: درجه اطمینان (0–1)
- `changed`: آیا state تغییر کرده
- `prev_snapshot` / `curr_snapshot`: مقایسه state
- `message`: توضیح تصمیم

**`RealtimeInterpreter`**
- تفسیر snapshot‌ها
- شناسایی تغییرات
- حفظ سیاق تاریخی

## رفتار

### OCR سبک

- تنها متن‌های **بالای `text_threshold`** (پیش‌فرض: 3) کاراکتر شمرده می‌شوند
- حداکثر **`max_texts`** متن (پیش‌فرض: 10) ثبت می‌شود
- برای پنجره‌های دارای متن کثیر، عملکرد بهتر است

### تشخیص تغییرات

1. **تغییر عنوان پنجره**: اگر پنجره فعال تغییر کرد → `changed = True`
2. **تغییر متن‌ها**: اگر مجموعهٔ متن‌ها فرق کرد → `changed = True`
3. پیش‌فرض (تغییری نیست) → `changed = False`

### تصمیم‌گیری (در main.py)

- **Safe**: فقط `hint`، بدون اقدام
- **Power + تغییر**: `act` (احتمال اقدام بیشتر)
- **Power + بدون تغییر**: `hint`

## استفاده

```python
from core.realtime_interpreter import RealtimeInterpreter
from core.desktop_vision import DesktopVision

# ایجاد instance
vision = DesktopVision()
interpreter = RealtimeInterpreter(
    vision=vision,
    ocr_enabled=True,
    text_threshold=3,
    max_texts=10
)

# تفسیر snapshot
result = await interpreter.interpret(safety_mode="power", risk_threshold=70.0)
print(f"Action: {result.action}")
print(f"Changed: {result.changed}")
print(f"Confidence: {result.confidence:.0%}")

# دریافت سیاق
context = interpreter.get_context()
```

## پارامترها

| پارامتر | نوع | پیش‌فرض | توضیح |
|---|---|---|---|
| `vision` | DesktopVision | - | ماژول بینایی |
| `ocr_enabled` | bool | True | فعال‌سازی OCR |
| `text_threshold` | int | 3 | حداقل طول متن |
| `max_texts` | int | 10 | حداکثر متن‌های ثبت |

## ایمنی

- به صورت async: عدم انسداد حلقه اصلی
- exception handling: خرابی OCR یا window detection مسدود نمی‌کند
- logging: تمام failures در DEBUG level ثبت می‌شوند

## تست

[فایل تست: `tests/test_realtime_interpreter.py`]

- تست capture snapshot
- تست تشخیص تغییرات
- تست OCR سبک
- تست مقایسه state

## نکات توسعه آینده

- اضافه کردن template matching برای عناصر UI
- cache texts برای بهتر کردن عملکرد
- statistical comparison برای confident تر detection
- integration با plan validator برای risk scoring
