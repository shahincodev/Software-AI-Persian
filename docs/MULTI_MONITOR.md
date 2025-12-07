# Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ Ú†Ù†Ø¯ Ù…Ø§Ù†ÛŒØªÙˆØ± (Multi-Monitor Support)

## Ù†Ù…Ø§ÛŒ Ú©Ù„ÛŒ

Ø³ÛŒØ³ØªÙ… Ú†Ù†Ø¯ Ù…Ø§Ù†ÛŒØªÙˆØ± Ø§Ù…Ú©Ø§Ù† Ú©Ø§Ø± Ø¨Ø§ Ú†Ù†Ø¯ÛŒÙ† Ù†Ù…Ø§ÛŒØ´Ú¯Ø± Ø±Ø§ ÙØ±Ø§Ù‡Ù… Ù…ÛŒâ€ŒÚ©Ù†Ø¯. Ø§ÛŒÙ† Ø³ÛŒØ³ØªÙ… Ø¨Ù‡ ØµÙˆØ±Øª Ø®ÙˆØ¯Ú©Ø§Ø± ØªÙ…Ø§Ù… Ù…Ø§Ù†ÛŒØªÙˆØ±Ù‡Ø§ Ø±Ø§ ØªØ´Ø®ÛŒØµ Ø¯Ø§Ø¯Ù‡ Ùˆ Ø§Ù…Ú©Ø§Ù† Ú©Ù†ØªØ±Ù„ Ø¯Ù‚ÛŒÙ‚ Ù…ÙˆØ³ Ùˆ Ø§Ù‚Ø¯Ø§Ù…Ø§Øª Ø¯Ø± Ù‡Ø± Ù…Ø§Ù†ÛŒØªÙˆØ± Ø±Ø§ Ù…ÛŒâ€ŒØ¯Ù‡Ø¯.

## ÙˆÛŒÚ˜Ú¯ÛŒâ€ŒÙ‡Ø§

### ðŸ–¥ï¸ ØªØ´Ø®ÛŒØµ Ø®ÙˆØ¯Ú©Ø§Ø±

- **Auto-Detection**: ØªØ´Ø®ÛŒØµ Ø®ÙˆØ¯Ú©Ø§Ø± ØªÙ…Ø§Ù… Ù…Ø§Ù†ÛŒØªÙˆØ±Ù‡Ø§ÛŒ Ù…ØªØµÙ„
- **Hot-Plug Support**: Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ Ø§Ø² Ø§ØªØµØ§Ù„/Ù‚Ø·Ø¹ Ø¯Ø± Ø­ÛŒÙ† Ø§Ø¬Ø±Ø§
- **Fallback System**: Ø³ÛŒØ³ØªÙ… Ø¬Ø§ÛŒÚ¯Ø²ÛŒÙ† Ø¯Ø± ØµÙˆØ±Øª Ø¹Ø¯Ù… ØªØ´Ø®ÛŒØµ

### ðŸ“ Ù…Ø¯ÛŒØ±ÛŒØª Ù…Ø®ØªØµØ§Øª

- **Coordinate Conversion**: ØªØ¨Ø¯ÛŒÙ„ Ù…Ø®ØªØµØ§Øª Ø¨ÛŒÙ† Ù…Ø§Ù†ÛŒØªÙˆØ±Ù‡Ø§
- **Relative/Absolute**: Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ Ø§Ø² Ù…Ø®ØªØµØ§Øª Ù†Ø³Ø¨ÛŒ Ùˆ Ù…Ø·Ù„Ù‚
- **Bounds Detection**: ØªØ´Ø®ÛŒØµ Ù…Ø­Ø¯ÙˆØ¯Ù‡ Ù‡Ø± Ù…Ø§Ù†ÛŒØªÙˆØ±

### ðŸŽ¯ Ø¹Ù…Ù„ÛŒØ§Øª Ù…ÙˆØ³

