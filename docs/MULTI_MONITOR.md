# پشتیبانی چند مانیتور (Multi-Monitor Support)

## نمای کلی

سیستم چند مانیتور امکان کار با چندین نمایشگر را فراهم می‌کند. این سیستم به صورت خودکار تمام مانیتورها را تشخیص داده و امکان کنترل دقیق موس و اقدامات در هر مانیتور را می‌دهد.

## ویژگی‌ها

### 🖥️ تشخیص خودکار

- **Auto-Detection**: تشخیص خودکار تمام مانیتورهای متصل
- **Hot-Plug Support**: پشتیبانی از اتصال/قطع در حین اجرا
- **Fallback System**: سیستم جایگزین در صورت عدم تشخیص

### 📐 مدیریت مختصات

- **Coordinate Conversion**: تبدیل مختصات بین مانیتورها
- **Relative/Absolute**: پشتیبانی از مختصات نسبی و مطلق
- **Bounds Detection**: تشخیص محدوده هر مانیتور

### 🎯 عملیات موس

- **Per-Monitor Click**: کلیک در مانیتور مشخص
- **Per-Monitor Move**: جابجایی موس بین مانیتورها
- **Current Monitor Detection**: تشخیص مانیتور فعلی موس

## نحوه استفاده

### راه‌اندازی اولیه

```python
from core import MultiMonitor

# ایجاد سیستم multi-monitor
multi_mon = MultiMonitor()

# دریافت لیست مانیتورها
monitors = multi_mon.get_monitors()

for mon in monitors:
    print(f"مانیتور {mon.index}: {mon.width}x{mon.height}")
```

### اطلاعات مانیتورها

```python
# تعداد مانیتورها
count = multi_mon.get_monitor_count()
print(f"تعداد مانیتورها: {count}")

# مانیتور اصلی
primary = multi_mon.get_primary_monitor()
print(f"مانیتور اصلی: {primary.name}")

# مانیتور خاص
monitor = multi_mon.get_monitor_by_index(1)
if monitor:
    print(f"مانیتور 1: {monitor.bounds}")
```

## MonitorInfo

### ساختار

```python
@dataclass
class MonitorInfo:
    index: int           # شماره مانیتور (0، 1، 2، ...)
    name: str           # نام مانیتور
    x: int              # موقعیت X (مطلق)
    y: int              # موقعیت Y (مطلق)
    width: int          # عرض (پیکسل)
    height: int         # ارتفاع (پیکسل)
    is_primary: bool    # آیا مانیتور اصلی است؟
    
    @property
    def center(self) -> Tuple[int, int]:
        """مرکز مانیتور."""
    
    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        """محدوده: (x, y, width, height)."""
    
    def contains_point(self, x: int, y: int) -> bool:
        """آیا نقطه در این مانیتور است؟"""
```

### مثال

```python
monitor = multi_mon.get_primary_monitor()

print(f"شماره: {monitor.index}")
print(f"نام: {monitor.name}")
print(f"موقعیت: ({monitor.x}, {monitor.y})")
print(f"اندازه: {monitor.width}x{monitor.height}")
print(f"مرکز: {monitor.center}")
print(f"محدوده: {monitor.bounds}")
print(f"اصلی: {monitor.is_primary}")

# بررسی نقطه
x, y = 1000, 500
if monitor.contains_point(x, y):
    print(f"نقطه ({x}, {y}) در این مانیتور است")
```

## عملیات مانیتور

### یافتن مانیتور

#### بر اساس شماره
```python
monitor = multi_mon.get_monitor_by_index(0)
```

#### بر اساس نقطه
```python
monitor = multi_mon.get_monitor_at_point(1000, 500)
if monitor:
    print(f"نقطه در مانیتور {monitor.index} است")
```

#### مانیتور فعلی (موس)
```python
current = multi_mon.get_current_monitor()
print(f"موس در مانیتور {current.index} است")
```

### تبدیل مختصات

```python
# تبدیل از مانیتور 0 به مانیتور 1
x, y = 100, 200  # نسبی در مانیتور 0

new_x, new_y = multi_mon.convert_to_monitor(
    x, y,
    from_monitor=0,
    to_monitor=1
)

print(f"در مانیتور 1: ({new_x}, {new_y})")
```

### عملیات موس

