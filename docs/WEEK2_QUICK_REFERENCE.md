# ⚡ Week 2 - Quick Reference
## Action Layer Development Guide

> **مرجع سریع** برای توسعه‌دهندگان - دسترسی آسان به اطلاعات کلیدی

---

## 📁 ساختار فایل‌ها (File Structure)

```
Software-AI/
│
├── core/                           # ماژول‌های اصلی (Core modules)
│   ├── mouse_control.py           # 🆕 اتوماسیون ماوس (Mouse automation)
│   ├── keyboard_control.py        # 🆕 اتوماسیون کیبورد (Keyboard automation)
│   ├── smart_wait.py              # 🆕 انتظار هوشمند (Intelligent waiting)
│   ├── action_controller.py       # 🆕 کنترل‌کننده عملیات (Action orchestrator)
│   ├── desktop_actions.py         # 🆕 طرح‌واره عملیات (Action schemas)
│   ├── action_safety.py           # 🆕 فیلترهای امنیتی (Safety filters)
│   ├── action_recovery.py         # 🆕 بازیابی خطا (Error recovery)
│   ├── desktop_vision.py          # ✏️ بهبودیافته (Enhanced)
│   ├── intelligent_agent.py       # ✏️ بهبودیافته (Enhanced)
│   └── ...                        # ماژول‌های موجود (Existing)
│
├── tests/                          # فایل‌های تست (Test files)
│   ├── test_mouse_control.py      # 🆕 تست‌های ماوس
│   ├── test_keyboard_control.py   # 🆕 تست‌های کیبورد
│   ├── test_smart_wait.py         # 🆕 تست‌های انتظار
│   ├── test_action_controller.py  # 🆕 تست‌های کنترلر
│   ├── test_desktop_actions.py    # 🆕 تست‌های عملیات
│   ├── integration/               # 🆕 تست‌های یکپارچه‌سازی
│   │   ├── test_complete_workflow.py
│   │   ├── test_error_scenarios.py
│   │   └── test_performance.py
│   └── ...
│
├── docs/                           # مستندات (Documentation)
│   ├── WEEK2_ACTION_LAYER_PLAN.md       # 🆕 برنامه اصلی
│   ├── WEEK2_EXECUTIVE_SUMMARY.md       # 🆕 خلاصه اجرایی
│   ├── WEEK2_QUICK_REFERENCE.md         # 🆕 این فایل
│   ├── MOUSE_CONTROL.md                   # 🆕 API ماوس
│   ├── KEYBOARD_CONTROL.md                # 🆕 API کیبورد
│   ├── SMART_WAIT.md                      # 🆕 API انتظار
│   ├── ACTION_CONTROLLER.md               # 🆕 API کنترلر
│   ├── DESKTOP_ACTIONS.md                 # 🆕 طرح‌واره عملیات
│   ├── EXAMPLES.md                        # 🆕 مثال‌های کاربردی
│   ├── TROUBLESHOOTING.md                 # 🆕 رفع مشکلات
│   ├── API_REFERENCE.md                   # 🆕 مرجع کامل API
│   └── ...                                # مستندات موجود
│
└── examples/
    └── desktop_automation_demo.py  # 🆕 اسکریپت نمایشی

راهنما: 🆕 جدید | ✏️ بهبودیافته | موجود
```

---

## 🎯 فازهای توسعه (Development Phases)

### فاز ۱: پایه‌گذاری (روزهای ۱-۲) ⚡ از اینجا شروع کنید
**فایل‌ها**: `mouse_control.py`, `keyboard_control.py`, `smart_wait.py`

**APIهای کلیدی**:
```python
# ماوس (Mouse)
mouse.click(x, y, button='left')
mouse.move(x, y, duration=0.5)
mouse.drag(start_x, start_y, end_x, end_y)

# کیبورد (Keyboard)
keyboard.type_text("Hello")
keyboard.hotkey('ctrl', 'c')
keyboard.press_key('enter')

# انتظار (Wait)
waiter.wait_for_element(text="OK")
waiter.wait_for_change(region)
```

### فاز ۲: یکپارچه‌سازی (روزهای ۳-۴)
**فایل‌ها**: `desktop_vision.py` بهبودیافته، `action_controller.py`