- **Per-Monitor Click**: Ú©Ù„ÛŒÚ© Ø¯Ø± Ù…Ø§Ù†ÛŒØªÙˆØ± Ù…Ø´Ø®Øµ
- **Per-Monitor Move**: Ø¬Ø§Ø¨Ø¬Ø§ÛŒÛŒ Ù…ÙˆØ³ Ø¨ÛŒÙ† Ù…Ø§Ù†ÛŒØªÙˆØ±Ù‡Ø§
- **Current Monitor Detection**: ØªØ´Ø®ÛŒØµ Ù…Ø§Ù†ÛŒØªÙˆØ± ÙØ¹Ù„ÛŒ Ù…ÙˆØ³

## Ù†Ø­ÙˆÙ‡ Ø§Ø³ØªÙØ§Ø¯Ù‡

### Ø±Ø§Ù‡â€ŒØ§Ù†Ø¯Ø§Ø²ÛŒ Ø§ÙˆÙ„ÛŒÙ‡

```python
from core import MultiMonitor

# Ø§ÛŒØ¬Ø§Ø¯ Ø³ÛŒØ³ØªÙ… multi-monitor
multi_mon = MultiMonitor()

# Ø¯Ø±ÛŒØ§ÙØª Ù„ÛŒØ³Øª Ù…Ø§Ù†ÛŒØªÙˆØ±Ù‡Ø§
monitors = multi_mon.get_monitors()

for mon in monitors:
    print(f"Ù…Ø§Ù†ÛŒØªÙˆØ± {mon.index}: {mon.width}x{mon.height}")
```

### Ø§Ø·Ù„Ø§Ø¹Ø§Øª Ù…Ø§Ù†ÛŒØªÙˆØ±Ù‡Ø§

```python
# ØªØ¹Ø¯Ø§Ø¯ Ù…Ø§Ù†ÛŒØªÙˆØ±Ù‡Ø§
count = multi_mon.get_monitor_count()
print(f"ØªØ¹Ø¯Ø§Ø¯ Ù…Ø§Ù†ÛŒØªÙˆØ±Ù‡Ø§: {count}")

# Ù…Ø§Ù†ÛŒØªÙˆØ± Ø§ØµÙ„ÛŒ
primary = multi_mon.get_primary_monitor()
print(f"Ù…Ø§Ù†ÛŒØªÙˆØ± Ø§ØµÙ„ÛŒ: {primary.name}")

# Ù…Ø§Ù†ÛŒØªÙˆØ± Ø®Ø§Øµ
monitor = multi_mon.get_monitor_by_index(1)
if monitor:
    print(f"Ù…Ø§Ù†ÛŒØªÙˆØ± 1: {monitor.bounds}")
```

## MonitorInfo

### Ø³Ø§Ø®ØªØ§Ø±

```python
@dataclass
class MonitorInfo:
    index: int           # Ø´Ù…Ø§Ø±Ù‡ Ù…Ø§Ù†ÛŒØªÙˆØ± (0ØŒ 1ØŒ 2ØŒ ...)
    name: str           # Ù†Ø§Ù… Ù…Ø§Ù†ÛŒØªÙˆØ±
    x: int              # Ù…ÙˆÙ‚Ø¹ÛŒØª X (Ù…Ø·Ù„Ù‚)
    y: int              # Ù…ÙˆÙ‚Ø¹ÛŒØª Y (Ù…Ø·Ù„Ù‚)
    width: int          # Ø¹Ø±Ø¶ (Ù¾ÛŒÚ©Ø³Ù„)
    height: int         # Ø§Ø±ØªÙØ§Ø¹ (Ù¾ÛŒÚ©Ø³Ù„)
    is_primary: bool    # Ø¢ÛŒØ§ Ù…Ø§Ù†ÛŒØªÙˆØ± Ø§ØµÙ„ÛŒ Ø§Ø³ØªØŸ
    
    @property
    def center(self) -> Tuple[int, int]:
        """Ù…Ø±Ú©Ø² Ù…Ø§Ù†ÛŒØªÙˆØ±."""
    
    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        """Ù…Ø­Ø¯ÙˆØ¯Ù‡: (x, y, width, height)."""
    
    def contains_point(self, x: int, y: int) -> bool:
        """Ø¢ÛŒØ§ Ù†Ù‚Ø·Ù‡ Ø¯Ø± Ø§ÛŒÙ† Ù…Ø§Ù†ÛŒØªÙˆØ± Ø§Ø³ØªØŸ"""
```

