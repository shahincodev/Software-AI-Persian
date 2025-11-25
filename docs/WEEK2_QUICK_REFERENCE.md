# ⚡ Week 2 - Quick Reference
## Action Layer Development Guide

> **مرجع سریع** برای توسعه‌دهندگان - دسترسی آسان به اطلاعات کلیدی

---

## 📁 File Structure

```
Software-AI/
│
├── core/                           # Core modules
│   ├── mouse_control.py           # 🆕 Mouse automation
│   ├── keyboard_control.py        # 🆕 Keyboard automation
│   ├── smart_wait.py              # 🆕 Intelligent waiting
│   ├── action_controller.py       # 🆕 Action orchestrator
│   ├── desktop_actions.py         # 🆕 Action schemas
│   ├── action_safety.py           # 🆕 Safety filters
│   ├── action_recovery.py         # 🆕 Error recovery
│   ├── desktop_vision.py          # ✏️ Enhanced (existing)
│   ├── intelligent_agent.py       # ✏️ Enhanced (existing)
│   └── ...                        # Existing modules
│
├── tests/                          # Test files
│   ├── test_mouse_control.py      # 🆕 Mouse tests
│   ├── test_keyboard_control.py   # 🆕 Keyboard tests
│   ├── test_smart_wait.py         # 🆕 Wait tests
│   ├── test_action_controller.py  # 🆕 Controller tests
│   ├── test_desktop_actions.py    # 🆕 Action tests
│   ├── integration/               # 🆕 Integration tests
│   │   ├── test_complete_workflow.py
│   │   ├── test_error_scenarios.py
│   │   └── test_performance.py
│   └── ...
│
├── docs/                           # Documentation
│   ├── WEEK2_ACTION_LAYER_PLAN.md         # 🆕 Master plan
│   ├── WEEK2_EXECUTIVE_SUMMARY.md         # 🆕 Executive summary
│   ├── WEEK2_QUICK_REFERENCE.md           # 🆕 This file
│   ├── MOUSE_CONTROL.md                   # 🆕 Mouse API
│   ├── KEYBOARD_CONTROL.md                # 🆕 Keyboard API
│   ├── SMART_WAIT.md                      # 🆕 Wait API
│   ├── ACTION_CONTROLLER.md               # 🆕 Controller API
│   ├── DESKTOP_ACTIONS.md                 # 🆕 Action schemas
│   ├── EXAMPLES.md                        # 🆕 Usage examples
│   ├── TROUBLESHOOTING.md                 # 🆕 Common issues
│   ├── API_REFERENCE.md                   # 🆕 Complete API
│   └── ...                                # Existing docs
│
└── examples/
    └── desktop_automation_demo.py  # 🆕 Demo script

Legend: 🆕 New | ✏️ Enhanced | Existing
```

---

## 🎯 Development Phases

### Phase 1: Foundation (Days 1-2) ⚡ START HERE
**Files**: `mouse_control.py`, `keyboard_control.py`, `smart_wait.py`

**Key APIs**:
```python
# Mouse
mouse.click(x, y, button='left')
mouse.move(x, y, duration=0.5)
mouse.drag(start_x, start_y, end_x, end_y)

# Keyboard
keyboard.type_text("Hello")
keyboard.hotkey('ctrl', 'c')
keyboard.press_key('enter')

# Wait
waiter.wait_for_element(text="OK")
waiter.wait_for_change(region)
```

### Phase 2: Integration (Days 3-4)
**Files**: Enhanced `desktop_vision.py`, `action_controller.py`

**Key APIs**:
```python
# Vision
vision.find_image(template_path)
vision.find_text_boxes("Submit")
vision.verify_click_success(region)

# Controller
controller.click_on_text("OK")
controller.type_in_field(field_id, "text")
controller.fill_form(fields_dict)
```

### Phase 3: Intelligence (Days 5-6)
**Files**: `desktop_actions.py`, Enhanced `intelligent_agent.py`

**Key APIs**:
```python
# Actions
action = ClickAction(target="OK button")
action = TypeAction(text="Hello", target="search")
action = DragDropAction(source="file", target="folder")

# Agent
agent.process_request("Click on OK")
agent.process_request("Type 'hello' in search box")
```

### Phase 4: Reliability (Day 7)
**Files**: `action_safety.py`, `action_recovery.py`

**Key APIs**:
```python
# Safety
safety.validate_desktop_action(action)
safety.is_safe_click_area(x, y)

# Recovery
recovery.retry_click(action, max_retries=3)
recovery.fallback_to_keyboard(failed_action)
```

### Phase 5: Advanced (Days 8-9)
**Files**: Advanced features, optimizations