**APIهای کلیدی**:
```python
# بینایی (Vision)
vision.find_image(template_path)
vision.find_text_boxes("Submit")
vision.verify_click_success(region)

# کنترلر (Controller)
controller.click_on_text("OK")
controller.type_in_field(field_id, "text")
controller.fill_form(fields_dict)
```

### فاز ۳: هوش مصنوعی (روزهای ۵-۶)
**فایل‌ها**: `desktop_actions.py`، `intelligent_agent.py` بهبودیافته

**APIهای کلیدی**:
```python
# عملیات (Actions)
action = ClickAction(target="OK button")
action = TypeAction(text="Hello", target="search")
action = DragDropAction(source="file", target="folder")

# عامل هوشمند (Agent)
agent.process_request("Click on OK")
agent.process_request("Type 'hello' in search box")
```

### فاز ۴: قابلیت اطمینان (روز ۷)
**فایل‌ها**: `action_safety.py`, `action_recovery.py`

**APIهای کلیدی**:
```python
# امنیت (Safety)
safety.validate_desktop_action(action)
safety.is_safe_click_area(x, y)

# بازیابی (Recovery)
recovery.retry_click(action, max_retries=3)
recovery.fallback_to_keyboard(failed_action)
```

### فاز ۵: پیشرفته (روزهای ۸-۹)
**فایل‌ها**: ویژگی‌های پیشرفته، بهینه‌سازی‌ها

### فاز ۶: کیفیت (روز ۱۰)
**فایل‌ها**: تست‌ها، مستندات، نمایش‌ها

---

## 🔧 وظایف رایج (Common Tasks)

### وظیفه: ایجاد عملیات جدید (Create a New Action)
```python
# ۱. تعریف در desktop_actions.py
@dataclass
class MyAction(SystemAction):
    param1: str
    param2: int = 10
    
    def get_risk_level(self) -> RiskLevel:
        return RiskLevel.LOW
    
    def validate(self) -> tuple[bool, str]:
        return True, "Valid"
    
    def describe(self) -> str:
        return f"My action with {self.param1}"

# ۲. افزودن تست
def test_my_action():
    action = MyAction(param1="test")
    assert action.validate()[0] == True

# ۳. مستندسازی در DESKTOP_ACTIONS.md
```

### وظیفه: افزودن به کنترلر عملیات (Add to Action Controller)
```python
# در action_controller.py
async def my_custom_action(self, param: str) -> ActionResult:
    """عملیات سفارشی سطح‌بالا."""
    # استفاده از mouse, keyboard, vision, wait
    await self.mouse.click(x, y)
    await self.keyboard.type_text(param)
    return ActionResult(...)
```

### وظیفه: یکپارچه‌سازی با عامل هوشمند (Integrate with Agent)
```python
# در intelligent_agent.py
async def process_request(self, user_request: str):
    # تجزیه درخواست
    if "my action" in user_request.lower():
        action = MyAction(param1=extracted_param)
        result = await self.execute_action(action)
        return result
```

---

## 🧪 چک‌لیست تست (Testing Checklist)

### برای هر ماژول (For Each Module)
- [ ] تست‌های واحد نوشته شده (Unit tests written)
- [ ] موردهای لبه پوشش داده شده (Edge cases covered)
- [ ] مدیریت خطا تست شده (Error handling tested)
- [ ] عملکرد سنجیده شده (Performance benchmarked)
- [ ] امنیت اعتبارسنجی شده (Security validated)

### تست‌های یکپارچه‌سازی (Integration Tests)
- [ ] گردش کار سرتاسری (End-to-end workflows)
- [ ] سناریوهای چندمرحله‌ای (Multi-step scenarios)
- [ ] بازیابی خطا (Error recovery)
- [ ] اعتبارسنجی امنیت (Safety validation)

### ساختار تست نمونه (Example Test Structure)
```python
import pytest
from core.mouse_control import MouseController

class TestMouseControl:
    def setup_method(self):
        """مقداردهی اولیه برای هر تست (Setup for each test)"""
        self.mouse = MouseController()
    
    def test_click_success(self):
        """تست کلیک موفق (Test successful click)"""
        result = self.mouse.click(100, 100)
        assert result.success
    
    def test_click_out_of_bounds(self):
        """تست کلیک خارج از محدوده (Test out of bounds)"""
        with pytest.raises(ValueError):
            self.mouse.click(-1, -1)
    
    @pytest.mark.slow
    def test_performance(self):
        """تست عملکرد (Performance test)"""
        import time
        start = time.time()
        self.mouse.click(100, 100)
        assert time.time() - start < 0.1
```