### Ù…Ø«Ø§Ù„

```python
monitor = multi_mon.get_primary_monitor()

print(f"Ø´Ù…Ø§Ø±Ù‡: {monitor.index}")
print(f"Ù†Ø§Ù…: {monitor.name}")
print(f"Ù…ÙˆÙ‚Ø¹ÛŒØª: ({monitor.x}, {monitor.y})")
print(f"Ø§Ù†Ø¯Ø§Ø²Ù‡: {monitor.width}x{monitor.height}")
print(f"Ù…Ø±Ú©Ø²: {monitor.center}")
print(f"Ù…Ø­Ø¯ÙˆØ¯Ù‡: {monitor.bounds}")
print(f"Ø§ØµÙ„ÛŒ: {monitor.is_primary}")

# Ø¨Ø±Ø±Ø³ÛŒ Ù†Ù‚Ø·Ù‡
x, y = 1000, 500
if monitor.contains_point(x, y):
    print(f"Ù†Ù‚Ø·Ù‡ ({x}, {y}) Ø¯Ø± Ø§ÛŒÙ† Ù…Ø§Ù†ÛŒØªÙˆØ± Ø§Ø³Øª")
```

## Ø¹Ù…Ù„ÛŒØ§Øª Ù…Ø§Ù†ÛŒØªÙˆØ±

### ÛŒØ§ÙØªÙ† Ù…Ø§Ù†ÛŒØªÙˆØ±

#### Ø¨Ø± Ø§Ø³Ø§Ø³ Ø´Ù…Ø§Ø±Ù‡
```python
monitor = multi_mon.get_monitor_by_index(0)
```

#### Ø¨Ø± Ø§Ø³Ø§Ø³ Ù†Ù‚Ø·Ù‡
```python
monitor = multi_mon.get_monitor_at_point(1000, 500)
if monitor:
    print(f"Ù†Ù‚Ø·Ù‡ Ø¯Ø± Ù…Ø§Ù†ÛŒØªÙˆØ± {monitor.index} Ø§Ø³Øª")
```

#### Ù…Ø§Ù†ÛŒØªÙˆØ± ÙØ¹Ù„ÛŒ (Ù…ÙˆØ³)
```python
current = multi_mon.get_current_monitor()
print(f"Ù…ÙˆØ³ Ø¯Ø± Ù…Ø§Ù†ÛŒØªÙˆØ± {current.index} Ø§Ø³Øª")
```

### ØªØ¨Ø¯ÛŒÙ„ Ù…Ø®ØªØµØ§Øª

```python
# ØªØ¨Ø¯ÛŒÙ„ Ø§Ø² Ù…Ø§Ù†ÛŒØªÙˆØ± 0 Ø¨Ù‡ Ù…Ø§Ù†ÛŒØªÙˆØ± 1
x, y = 100, 200  # Ù†Ø³Ø¨ÛŒ Ø¯Ø± Ù…Ø§Ù†ÛŒØªÙˆØ± 0

new_x, new_y = multi_mon.convert_to_monitor(
    x, y,
    from_monitor=0,
    to_monitor=1
)

print(f"Ø¯Ø± Ù…Ø§Ù†ÛŒØªÙˆØ± 1: ({new_x}, {new_y})")
```

### Ø¹Ù…Ù„ÛŒØ§Øª Ù…ÙˆØ³