### Phase 6: Quality (Day 10)
**Files**: Tests, docs, demos

---

## 🔧 Common Tasks

### Task: Create a New Action
```python
# 1. Define in desktop_actions.py
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

# 2. Add test
def test_my_action():
    action = MyAction(param1="test")
    assert action.validate()[0] == True

# 3. Document in DESKTOP_ACTIONS.md
```

### Task: Add to Action Controller
```python
# In action_controller.py
async def my_custom_action(self, param: str) -> ActionResult:
    """My custom high-level action."""
    # Use mouse, keyboard, vision, wait
    await self.mouse.click(x, y)
    await self.keyboard.type_text(param)
    return ActionResult(...)
```

### Task: Integrate with Agent
```python
# In intelligent_agent.py
async def process_request(self, user_request: str):
    # Parse request
    if "my action" in user_request.lower():
        action = MyAction(param1=extracted_param)
        result = await self.execute_action(action)
        return result
```

---

## 🧪 Testing Checklist

### For Each Module
- [ ] Unit tests written
- [ ] Edge cases covered
- [ ] Error handling tested
- [ ] Performance benchmarked
- [ ] Security validated

### Integration Tests
- [ ] End-to-end workflows
- [ ] Multi-step scenarios
- [ ] Error recovery
- [ ] Safety validation

### Example Test Structure
```python
import pytest
from core.mouse_control import MouseController

class TestMouseControl:
    def setup_method(self):
        self.mouse = MouseController()
    
    def test_click_success(self):
        result = self.mouse.click(100, 100)
        assert result.success
    
    def test_click_out_of_bounds(self):
        with pytest.raises(ValueError):
            self.mouse.click(-1, -1)
    
    @pytest.mark.slow
    def test_performance(self):
        import time
        start = time.time()
        self.mouse.click(100, 100)
        assert time.time() - start < 0.1
```

---

## 📝 Documentation Template

### For Each Module
```markdown
# Module Name

## Overview
Brief description of what this module does.

## Installation
Any special setup required.

## Quick Start
```python
from core.module import Class
obj = Class()
obj.method()
```

## API Reference
### Class: ClassName
Description.

#### Methods
- `method(param: type) -> return_type`: Description

## Examples
### Example 1: Basic Usage
Code example with explanation.

### Example 2: Advanced Usage
More complex example.

## Troubleshooting
Common issues and solutions.

## See Also
Links to related docs.
```

---

## 🚨 Safety Guidelines

### Before Implementing Any Action
1. ✅ Define risk level
2. ✅ Add validation
3. ✅ Check boundaries
4. ✅ Log action
5. ✅ Add undo capability (if possible)

### Risk Levels
```python
SAFE      # Read-only (e.g., get position)
LOW       # Simple actions (e.g., click)
MEDIUM    # Destructive (e.g., drag file)
HIGH      # System changes (e.g., install)
CRITICAL  # Dangerous (e.g., delete system file)
```

### Required Safety Checks
```python
# Location safety
if not self.is_safe_position(x, y):
    raise ValueError("Unsafe position")

# Content safety
if self.contains_dangerous_content(text):
    raise ValueError("Dangerous content")

# Rate limiting
if self.is_rate_limited():
    raise RateLimitError("Too many actions")
```

---

## 🎨 Code Style Guide

### Naming Conventions
```python
# Classes: PascalCase
class MouseController:
    pass

# Functions/Methods: snake_case
def click_on_element():
    pass

# Constants: UPPER_CASE
MAX_RETRIES = 3

# Private: _prefix
def _internal_method():
    pass
```

### Type Hints
```python
# Always use type hints
def click(x: int, y: int, button: str = 'left') -> ActionResult:
    pass

# Use Optional for nullable
def find_element(text: str) -> Optional[Box]:
    pass

# Use Union for multiple types
def process(input: str | int) -> bool:
    pass
```

### Docstrings
```python
def method(param: str) -> bool:
    """Short description.
    
    Longer description with more details about what
    this method does and when to use it.
    
    Args:
        param: Description of param
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param is invalid
    
    Example:
        >>> method("test")
        True
    """
    pass
```

---

## 🔍 Debugging Tips

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Use Dry Run Mode
```python
agent = IntelligentSystemAgent(dry_run=True)
# Actions will be logged but not executed
```

### Visual Debugging
```python
from core.desktop_vision import DesktopVision

vision = DesktopVision()
screenshot = vision.capture_screen()
vision.draw_box(screenshot, box, color='red')
screenshot.save('debug.png')
```

### Common Issues