#### کلیک در مانیتور مشخص
```python
# کلیک در مرکز مانیتور 1
multi_mon.click_on_monitor(
    x=monitor.width // 2,
    y=monitor.height // 2,
    monitor_index=1,
    button='left'
)
```

#### جابجایی موس
```python
# انتقال موس به مانیتور 2
multi_mon.move_to_monitor(
    x=100,
    y=200,
    monitor_index=2
)
```

## Layout مانیتورها

### دریافت اندازه کل

```python
total_width, total_height = multi_mon.get_total_screen_size()
print(f"اندازه کل: {total_width}x{total_height}")
```

### دریافت Layout کامل

```python
layout = multi_mon.get_monitor_layout()

print(f"تعداد: {layout['count']}")
print(f"مانیتور اصلی: {layout['primary']}")
print(f"اندازه کل: {layout['total_size']}")

for mon_info in layout['monitors']:
    print(f"  مانیتور {mon_info['index']}: {mon_info['size']}")
```

## سناریوهای متداول

### سناریو 1: کار با دو مانیتور

```python
from core import MultiMonitor

multi_mon = MultiMonitor()

# بررسی تعداد
if multi_mon.get_monitor_count() < 2:
    print("فقط یک مانیتور متصل است")
else:
    # دریافت دو مانیتور
    mon0 = multi_mon.get_monitor_by_index(0)
    mon1 = multi_mon.get_monitor_by_index(1)
    
    # کلیک در مرکز هر مانیتور
    multi_mon.click_on_monitor(
        mon0.width // 2,
        mon0.height // 2,
        0
    )
    
    await asyncio.sleep(1)
    
    multi_mon.click_on_monitor(
        mon1.width // 2,
        mon1.height // 2,
        1
    )
```

### سناریو 2: یافتن مانیتور فعال

```python
# یافتن مانیتوری که موس در آن است
current = multi_mon.get_current_monitor()

print(f"موس در مانیتور {current.index}")
print(f"اندازه: {current.width}x{current.height}")

# انجام عملیات در همان مانیتور
multi_mon.click_on_monitor(
    x=100,
    y=100,
    monitor_index=current.index
)
```

### سناریو 3: کار با مختصات مطلق

```python
from core import MouseControl

mouse = MouseControl()

# دریافت موقعیت فعلی (مطلق)
pos = mouse.get_position()
print(f"موقعیت مطلق: {pos}")

# یافتن مانیتور
monitor = multi_mon.get_monitor_at_point(pos[0], pos[1])

if monitor:
    # تبدیل به نسبی
    rel_x = pos[0] - monitor.x
    rel_y = pos[1] - monitor.y
    print(f"موقعیت نسبی در مانیتور {monitor.index}: ({rel_x}, {rel_y})")
```

### سناریو 4: جابجایی پنجره بین مانیتورها

```python
from core import MultiMonitor, DesktopActions

multi_mon = MultiMonitor()
desktop = DesktopActions()

# یافتن پنجره فعال
window_title = "Notepad"

# انتقال به مانیتور 1
monitor = multi_mon.get_monitor_by_index(1)
if monitor:
    # موقعیت جدید در مرکز مانیتور
    new_x = monitor.x + monitor.width // 2
    new_y = monitor.y + monitor.height // 2
    
    # جابجایی پنجره
    desktop.move_window(window_title, new_x, new_y)
```

## پیکربندی چیدمان

### چیدمان افقی (Horizontal)
```
┌─────────┬─────────┐
│Monitor 0│Monitor 1│
│  (0,0)  │(1920,0) │
└─────────┴─────────┘
```

```python
# مانیتور 0: (0, 0, 1920, 1080)
# مانیتور 1: (1920, 0, 1920, 1080)

# تبدیل (100, 100) از Mon0 به Mon1
x, y = multi_mon.convert_to_monitor(100, 100, 0, 1)
# نتیجه: (2020, 100)
```

### چیدمان عمودی (Vertical)
```
┌─────────┐
│Monitor 0│
│  (0,0)  │
├─────────┤
│Monitor 1│
│ (0,1080)│
└─────────┘
```