#### Ú©Ù„ÛŒÚ© Ø¯Ø± Ù…Ø§Ù†ÛŒØªÙˆØ± Ù…Ø´Ø®Øµ
```python
# Ú©Ù„ÛŒÚ© Ø¯Ø± Ù…Ø±Ú©Ø² Ù…Ø§Ù†ÛŒØªÙˆØ± 1
multi_mon.click_on_monitor(
    x=monitor.width // 2,
    y=monitor.height // 2,
    monitor_index=1,
    button='left'
)
```

#### Ø¬Ø§Ø¨Ø¬Ø§ÛŒÛŒ Ù…ÙˆØ³
```python
# Ø§Ù†ØªÙ‚Ø§Ù„ Ù…ÙˆØ³ Ø¨Ù‡ Ù…Ø§Ù†ÛŒØªÙˆØ± 2
multi_mon.move_to_monitor(
    x=100,
    y=200,
    monitor_index=2
)
```

## Layout Ù…Ø§Ù†ÛŒØªÙˆØ±Ù‡Ø§

### Ø¯Ø±ÛŒØ§ÙØª Ø§Ù†Ø¯Ø§Ø²Ù‡ Ú©Ù„

```python
total_width, total_height = multi_mon.get_total_screen_size()
print(f"Ø§Ù†Ø¯Ø§Ø²Ù‡ Ú©Ù„: {total_width}x{total_height}")
```

### Ø¯Ø±ÛŒØ§ÙØª Layout Ú©Ø§Ù…Ù„

```python
layout = multi_mon.get_monitor_layout()

print(f"ØªØ¹Ø¯Ø§Ø¯: {layout['count']}")
print(f"Ù…Ø§Ù†ÛŒØªÙˆØ± Ø§ØµÙ„ÛŒ: {layout['primary']}")
print(f"Ø§Ù†Ø¯Ø§Ø²Ù‡ Ú©Ù„: {layout['total_size']}")

for mon_info in layout['monitors']:
    print(f"  Ù…Ø§Ù†ÛŒØªÙˆØ± {mon_info['index']}: {mon_info['size']}")
```

## Ø³Ù†Ø§Ø±ÛŒÙˆÙ‡Ø§ÛŒ Ù…ØªØ¯Ø§ÙˆÙ„

### Ø³Ù†Ø§Ø±ÛŒÙˆ 1: Ú©Ø§Ø± Ø¨Ø§ Ø¯Ùˆ Ù…Ø§Ù†ÛŒØªÙˆØ±

```python
from core import MultiMonitor

multi_mon = MultiMonitor()

# Ø¨Ø±Ø±Ø³ÛŒ ØªØ¹Ø¯Ø§Ø¯
if multi_mon.get_monitor_count() < 2:
    print("ÙÙ‚Ø· ÛŒÚ© Ù…Ø§Ù†ÛŒØªÙˆØ± Ù…ØªØµÙ„ Ø§Ø³Øª")
else:
    # Ø¯Ø±ÛŒØ§ÙØª Ø¯Ùˆ Ù…Ø§Ù†ÛŒØªÙˆØ±
    mon0 = multi_mon.get_monitor_by_index(0)
    mon1 = multi_mon.get_monitor_by_index(1)
    
    # Ú©Ù„ÛŒÚ© Ø¯Ø± Ù…Ø±Ú©Ø² Ù‡Ø± Ù…Ø§Ù†ÛŒØªÙˆØ±
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

### Ø³Ù†Ø§Ø±ÛŒÙˆ 2: ÛŒØ§ÙØªÙ† Ù…Ø§Ù†ÛŒØªÙˆØ± ÙØ¹Ø§Ù„

```python
# ÛŒØ§ÙØªÙ† Ù…Ø§Ù†ÛŒØªÙˆØ±ÛŒ Ú©Ù‡ Ù…ÙˆØ³ Ø¯Ø± Ø¢Ù† Ø§Ø³Øª
current = multi_mon.get_current_monitor()

print(f"Ù…ÙˆØ³ Ø¯Ø± Ù…Ø§Ù†ÛŒØªÙˆØ± {current.index}")
print(f"Ø§Ù†Ø¯Ø§Ø²Ù‡: {current.width}x{current.height}")