**Issue**: Click not working
```python
# Solution 1: Check coordinates
print(f"Clicking at: {x}, {y}")
print(f"Screen size: {vision.get_screen_size()}")

# Solution 2: Add delay
await asyncio.sleep(0.5)
mouse.click(x, y)

# Solution 3: Verify element
if vision.find_text("OK"):
    mouse.click(x, y)
```

**Issue**: Type not working
```python
# Solution 1: Focus first
await controller.click_on_field(field_id)
await asyncio.sleep(0.2)
keyboard.type_text(text)

# Solution 2: Use clipboard
keyboard.copy_to_clipboard(text)
keyboard.hotkey('ctrl', 'v')
```

**Issue**: Element not found
```python
# Solution 1: Wait for it
await waiter.wait_for_element(text, timeout=10)

# Solution 2: Use lower confidence
box = vision.find_text(text, confidence=0.7)

# Solution 3: Try template match
box = vision.find_image(template_path)
```

---

## 📊 Performance Tips

### Optimize Vision
```python
# Cache screenshots
vision._cache_enabled = True

# Use regions instead of full screen
region = (100, 100, 500, 500)
vision.capture_region(region)

# Lower OCR quality for speed
vision.read_text(screenshot, config='--psm 6')
```

### Async Operations
```python
# Run multiple waits in parallel
await asyncio.gather(
    waiter.wait_for_window("App"),
    waiter.wait_for_element("OK"),
)

# Don't block unnecessarily
await controller.click_on_text("OK", verify=False)
```

### Batch Operations
```python
# Bad
for item in items:
    await keyboard.type_text(item)

# Good
text = '\n'.join(items)
await keyboard.type_text(text)
```

---

## 🎯 Daily Checklist

### Start of Day
- [ ] Review plan for today
- [ ] Check Git status
- [ ] Pull latest changes
- [ ] Run existing tests

### During Development
- [ ] Write test first (TDD)
- [ ] Implement feature
- [ ] Add docstring
- [ ] Run tests
- [ ] Commit with clear message

### End of Day
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Push changes
- [ ] Update progress

---

## 📚 Resources

### Documentation
- [Master Plan](WEEK2_ACTION_LAYER_PLAN.md) - Complete roadmap
- [Executive Summary](WEEK2_EXECUTIVE_SUMMARY.md) - Overview
- [API Reference](API_REFERENCE.md) - Complete API

### External Resources
- [pyautogui docs](https://pyautogui.readthedocs.io/)
- [pynput docs](https://pynput.readthedocs.io/)
- [OpenCV tutorial](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)

### Examples
```python
# Example 1: Simple click
from core.intelligent_agent import IntelligentSystemAgent

agent = IntelligentSystemAgent()
await agent.process_request("Click on OK button")

# Example 2: Form filling
await agent.process_request("""
Fill the form:
- Name: John Doe
- Email: john@example.com
Click Submit
""")

# Example 3: Drag and drop
await agent.process_request("Drag file.txt to Documents folder")
```

---

## 🚀 Quick Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run specific test
pytest tests/test_mouse_control.py

# Coverage
pytest --cov=core --cov-report=html
```

### Development
```bash
# Format code
black core/

# Type check
mypy core/

# Lint
flake8 core/

# Run demo
python examples/desktop_automation_demo.py
```

### Git Workflow
```bash
# New feature
git checkout -b feature/mouse-control
git add .
git commit -m "feat: add mouse control module"
git push origin feature/mouse-control

# Update docs
git add docs/
git commit -m "docs: add mouse control documentation"
```

---

## 💡 Pro Tips

1. **Start with Tests**: TDD approach saves time
2. **Use Type Hints**: Catches bugs early
3. **Log Everything**: Debugging is easier
4. **Safety First**: Validate before execute
5. **Document as You Code**: Don't leave it for later
6. **Profile Performance**: Optimize what matters
7. **Ask for Help**: Don't get stuck
8. **Commit Often**: Small, focused commits
9. **Review Your Code**: Pretend you're the reviewer
10. **Celebrate Progress**: Acknowledge achievements!

---

## 📞 Getting Help

### Self-Help
1. Check this Quick Reference
2. Read the Master Plan
3. Look at existing code
4. Run the tests
5. Check documentation

### Ask for Help
1. Describe the problem clearly
2. Share relevant code
3. Include error messages
4. Show what you've tried
5. Ask specific questions

---

**این فایل دستیار روزانه توست! 🎯**

**Bookmark این صفحه و هر روز مراجعه کن.**

---

*Last Updated: Week 2 Planning Phase*  
*Status: Ready for Development*  
*Next: Start Phase 1 (Mouse Control)*

**Let's code! 💻**