---

## 📝 الگوی مستندسازی (Documentation Template)

### برای هر ماژول (For Each Module)
```markdown
# نام ماژول

## معرفی (Overview)
توضیح مختصر درباره کارکرد این ماژول.

## نصب (Installation)
مراحل نصب ویژه (اگر لازم است).

## شروع سریع (Quick Start)
```python
from core.module import Class
obj = Class()
obj.method()
```

## مرجع API (API Reference)
### Class: ClassName
توضیح.

#### متدها (Methods)
- `method(param: type) -> return_type`: توضیح (Description)

## مثال‌ها (Examples)
### مثال ۱: استفاده پایه (Example 1: Basic Usage)
مثال کد با توضیح.

### مثال ۲: استفاده پیشرفته (Example 2: Advanced Usage)
مثال پیچیده‌تر.

## رفع مشکل (Troubleshooting)
مشکلات رایج و راه‌حل‌ها.

## مراجع مرتبط (See Also)
لینک به مستندات مرتبط.
```

---

## 🚨 راهنماهای امنیتی (Safety Guidelines)

### قبل از پیاده‌سازی هر عملیاتی (Before Implementing Any Action)
1. ✅ تعیین سطح ریسک (Define risk level)
2. ✅ افزودن اعتبارسنجی (Add validation)
3. ✅ بررسی محدوده‌ها (Check boundaries)
4. ✅ ثبت عملیات (Log action)
5. ✅ افزودن قابلیت undo (در صورت امکان)

### سطوح ریسک (Risk Levels)
```python
SAFE      # فقط خواندن (Read-only) - مثل get position
LOW       # عملیات ساده (Simple actions) - مثل click
MEDIUM    # مخرب (Destructive) - مثل drag file
HIGH      # تغییرات سیستمی (System changes) - مثل install
CRITICAL  # خطرناک (Dangerous) - مثل delete system file
```

### بررسی‌های امنیتی ضروری (Required Safety Checks)
```python
# امنیت موقعیت (Location safety)
if not self.is_safe_position(x, y):
    raise ValueError("موقعیت ناامن - Unsafe position")

# امنیت محتوا (Content safety)
if self.contains_dangerous_content(text):
    raise ValueError("محتوای خطرناک - Dangerous content")

# محدودیت نرخ (Rate limiting)
if self.is_rate_limited():
    raise RateLimitError("عملیات بیش از حد - Too many actions")
```

---

## 🎨 راهنمای سبک کدنویسی (Code Style Guide)

### قراردادهای نام‌گذاری (Naming Conventions)
```python
# کلاس‌ها: PascalCase (Classes)
class MouseController:
    pass

# توابع/متدها: snake_case (Functions/Methods)
def click_on_element():
    pass

# ثابت‌ها: UPPER_CASE (Constants)
MAX_RETRIES = 3

# خصوصی: _prefix (Private)
def _internal_method():
    pass
```

### نشانه‌های نوع (Type Hints)
```python
# همیشه از type hints استفاده کنید (Always use type hints)
def click(x: int, y: int, button: str = 'left') -> ActionResult:
    pass

# برای nullable از Optional استفاده کنید (Use Optional for nullable)
def find_element(text: str) -> Optional[Box]:
    pass

# برای چند نوع از Union استفاده کنید (Use Union for multiple types)
def process(input: str | int) -> bool:
    pass
```

### مستندسازی داخلی (Docstrings)
```python
def method(param: str) -> bool:
    """توضیح کوتاه (Short description).
    
    توضیح بلندتر با جزئیات بیشتر درباره کارکرد این متد و زمان استفاده.
    (Longer description with more details)
    
    Args:
        param: توضیح پارامتر (Description of param)
    
    Returns:
        توضیح مقدار برگشتی (Description of return value)
    
    Raises:
        ValueError: زمانی که پارامتر نامعتبر است (When param is invalid)
    
    Example:
        >>> method("test")
        True
    """
    pass
```

---

## 🔍 نکات عیب‌یابی (Debugging Tips)