# Ø§Ù†Ø¬Ø§Ù… Ø¹Ù…Ù„ÛŒØ§Øª Ø¯Ø± Ù‡Ù…Ø§Ù† Ù…Ø§Ù†ÛŒØªÙˆØ±
multi_mon.click_on_monitor(
    x=100,
    y=100,
    monitor_index=current.index
)
```

### Ø³Ù†Ø§Ø±ÛŒÙˆ 3: Ú©Ø§Ø± Ø¨Ø§ Ù…Ø®ØªØµØ§Øª Ù…Ø·Ù„Ù‚

```python
from core import MouseControl

mouse = MouseControl()

# Ø¯Ø±ÛŒØ§ÙØª Ù…ÙˆÙ‚Ø¹ÛŒØª ÙØ¹Ù„ÛŒ (Ù…Ø·Ù„Ù‚)
pos = mouse.get_position()
print(f"Ù…ÙˆÙ‚Ø¹ÛŒØª Ù…Ø·Ù„Ù‚: {pos}")

# ÛŒØ§ÙØªÙ† Ù…Ø§Ù†ÛŒØªÙˆØ±
monitor = multi_mon.get_monitor_at_point(pos[0], pos[1])

if monitor:
    # ØªØ¨Ø¯ÛŒÙ„ Ø¨Ù‡ Ù†Ø³Ø¨ÛŒ
    rel_x = pos[0] - monitor.x
    rel_y = pos[1] - monitor.y
    print(f"Ù…ÙˆÙ‚Ø¹ÛŒØª Ù†Ø³Ø¨ÛŒ Ø¯Ø± Ù…Ø§Ù†ÛŒØªÙˆØ± {monitor.index}: ({rel_x}, {rel_y})")
```

### Ø³Ù†Ø§Ø±ÛŒÙˆ 4: Ø¬Ø§Ø¨Ø¬Ø§ÛŒÛŒ Ù¾Ù†Ø¬Ø±Ù‡ Ø¨ÛŒÙ† Ù…Ø§Ù†ÛŒØªÙˆØ±Ù‡Ø§

```python
from core import MultiMonitor, DesktopActions

multi_mon = MultiMonitor()
desktop = DesktopActions()

# ÛŒØ§ÙØªÙ† Ù¾Ù†Ø¬Ø±Ù‡ ÙØ¹Ø§Ù„
window_title = "Notepad"

# Ø§Ù†ØªÙ‚Ø§Ù„ Ø¨Ù‡ Ù…Ø§Ù†ÛŒØªÙˆØ± 1
monitor = multi_mon.get_monitor_by_index(1)
if monitor:
    # Ù…ÙˆÙ‚Ø¹ÛŒØª Ø¬Ø¯ÛŒØ¯ Ø¯Ø± Ù…Ø±Ú©Ø² Ù…Ø§Ù†ÛŒØªÙˆØ±
    new_x = monitor.x + monitor.width // 2
    new_y = monitor.y + monitor.height // 2
    
    # Ø¬Ø§Ø¨Ø¬Ø§ÛŒÛŒ Ù¾Ù†Ø¬Ø±Ù‡
    desktop.move_window(window_title, new_x, new_y)
```

## Ù¾ÛŒÚ©Ø±Ø¨Ù†Ø¯ÛŒ Ú†ÛŒØ¯Ù…Ø§Ù†

### Ú†ÛŒØ¯Ù…Ø§Ù† Ø§ÙÙ‚ÛŒ (Horizontal)
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚Monitor 0â”‚Monitor 1â”‚
â”‚  (0,0)  â”‚(1920,0) â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

```python
# Ù…Ø§Ù†ÛŒØªÙˆØ± 0: (0, 0, 1920, 1080)
# Ù…Ø§Ù†ÛŒØªÙˆØ± 1: (1920, 0, 1920, 1080)

