# 🎯 Desktop Actions - اقدامات دسکتاپ

سیستم اقدامات Desktop برای تعریف و اجرای عملیات‌های خودکار روی رابط کاربری.

## 📋 فهرست مطالب

- [معرفی](#معرفی)
- [انواع اقدامات](#انواع-اقدامات)
- [استفاده](#استفاده)
- [ارزیابی خطر](#ارزیابی-خطر)
- [اعتبارسنجی](#اعتبارسنجی)
- [سریال‌سازی](#سریال‌سازی)

---

## 🎯 معرفی

ماژول `desktop_actions` مجموعه‌ای از کلاس‌های Action برای تعامل با رابط کاربری ویندوز فراهم می‌کند. این اقدامات به صورت یکنواخت طراحی شده‌اند و شامل:

- **ارزیابی خطر**: هر اقدام سطح خطر خود را مشخص می‌کند
- **اعتبارسنجی**: بررسی صحت پارامترها قبل از اجرا
- **توصیف فارسی**: توضیح خوانا برای کاربر
- **سریال‌سازی**: ذخیره و بازیابی از JSON/Dict

---

## 📦 انواع اقدامات

### 1️⃣ ClickAction - کلیک روی عناصر

**کاربرد**: کلیک روی دکمه‌ها، لینک‌ها و عناصر UI

```python
from core.desktop_actions import ClickAction

# کلیک با متن
action = ClickAction(target="OK", button="left")

# کلیک با مختصات
action = ClickAction(target=(500, 300), button="right", clicks=2)

# اجرا
valid, msg = action.validate()
if valid:
    risk = action.get_risk_level()
    desc = action.describe()  # "کلیک چپ روی OK"
```

**پارامترها**:
- `target`: متن برای جستجو یا مختصات `(x, y)` - **الزامی**
- `button`: دکمه موس (`left`, `right`, `middle`) - پیش‌فرض: `left`
- `clicks`: تعداد کلیک (1-3) - پیش‌فرض: `1`
- `verify`: تایید نتیجه بعد از کلیک - پیش‌فرض: `True`
- `confidence`: حداقل اطمینان برای یافتن عنصر (0.0-1.0) - پیش‌فرض: `0.8`
- `timeout`: حداکثر زمان انتظار (ثانیه) - پیش‌فرض: `10`

**سطح خطر**:
- کلیک چپ معمولی: `SAFE`
- کلیک راست: `LOW` (می‌تواند منوی خطرناک باز کند)
- دابل/تریپل کلیک: `LOW` (می‌تواند برنامه باز کند)

---

### 2️⃣ TypeAction - تایپ متن

**کاربرد**: تایپ متن در فیلدهای ورودی

```python
from core.desktop_actions import TypeAction

# تایپ ساده
action = TypeAction(text="سلام دنیا")

# تایپ در فیلد خاص
action = TypeAction(
    text="user@example.com",
    target="Email",
    clear_first=True,
    verify=True
)

# تایپ سریع با clipboard
action = TypeAction(
    text="متن طولانی...",
    use_clipboard=True
)
```

**پارامترها**:
- `text`: متن برای تایپ - **الزامی**
- `target`: فیلد هدف (اگر `None` باشد، در فیلد فعال تایپ می‌شود)
- `clear_first`: پاک کردن محتوای قبلی - پیش‌فرض: `False`
- `interval`: تاخیر بین کاراکترها (ثانیه) - پیش‌فرض: `0.05`
- `verify`: تایید محتوا بعد از تایپ - پیش‌فرض: `True`
- `use_clipboard`: استفاده از clipboard برای سرعت - پیش‌فرض: `False`

**سطح خطر**:
- متن عادی: `LOW`
- محتوای حساس (password, credit card): `MEDIUM`
- دستورات مخرب (`rm -rf`, `format`, `shutdown`): `HIGH`

---

### 3️⃣ WaitAction - انتظار هوشمند

**کاربرد**: انتظار برای شرایط مختلف

```python
from core.desktop_actions import WaitAction

# انتظار برای ظاهر شدن عنصر
action = WaitAction(wait_type="element", target="Save Button", timeout=30)

# انتظار زمان‌دار
action = WaitAction(wait_type="time", target=5.0)

# انتظار برای باز شدن پنجره
action = WaitAction(wait_type="window", target="Notepad")

# انتظار برای ناپدید شدن (inverse)
action = WaitAction(
    wait_type="element",
    target="Loading...",
    inverse=True
)
```

**پارامترها**:
- `wait_type`: نوع انتظار - **الزامی**
  - `element`: انتظار برای عنصر UI
  - `window`: انتظار برای پنجره
  - `process`: انتظار برای فرآیند
  - `change`: انتظار برای تغییر ناحیه صفحه
  - `time`: انتظار زمانی ساده
- `target`: هدف (بسته به نوع) - برای `element`, `window`, `process` **الزامی**
- `timeout`: حداکثر زمان انتظار (ثانیه) - پیش‌فرض: `30`
- `check_interval`: فاصله بررسی (ثانیه) - پیش‌فرض: `0.5`
- `inverse`: انتظار برای ناپدید شدن - پیش‌فرض: `False`

**سطح خطر**: همیشه `SAFE` (انتظار خطری ندارد)

---

### 4️⃣ DragDropAction - کشیدن و رها کردن

**کاربرد**: Drag & Drop فایل‌ها و عناصر

```python
from core.desktop_actions import DragDropAction

# کشیدن فایل به پوشه
action = DragDropAction(source="file.txt", target="Documents")

# کشیدن با مختصات
action = DragDropAction(
    source=(100, 100),
    target=(500, 500),
    duration=1.0
)

# کشیدن با دکمه راست
action = DragDropAction(
    source="Image.png",
    target="Desktop",
    button="right"
)
```

**پارامترها**:
- `source`: مبدا (متن یا مختصات) - **الزامی**
- `target`: مقصد (متن یا مختصات) - **الزامی**
- `duration`: مدت زمان حرکت (ثانیه) - پیش‌فرض: `0.5`
- `verify`: تایید نتیجه - پیش‌فرض: `True`
- `button`: دکمه موس - پیش‌فرض: `left`

**سطح خطر**: همیشه `MEDIUM` (می‌تواند فایل منتقل کند)

---

### 5️⃣ HotkeyAction - میانبرهای صفحه‌کلید

**کاربرد**: فشردن ترکیب کلیدها

```python
from core.desktop_actions import HotkeyAction

# کپی
action = HotkeyAction(keys=["ctrl", "c"])

# پیست
action = HotkeyAction(keys=["ctrl", "v"])

# تعویض پنجره
action = HotkeyAction(keys=["alt", "tab"])

# ترکیب 3 کلیدی
action = HotkeyAction(
    keys=["ctrl", "shift", "esc"],
    hold_duration=0.2
)
```

**پارامترها**:
- `keys`: لیست کلیدها به ترتیب - **الزامی**
- `interval`: تاخیر بین فشردن کلیدها (ثانیه) - پیش‌فرض: `0.1`
- `hold_duration`: مدت نگه داشتن (ثانیه) - پیش‌فرض: `0.0`

**سطح خطر**:
- میانبرهای عادی (Ctrl+C, Ctrl+V): `LOW`
- میانبرهای خطرناک (Alt+F4, Win+L, Ctrl+Alt+Del): `MEDIUM`

---

### 6️⃣ ScrollAction - اسکرول صفحه

**کاربرد**: اسکرول عمودی و افقی

```python
from core.desktop_actions import ScrollAction

# اسکرول به پایین
action = ScrollAction(direction="down", clicks=5)

# اسکرول در عنصر خاص
action = ScrollAction(
    direction="up",
    clicks=3,
    target="ListView"
)

# اسکرول نرم
action = ScrollAction(
    direction="down",
    clicks=10,
    smooth=True
)
```

**پارامترها**:
- `direction`: جهت اسکرول (`up`, `down`, `left`, `right`) - **الزامی**
- `clicks`: تعداد کلیک اسکرول (شدت) - پیش‌فرض: `3`
- `target`: عنصر یا مختصات هدف - پیش‌فرض: `None` (موقعیت فعلی موس)
- `smooth`: اسکرول نرم و تدریجی - پیش‌فرض: `False`

**سطح خطر**: همیشه `SAFE` (اسکرول خطری ندارد)

---

## 💻 استفاده

### ایجاد Action

```python
from core.desktop_actions import ClickAction, TypeAction

# ایجاد مستقیم
click = ClickAction(target="Submit", button="left")
type_action = TypeAction(text="Hello World")
```

### اعتبارسنجی

```python
# بررسی اعتبار
valid, message = action.validate()
if valid:
    print("✅ اقدام معتبر است")
else:
    print(f"❌ خطا: {message}")
```

### ارزیابی خطر

```python
from core.system_actions import RiskLevel

# بررسی سطح خطر
risk = action.get_risk_level()

if risk == RiskLevel.SAFE:
    # اجرای مستقیم
    pass
elif risk == RiskLevel.LOW:
    # اجرا با لاگ
    pass
elif risk == RiskLevel.MEDIUM:
    # درخواست تایید
    pass
else:  # HIGH or CRITICAL
    # مسدود کردن یا تایید قوی
    pass
```

### توصیف فارسی

```python
# دریافت توضیح خوانا
description = action.describe()
print(description)  # مثال: "کلیک چپ روی OK"
```

---

## 🔒 ارزیابی خطر

هر Action سطح خطر خود را مشخص می‌کند:

| سطح | توضیح | مثال |
|-----|-------|------|
| `SAFE` | بدون خطر | اسکرول، انتظار |
| `LOW` | خطر کم | کلیک معمولی، تایپ عادی |
| `MEDIUM` | خطر متوسط | Drag & Drop، میانبرهای خاص |
| `HIGH` | خطر زیاد | تایپ دستورات مخرب |
| `CRITICAL` | خطر بحرانی | (برای اقدامات سیستمی) |

**مثال**:

```python
from core.desktop_actions import TypeAction
from core.system_actions import RiskLevel

# متن عادی - LOW
action1 = TypeAction(text="Hello")
assert action1.get_risk_level() == RiskLevel.LOW

# دستور خطرناک - HIGH
action2 = TypeAction(text="rm -rf /")
assert action2.get_risk_level() == RiskLevel.HIGH

# محتوای حساس - MEDIUM
action3 = TypeAction(text="my password is 123456")
assert action3.get_risk_level() == RiskLevel.MEDIUM
```

---

## ✅ اعتبارسنجی

همه Actions پارامترهای خود را اعتبارسنجی می‌کنند:

```python
from core.desktop_actions import ClickAction

# مثال 1: مختصات معتبر
action = ClickAction(target=(100, 200))
valid, msg = action.validate()
assert valid == True

# مثال 2: مختصات منفی (نامعتبر)
action = ClickAction(target=(-10, 50))
valid, msg = action.validate()
assert valid == False
assert "منفی" in msg

# مثال 3: تعداد کلیک نامعتبر
action = ClickAction(target="OK", clicks=10)
valid, msg = action.validate()
assert valid == False
assert "بین 1 تا 3" in msg
```

**قوانین اعتبارسنجی**:

### ClickAction
- مختصات باید >= 0 باشند
- متن نباید خالی باشد
- `clicks` بین 1 تا 3
- `confidence` بین 0.0 تا 1.0
- `timeout` بین 1 تا 60 ثانیه

### TypeAction
- `text` نباید خالی باشد
- طول `text` حداکثر 10000 کاراکتر
- `interval` بین 0 تا 1 ثانیه

### WaitAction
- `wait_type` باید یکی از مقادیر مجاز باشد
- برای `element`, `window`, `process` حتماً `target` باید مقداردهی شود
- `timeout` بین 1 تا 300 ثانیه
- `check_interval` بین 0.1 تا 10 ثانیه

### DragDropAction
- `source` و `target` نباید خالی باشند
- مختصات باید >= 0 باشند
- `duration` بین 0.1 تا 5 ثانیه

### HotkeyAction
- حداقل 1 کلید لازم است
- حداکثر 4 کلید مجاز
- هر کلید نباید خالی باشد
- `interval` بین 0 تا 1 ثانیه
- `hold_duration` بین 0 تا 10 ثانیه

### ScrollAction
- `direction` باید یکی از `up`, `down`, `left`, `right` باشد
- `clicks` بین 1 تا 20
- مختصات `target` باید >= 0 باشند

---

## 💾 سریال‌سازی

Actions قابل تبدیل به JSON/Dict و بازگشت هستند:

### به Dict/JSON

```python
from core.desktop_actions import ClickAction, serialize_action

action = ClickAction(target="OK", button="left", clicks=1)

# تبدیل به dict
data = serialize_action(action)
print(data)
# {
#     'type': 'click',
#     'target': 'OK',
#     'button': 'left',
#     'clicks': 1,
#     'verify': True,
#     'confidence': 0.8,
#     'timeout': 10,
#     'action_id': '...',
#     'dry_run': False,
#     ...
# }

# تبدیل به JSON
import json
json_str = json.dumps(data, ensure_ascii=False, indent=2)
```

### از Dict/JSON

```python
from core.desktop_actions import create_action_from_dict

# از dict
data = {
    'type': 'click',
    'target': 'Submit',
    'button': 'left'
}
action = create_action_from_dict(data)

# از JSON
import json
json_str = '{"type": "type", "text": "Hello"}'
data = json.loads(json_str)
action = create_action_from_dict(data)
```

### انواع Action در سریال‌سازی

| کلاس Action | نوع در Dict (`type`) |
|-------------|----------------------|
| ClickAction | `click` |
| TypeAction | `type` |
| WaitAction | `wait` |
| DragDropAction | `drag_drop` |
| HotkeyAction | `hotkey` |
| ScrollAction | `scroll` |

---

## 🧪 تست‌ها

67 تست جامع برای همه اقدامات:

```bash
pytest tests/test_desktop_actions.py -v
```

**دسته‌بندی تست‌ها**:
- ✅ **TestClickAction** (12 تست): تست‌های کلیک
- ✅ **TestTypeAction** (11 تست): تست‌های تایپ
- ✅ **TestWaitAction** (10 تست): تست‌های انتظار
- ✅ **TestDragDropAction** (7 تست): تست‌های Drag & Drop
- ✅ **TestHotkeyAction** (8 تست): تست‌های میانبر
- ✅ **TestScrollAction** (8 تست): تست‌های اسکرول
- ✅ **TestSerialization** (8 تست): تست‌های سریال‌سازی
- ✅ **TestIntegration** (4 تست): تست‌های یکپارچه

---

## 🎓 مثال‌های کامل

### مثال 1: ورود به سیستم

```python
from core.desktop_actions import (
    ClickAction, TypeAction, WaitAction, HotkeyAction
)

# 1. کلیک روی فیلد نام کاربری
click_username = ClickAction(target="Username")

# 2. تایپ نام کاربری
type_username = TypeAction(text="user@example.com", clear_first=True)

# 3. رفتن به فیلد بعدی با Tab
press_tab = HotkeyAction(keys=["tab"])

# 4. تایپ رمز عبور
type_password = TypeAction(text="MyPassword123", verify=False)

# 5. کلیک روی دکمه ورود
click_login = ClickAction(target="Login", verify=True)

# 6. انتظار برای باز شدن داشبورد
wait_dashboard = WaitAction(wait_type="element", target="Dashboard", timeout=10)

# اجرای توالی
actions = [
    click_username,
    type_username,
    press_tab,
    type_password,
    click_login,
    wait_dashboard
]

for action in actions:
    valid, msg = action.validate()
    if valid:
        risk = action.get_risk_level()
        print(f"▶️ {action.describe()} [خطر: {risk.name}]")
        # اجرای واقعی...
    else:
        print(f"❌ خطا: {msg}")
        break
```

### مثال 2: جستجو و اسکرول

```python
from core.desktop_actions import (
    ClickAction, TypeAction, HotkeyAction,
    ScrollAction, WaitAction
)

# 1. فوکوس روی نوار جستجو
focus_search = HotkeyAction(keys=["ctrl", "f"])

# 2. تایپ کلمه جستجو
type_query = TypeAction(text="Python programming")

# 3. فشردن Enter
press_enter = HotkeyAction(keys=["enter"])

# 4. انتظار برای نتایج
wait_results = WaitAction(wait_type="element", target="Results", timeout=5)

# 5. اسکرول برای مشاهده نتایج بیشتر
scroll_down = ScrollAction(direction="down", clicks=10, smooth=True)

# اجرا
for action in [focus_search, type_query, press_enter, wait_results, scroll_down]:
    print(action.describe())
```

### مثال 3: Drag & Drop فایل‌ها

```python
from core.desktop_actions import DragDropAction, WaitAction

# 1. انتظار برای آماده شدن فایل منیجر
wait_ready = WaitAction(wait_type="window", target="File Explorer")

# 2. کشیدن فایل به پوشه
drag_file = DragDropAction(
    source="report.pdf",
    target="Documents",
    duration=0.8,
    verify=True
)

# 3. انتظار برای کامل شدن انتقال
wait_complete = WaitAction(wait_type="change", target=(100, 100, 500, 500))

# اجرا با بررسی خطر
for action in [wait_ready, drag_file, wait_complete]:
    risk = action.get_risk_level()
    if risk.value >= 3:  # MEDIUM یا بالاتر
        confirm = input(f"⚠️ {action.describe()} [خطر: {risk.name}] - ادامه؟ (y/n): ")
        if confirm.lower() != 'y':
            break
    print(f"✅ {action.describe()}")
```

---

## 📚 منابع مرتبط

- [`MOUSE_CONTROL.md`](MOUSE_CONTROL.md) - کنترل موس
- [`KEYBOARD_CONTROL.md`](KEYBOARD_CONTROL.md) - کنترل صفحه‌کلید
- [`DESKTOP_VISION.md`](DESKTOP_VISION.md) - شناسایی بصری عناصر
- [`SMART_WAIT.md`](SMART_WAIT.md) - انتظار هوشمند
- [`ACTION_CONTROLLER.md`](ACTION_CONTROLLER.md) - کنترلر اقدامات

---

## 🔧 توسعه

### افزودن Action جدید

1. ارث‌بری از `SystemAction`
2. استفاده از `@dataclass`
3. پیاده‌سازی `get_risk_level()`, `validate()`, `describe()`
4. اضافه کردن به `create_action_from_dict()` و `serialize_action()`
5. نوشتن تست‌های جامع

**مثال**:

```python
from dataclasses import dataclass
from typing import Literal
from core.system_actions import SystemAction, RiskLevel

@dataclass
class MyNewAction(SystemAction):
    """توضیح اقدام جدید."""
    
    param1: str | None = None
    param2: int = 10
    
    def __post_init__(self):
        if self.param1 is None:
            raise ValueError("param1 الزامی است")
    
    def get_risk_level(self) -> RiskLevel:
        return RiskLevel.LOW
    
    def validate(self) -> tuple[bool, str]:
        if not self.param1:
            return False, "param1 نباید خالی باشد"
        return True, "معتبر است"
    
    def describe(self) -> str:
        return f"اقدام جدید با {self.param1}"
```

---

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: December 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