### فعال‌سازی لاگ دیباگ (Enable Debug Logging)
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### استفاده از حالت Dry Run (Use Dry Run Mode)
```python
agent = IntelligentSystemAgent(dry_run=True)
# عملیات لاگ می‌شوند اما اجرا نمی‌شوند (Actions logged but not executed)
```

### عیب‌یابی بصری (Visual Debugging)
```python
from core.desktop_vision import DesktopVision

vision = DesktopVision()
screenshot = vision.capture_screen()  # تهیه اسکرین‌شات (Capture screenshot)
vision.draw_box(screenshot, box, color='red')  # رسم کادر (Draw box)
screenshot.save('debug.png')  # ذخیره برای بررسی (Save for review)
```

### مشکلات رایج (Common Issues)

**مشکل**: کلیک کار نمی‌کند (Click not working)
```python
# راه حل ۱: بررسی مختصات (Solution 1: Check coordinates)
print(f"در حال کلیک در: {x}, {y}")
print(f"اندازه صفحه: {vision.get_screen_size()}")

# راه حل ۲: افزودن تأخیر (Solution 2: Add delay)
await asyncio.sleep(0.5)
mouse.click(x, y)

# راه حل ۳: تأیید عنصر (Solution 3: Verify element)
if vision.find_text("OK"):
    mouse.click(x, y)
```

**مشکل**: تایپ کار نمی‌کند (Type not working)
```python
# راه حل ۱: ابتدا فوکوس کنید (Focus first)
await controller.click_on_field(field_id)
await asyncio.sleep(0.2)
keyboard.type_text(text)

# راه حل ۲: از clipboard استفاده کنید
keyboard.copy_to_clipboard(text)
keyboard.hotkey('ctrl', 'v')
```

**مشکل**: عنصر پیدا نشد (Element not found)
```python
# راه حل ۱: منتظر بمانید (Wait for it)
await waiter.wait_for_element(text, timeout=10)

# راه حل ۲: اطمینان کمتر استفاده کنید (Use lower confidence)
box = vision.find_text(text, confidence=0.7)

# راه حل ۳: تطبیق الگو (Try template match)
box = vision.find_image(template_path)
```

---

## 📊 نکات عملکردی (Performance Tips)

### بهینه‌سازی Vision (Optimize Vision)
```python
# فعال‌سازی کش (Cache screenshots)
vision._cache_enabled = True

# استفاده از ناحیه به‌جای تمام صفحه (Use regions)
region = (100, 100, 500, 500)
vision.capture_region(region)

# کاهش کیفیت OCR برای سرعت (Lower OCR quality)
vision.read_text(screenshot, config='--psm 6')
```

### عملیات ناهمزمان (Async Operations)
```python
# اجرای موازی چندین انتظار (Run multiple waits in parallel)
await asyncio.gather(
    waiter.wait_for_window("App"),
    waiter.wait_for_element("OK"),
)

# بلاک نکردن بی‌دلیل (Don't block unnecessarily)
await controller.click_on_text("OK", verify=False)
```

### عملیات دسته‌جمعی (Batch Operations)
```python
# بد (Bad)
for item in items:
    await keyboard.type_text(item)

# خوب (Good)
text = '\n'.join(items)
await keyboard.type_text(text)
```

---

## 🎯 چک‌لیست روزانه (Daily Checklist)

### شروع روز (Start of Day)
- [ ] بررسی برنامه امروز (Review plan for today)
- [ ] بررسی وضعیت Git (Check Git status)
- [ ] دریافت آخرین تغییرات (Pull latest changes)
- [ ] اجرای تست‌های موجود (Run existing tests)

### حین توسعه (During Development)
- [ ] ابتدا تست بنویسید (Write test first - TDD)
- [ ] پیاده‌سازی ویژگی (Implement feature)
- [ ] افزودن docstring
- [ ] اجرای تست‌ها (Run tests)
- [ ] Commit با پیام واضح (Clear message)

### پایان روز (End of Day)
- [ ] همه تست‌ها پاس می‌شوند (All tests passing)
- [ ] کد بررسی شده (Code reviewed)
- [ ] مستندات به‌روز شده (Documentation updated)
- [ ] Push تغییرات (Push changes)
- [ ] به‌روزرسانی پیشرفت (Update progress)

---

## 📚 منابع (Resources)