# ØªØ¨Ø¯ÛŒÙ„ (100, 100) Ø§Ø² Mon0 Ø¨Ù‡ Mon1
x, y = multi_mon.convert_to_monitor(100, 100, 0, 1)
# Ù†ØªÛŒØ¬Ù‡: (2020, 100)
```

### Ú†ÛŒØ¯Ù…Ø§Ù† Ø¹Ù…ÙˆØ¯ÛŒ (Vertical)
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚Monitor 0â”‚
â”‚  (0,0)  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚Monitor 1â”‚
â”‚ (0,1080)â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

```python
# Ù…Ø§Ù†ÛŒØªÙˆØ± 0: (0, 0, 1920, 1080)
# Ù…Ø§Ù†ÛŒØªÙˆØ± 1: (0, 1080, 1920, 1080)

# ØªØ¨Ø¯ÛŒÙ„ (100, 100) Ø§Ø² Mon0 Ø¨Ù‡ Mon1
x, y = multi_mon.convert_to_monitor(100, 100, 0, 1)
# Ù†ØªÛŒØ¬Ù‡: (100, 1180)
```

### Ú†ÛŒØ¯Ù…Ø§Ù† ØªØ±Ú©ÛŒØ¨ÛŒ (Mixed)
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚Monitor 1â”‚Monitor 2â”‚
â”‚ (0,-1080)â”‚(1920,-1080)â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚    Monitor 0      â”‚
â”‚      (0,0)        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## ØªØ´Ø®ÛŒØµ ØªØºÛŒÛŒØ±Ø§Øª

### Ø§ØªØµØ§Ù„ Ù…Ø§Ù†ÛŒØªÙˆØ± Ø¬Ø¯ÛŒØ¯

```python
# Ø¯Ø±ÛŒØ§ÙØª ØªØ¹Ø¯Ø§Ø¯ ÙØ¹Ù„ÛŒ
count_before = multi_mon.get_monitor_count()

# ØµØ¨Ø± Ø¨Ø±Ø§ÛŒ Ø§ØªØµØ§Ù„

# Ø¨Ø±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ (re-detection)
multi_mon = MultiMonitor()
count_after = multi_mon.get_monitor_count()

if count_after > count_before:
    print(f"{count_after - count_before} Ù…Ø§Ù†ÛŒØªÙˆØ± Ø¬Ø¯ÛŒØ¯ Ø§Ø¶Ø§ÙÙ‡ Ø´Ø¯")
```

### ØªØ´Ø®ÛŒØµ Ù‚Ø·Ø¹ Ø§ØªØµØ§Ù„

```python
# Ø¨Ø±Ø±Ø³ÛŒ Ø¯ÙˆØ±Ù‡â€ŒØ§ÛŒ
import asyncio

async def monitor_changes():
    previous_count = multi_mon.get_monitor_count()
    
    while True:
        await asyncio.sleep(5)  # Ù‡Ø± 5 Ø«Ø§Ù†ÛŒÙ‡
        
        current_count = multi_mon.get_monitor_count()
        
        if current_count != previous_count:
            print(f"ØªØºÛŒÛŒØ±: {previous_count} â†’ {current_count}")
            previous_count = current_count