```python
# مانیتور 0: (0, 0, 1920, 1080)
# مانیتور 1: (0, 1080, 1920, 1080)

# تبدیل (100, 100) از Mon0 به Mon1
x, y = multi_mon.convert_to_monitor(100, 100, 0, 1)
# نتیجه: (100, 1180)
```

### چیدمان ترکیبی (Mixed)
```
┌─────────┬─────────┐
│Monitor 1│Monitor 2│
│ (0,-1080)│(1920,-1080)│
├─────────┴─────────┤
│    Monitor 0      │
│      (0,0)        │
└───────────────────┘
```

## تشخیص تغییرات

### اتصال مانیتور جدید

```python
# دریافت تعداد فعلی
count_before = multi_mon.get_monitor_count()

# صبر برای اتصال

# بروزرسانی (re-detection)
multi_mon = MultiMonitor()
count_after = multi_mon.get_monitor_count()

if count_after > count_before:
    print(f"{count_after - count_before} مانیتور جدید اضافه شد")
```

### تشخیص قطع اتصال

```python
# بررسی دوره‌ای
import asyncio

async def monitor_changes():
    previous_count = multi_mon.get_monitor_count()
    
    while True:
        await asyncio.sleep(5)  # هر 5 ثانیه
        
        current_count = multi_mon.get_monitor_count()
        
        if current_count != previous_count:
            print(f"تغییر: {previous_count} → {current_count}")
            previous_count = current_count
```

## API Reference

### MultiMonitor

#### `__init__()`
ایجاد سیستم multi-monitor و تشخیص خودکار مانیتورها.

#### `get_monitors() -> List[MonitorInfo]`
دریافت لیست تمام مانیتورها.

#### `get_monitor_count() -> int`
دریافت تعداد مانیتورها.

#### `get_primary_monitor() -> MonitorInfo`
دریافت مانیتور اصلی.

#### `get_monitor_by_index(index: int) -> Optional[MonitorInfo]`
دریافت مانیتور با شماره مشخص.

#### `get_monitor_at_point(x: int, y: int) -> Optional[MonitorInfo]`
یافتن مانیتوری که نقطه در آن قرار دارد.

#### `get_current_monitor() -> Optional[MonitorInfo]`
یافتن مانیتوری که موس در آن است.

#### `convert_to_monitor(x: int, y: int, from_monitor: int, to_monitor: int) -> Tuple[int, int]`
تبدیل مختصات از یک مانیتور به مانیتور دیگر.

#### `click_on_monitor(x: int, y: int, monitor_index: int, button: str = 'left')`
کلیک در موقعیت مشخص در مانیتور خاص.

#### `move_to_monitor(x: int, y: int, monitor_index: int)`
جابجایی موس به موقعیت در مانیتور خاص.

#### `get_total_screen_size() -> Tuple[int, int]`
دریافت اندازه کل فضای صفحه.

#### `get_monitor_layout() -> Dict[str, Any]`
دریافت اطلاعات کامل layout.

## عیب‌یابی

### مشکل: فقط یک مانیتور تشخیص می‌دهد

**علت:** مانیتور دوم غیرفعال است یا screeninfo آن را نمی‌بیند

**راه‌حل:**
1. تنظیمات Windows → Display → تشخیص مانیتورها
2. بررسی اتصال کابل
3. نصب مجدد driver کارت گرافیک

### مشکل: مختصات اشتباه است

**علت:** تفاوت بین مختصات نسبی و مطلق

**راه‌حل:**
```python
# استفاده از convert_to_monitor
new_x, new_y = multi_mon.convert_to_monitor(x, y, from_mon, to_mon)
```

### مشکل: کلیک در جای اشتباه

**علت:** فراموش کردن offset مانیتور

**راه‌حل:**
```python
# استفاده از click_on_monitor به جای mouse.click
multi_mon.click_on_monitor(x, y, monitor_index)
```

## بهترین شیوه‌ها

1. **همیشه از click_on_monitor استفاده کنید** برای کلیک چند مانیتوری
2. **مختصات را تبدیل کنید** قبل از استفاده در مانیتور دیگر
3. **مانیتور فعلی را بررسی کنید** قبل از عملیات
4. **تعداد مانیتورها را validate کنید** - ممکن است تغییر کند
5. **از bounds استفاده کنید** برای بررسی محدوده

---

**نسخه:** 1.0  
**آخرین بروزرسانی:** 2025-12-01