### مستندات (Documentation)
- [برنامه اصلی](WEEK2_ACTION_LAYER_PLAN.md) - نقشه راه کامل
- [خلاصه اجرایی](WEEK2_EXECUTIVE_SUMMARY.md) - دیدکلی
- [مرجع API](API_REFERENCE.md) - API کامل

### منابع خارجی (External Resources)
- [pyautogui docs](https://pyautogui.readthedocs.io/)
- [pynput docs](https://pynput.readthedocs.io/)
- [OpenCV tutorial](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)

### مثال‌ها (Examples)
```python
# مثال ۱: کلیک ساده (Example 1: Simple click)
from core.intelligent_agent import IntelligentSystemAgent

agent = IntelligentSystemAgent()
await agent.process_request("روی دکمه OK کلیک کن")

# مثال ۲: پرکردن فرم (Example 2: Form filling)
await agent.process_request("""
فرم را پر کن:
- Name: John Doe
- Email: john@example.com
روی Submit کلیک کن
""")

# مثال ۳: کشیدن و رها کردن (Example 3: Drag and drop)
await agent.process_request("فایل file.txt را به پوشه Documents بکش")
```

---

## 🚀 دستورات سریع (Quick Commands)

### نصب (Setup)
```bash
# نصب وابستگی‌ها (Install dependencies)
pip install -r requirements.txt

# اجرای تست‌ها (Run tests)
pytest

# اجرای تست خاص (Run specific test)
pytest tests/test_mouse_control.py

# پوشش کد (Coverage)
pytest --cov=core --cov-report=html
```

### توسعه (Development)
```bash
# فرمت کد (Format code)
black core/

# بررسی نوع (Type check)
mypy core/

# بررسی کد (Lint)
flake8 core/

# اجرای نمایش (Run demo)
python examples/desktop_automation_demo.py
```

### گردش کار Git (Git Workflow)
```bash
# ویژگی جدید (New feature)
git checkout -b feature/mouse-control
git add .
git commit -m "feat: add mouse control module"
git push origin feature/mouse-control

# به‌روزرسانی مستندات (Update docs)
git add docs/
git commit -m "docs: add mouse control documentation"
```

---

## 💡 نکات حرفه‌ای (Pro Tips)

1. **با تست شروع کنید** (Start with Tests): رویکرد TDD وقت شما را ذخیره می‌کند
2. **از Type Hints استفاده کنید** (Use Type Hints): خطاها را زودتر می‌گیرد
3. **همه چیز را لاگ کنید** (Log Everything): عیب‌یابی آسان‌تر می‌شود
4. **امنیت اولویت است** (Safety First): قبل از اجرا اعتبارسنجی کنید
5. **همزمان با کد مستندسازی کنید** (Document as You Code): به بعد موکول نکنید
6. **عملکرد را پروفایل کنید** (Profile Performance): آنچه مهم است را بهینه کنید
7. **کمک بخواهید** (Ask for Help): گیر نکنید
8. **مکرر Commit کنید** (Commit Often): Commitهای کوچک و متمرکز
9. **کد خود را بررسی کنید** (Review Your Code): طوری باشید که شما بررسی‌کننده هستید
10. **پیشرفت را جشن بگیرید** (Celebrate Progress): دستاوردها را بپذیرید!

---

## 📞 دریافت کمک (Getting Help)

### کمک خودمحور (Self-Help)
1. این مرجع سریع را بررسی کنید (Check this Quick Reference)
2. برنامه اصلی را بخوانید (Read the Master Plan)
3. به کد موجود نگاه کنید (Look at existing code)
4. تست‌ها را اجرا کنید (Run the tests)
5. مستندات را بررسی کنید (Check documentation)

### درخواست کمک (Ask for Help)
1. مشکل را به وضوح شرح دهید (Describe the problem clearly)
2. کد مرتبط را به اشتراک بگذارید (Share relevant code)
3. پیام‌های خطا را بفرستید (Include error messages)
4. نشان دهید چه امتحان کرده‌اید (Show what you've tried)
5. سؤالات مشخص بپرسید (Ask specific questions)

---

**این فایل دستیار روزانه توست!** 🎯

**این صفحه را Bookmark کن و هر روز مراجعه کن.**

---

*آخرین به‌روزرسانی: برنامه‌ریزی هفته ۲ (2025-11-26)*  
*وضعیت: آماده برای توسعه*  
*بعدی: شروع فاز ۱ (کنترل ماوس)*

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: December 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