```

## API Reference

### MultiMonitor

#### `__init__()`
Ø§ÛŒØ¬Ø§Ø¯ Ø³ÛŒØ³ØªÙ… multi-monitor Ùˆ ØªØ´Ø®ÛŒØµ Ø®ÙˆØ¯Ú©Ø§Ø± Ù…Ø§Ù†ÛŒØªÙˆØ±Ù‡Ø§.

#### `get_monitors() -> List[MonitorInfo]`
Ø¯Ø±ÛŒØ§ÙØª Ù„ÛŒØ³Øª ØªÙ…Ø§Ù… Ù…Ø§Ù†ÛŒØªÙˆØ±Ù‡Ø§.

#### `get_monitor_count() -> int`
Ø¯Ø±ÛŒØ§ÙØª ØªØ¹Ø¯Ø§Ø¯ Ù…Ø§Ù†ÛŒØªÙˆØ±Ù‡Ø§.

#### `get_primary_monitor() -> MonitorInfo`
Ø¯Ø±ÛŒØ§ÙØª Ù…Ø§Ù†ÛŒØªÙˆØ± Ø§ØµÙ„ÛŒ.

#### `get_monitor_by_index(index: int) -> Optional[MonitorInfo]`
Ø¯Ø±ÛŒØ§ÙØª Ù…Ø§Ù†ÛŒØªÙˆØ± Ø¨Ø§ Ø´Ù…Ø§Ø±Ù‡ Ù…Ø´Ø®Øµ.

#### `get_monitor_at_point(x: int, y: int) -> Optional[MonitorInfo]`
ÛŒØ§ÙØªÙ† Ù…Ø§Ù†ÛŒØªÙˆØ±ÛŒ Ú©Ù‡ Ù†Ù‚Ø·Ù‡ Ø¯Ø± Ø¢Ù† Ù‚Ø±Ø§Ø± Ø¯Ø§Ø±Ø¯.

#### `get_current_monitor() -> Optional[MonitorInfo]`
ÛŒØ§ÙØªÙ† Ù…Ø§Ù†ÛŒØªÙˆØ±ÛŒ Ú©Ù‡ Ù…ÙˆØ³ Ø¯Ø± Ø¢Ù† Ø§Ø³Øª.

#### `convert_to_monitor(x: int, y: int, from_monitor: int, to_monitor: int) -> Tuple[int, int]`
ØªØ¨Ø¯ÛŒÙ„ Ù…Ø®ØªØµØ§Øª Ø§Ø² ÛŒÚ© Ù…Ø§Ù†ÛŒØªÙˆØ± Ø¨Ù‡ Ù…Ø§Ù†ÛŒØªÙˆØ± Ø¯ÛŒÚ¯Ø±.

#### `click_on_monitor(x: int, y: int, monitor_index: int, button: str = 'left')`
Ú©Ù„ÛŒÚ© Ø¯Ø± Ù…ÙˆÙ‚Ø¹ÛŒØª Ù…Ø´Ø®Øµ Ø¯Ø± Ù…Ø§Ù†ÛŒØªÙˆØ± Ø®Ø§Øµ.

#### `move_to_monitor(x: int, y: int, monitor_index: int)`
Ø¬Ø§Ø¨Ø¬Ø§ÛŒÛŒ Ù…ÙˆØ³ Ø¨Ù‡ Ù…ÙˆÙ‚Ø¹ÛŒØª Ø¯Ø± Ù…Ø§Ù†ÛŒØªÙˆØ± Ø®Ø§Øµ.

#### `get_total_screen_size() -> Tuple[int, int]`
Ø¯Ø±ÛŒØ§ÙØª Ø§Ù†Ø¯Ø§Ø²Ù‡ Ú©Ù„ ÙØ¶Ø§ÛŒ ØµÙØ­Ù‡.

#### `get_monitor_layout() -> Dict[str, Any]`
Ø¯Ø±ÛŒØ§ÙØª Ø§Ø·Ù„Ø§Ø¹Ø§Øª Ú©Ø§Ù…Ù„ layout.

## Ø¹ÛŒØ¨â€ŒÛŒØ§Ø¨ÛŒ

### Ù…Ø´Ú©Ù„: ÙÙ‚Ø· ÛŒÚ© Ù…Ø§Ù†ÛŒØªÙˆØ± ØªØ´Ø®ÛŒØµ Ù…ÛŒâ€ŒØ¯Ù‡Ø¯

**Ø¹Ù„Øª:** Ù…Ø§Ù†ÛŒØªÙˆØ± Ø¯ÙˆÙ… ØºÛŒØ±ÙØ¹Ø§Ù„ Ø§Ø³Øª ÛŒØ§ screeninfo Ø¢Ù† Ø±Ø§ Ù†Ù…ÛŒâ€ŒØ¨ÛŒÙ†Ø¯

**Ø±Ø§Ù‡â€ŒØ­Ù„:**
1. ØªÙ†Ø¸ÛŒÙ…Ø§Øª Windows â†’ Display â†’ ØªØ´Ø®ÛŒØµ Ù…Ø§Ù†ÛŒØªÙˆØ±Ù‡Ø§
2. Ø¨Ø±Ø±Ø³ÛŒ Ø§ØªØµØ§Ù„ Ú©Ø§Ø¨Ù„
3. Ù†ØµØ¨ Ù…Ø¬Ø¯Ø¯ driver Ú©Ø§Ø±Øª Ú¯Ø±Ø§ÙÛŒÚ©

### Ù…Ø´Ú©Ù„: Ù…Ø®ØªØµØ§Øª Ø§Ø´ØªØ¨Ø§Ù‡ Ø§Ø³Øª

**Ø¹Ù„Øª:** ØªÙØ§ÙˆØª Ø¨ÛŒÙ† Ù…Ø®ØªØµØ§Øª Ù†Ø³Ø¨ÛŒ Ùˆ Ù…Ø·Ù„Ù‚

**Ø±Ø§Ù‡â€ŒØ­Ù„:**
```python
# Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² convert_to_monitor
new_x, new_y = multi_mon.convert_to_monitor(x, y, from_mon, to_mon)
```

### Ù…Ø´Ú©Ù„: Ú©Ù„ÛŒÚ© Ø¯Ø± Ø¬Ø§ÛŒ Ø§Ø´ØªØ¨Ø§Ù‡

**Ø¹Ù„Øª:** ÙØ±Ø§Ù…ÙˆØ´ Ú©Ø±Ø¯Ù† offset Ù…Ø§Ù†ÛŒØªÙˆØ±

**Ø±Ø§Ù‡â€ŒØ­Ù„:**
```python
# Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² click_on_monitor Ø¨Ù‡ Ø¬Ø§ÛŒ mouse.click
multi_mon.click_on_monitor(x, y, monitor_index)
```

## Ø¨Ù‡ØªØ±ÛŒÙ† Ø´ÛŒÙˆÙ‡â€ŒÙ‡Ø§

1. **Ù‡Ù…ÛŒØ´Ù‡ Ø§Ø² click_on_monitor Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯** Ø¨Ø±Ø§ÛŒ Ú©Ù„ÛŒÚ© Ú†Ù†Ø¯ Ù…Ø§Ù†ÛŒØªÙˆØ±ÛŒ
2. **Ù…Ø®ØªØµØ§Øª Ø±Ø§ ØªØ¨Ø¯ÛŒÙ„ Ú©Ù†ÛŒØ¯** Ù‚Ø¨Ù„ Ø§Ø² Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø¯Ø± Ù…Ø§Ù†ÛŒØªÙˆØ± Ø¯ÛŒÚ¯Ø±
3. **Ù…Ø§Ù†ÛŒØªÙˆØ± ÙØ¹Ù„ÛŒ Ø±Ø§ Ø¨Ø±Ø±Ø³ÛŒ Ú©Ù†ÛŒØ¯** Ù‚Ø¨Ù„ Ø§Ø² Ø¹Ù…Ù„ÛŒØ§Øª
4. **ØªØ¹Ø¯Ø§Ø¯ Ù…Ø§Ù†ÛŒØªÙˆØ±Ù‡Ø§ Ø±Ø§ validate Ú©Ù†ÛŒØ¯** - Ù…Ù…Ú©Ù† Ø§Ø³Øª ØªØºÛŒÛŒØ± Ú©Ù†Ø¯
5. **Ø§Ø² bounds Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯** Ø¨Ø±Ø§ÛŒ Ø¨Ø±Ø±Ø³ÛŒ Ù…Ø­Ø¯ÙˆØ¯Ù‡

---

**Ù†Ø³Ø®Ù‡:** 1.0  
**Ø¢Ø®Ø±ÛŒÙ† Ø¨Ø±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ:** 2025-12-01

---

**توسعهدهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: November 2025  
**وضعیت**: Production Ready 

---

##  مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
