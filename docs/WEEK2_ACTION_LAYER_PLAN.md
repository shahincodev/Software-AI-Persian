# 🎯 Week 2: Action Layer Implementation Plan
## Click, Type, Smart Wait - Desktop Automation Enhancement

> **هدف اصلی**: توسعه لایه Action برای کنترل کامل Desktop ویندوز با قابلیت‌های Click, Type, و Smart Wait

---

## 📊 وضعیت فعلی پروژه (Current State Analysis)

### ✅ موارد موجود
1. **Browser Control** (100%)
   - کنترل کامل مرورگر با browser-use
   - Agent پیشرفته برای وب اتوماسیون
   - Browser Vision و Element Detection

2. **Desktop Vision** (90%)
   - Screenshot capture (تمام صفحه + ناحیه خاص)
   - OCR با Tesseract
   - Window Management
   - Element Detection
   - Change Detection
   - Smart Waiting

3. **Windows Automation** (70%)
   - Launch App
   - Install Package
   - Query Hardware
   - Terminate Process
   - Safety Filter & Security
   - Execution Manager

4. **AI Integration** (85%)
   - Multi-model support (OpenAI, Google, Groq, Browser-Use)
   - Auto model selection
   - System-aware AI
   - Voice I/O

### ❌ موارد ناقص (Gap Analysis)
1. **Physical Interaction** - ندارد
   - Mouse Click (Left/Right/Double)
   - Mouse Movement
   - Mouse Drag & Drop
   - Keyboard Input (Type)
   - Hotkey Support (Ctrl+C, Alt+Tab, ...)

2. **Advanced Vision** - محدود
   - Template Matching
   - Image Recognition
   - UI Element Classification
   - Visual Validation

3. **Smart Automation** - نیاز به توسعه
   - Context-aware clicking
   - Intelligent retry mechanism
   - State verification
   - Error recovery

---

## 🏗️ معماری Week 2 - Action Layer

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Interface (main.py)                  │
│          Voice Input/Text → IntelligentSystemAgent           │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 IntelligentSystemAgent (Enhanced)            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │SystemActions │  │VisionActions │  │BrowserActions│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    🆕 Action Layer (NEW)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ ActionController (Orchestrator)                      │   │
│  │  - Coordinate Click/Type/Wait                       │   │
│  │  - Vision-guided actions                            │   │
│  │  - State management                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │MouseControl│  │KbdControl  │  │SmartWait   │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Desktop Vision (Enhanced)                       │
│  - Element Location    - Visual Feedback                    │
│  - Template Match      - State Verification                 │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Windows OS (pyautogui/pynput)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Roadmap

### **Phase 1: Core Action Infrastructure** (Days 1-2)

#### Task 1.1: Mouse Control System
**File**: `core/mouse_control.py`

```python
class MouseController:
    """کنترل کامل موس با امنیت و اعتبارسنجی"""
    
    # Features:
    - click(x, y, button='left', clicks=1, interval=0.1)
    - move(x, y, duration=0.5, smooth=True)
    - drag(start_x, start_y, end_x, end_y, duration=0.5)
    - scroll(clicks, direction='down')
    - get_position() -> (x, y)
    - is_safe_position(x, y) -> bool  # امنیت
```

**Dependencies**: `pyautogui`, `pynput`

**Test File**: `tests/test_mouse_control.py`
- Unit tests for all methods
- Boundary testing
- Safety validation
- Performance benchmarks

**Doc File**: `docs/MOUSE_CONTROL.md`

---

#### Task 1.2: Keyboard Control System
**File**: `core/keyboard_control.py`

```python
class KeyboardController:
    """کنترل کیبورد با پشتیبانی کامل از زبان‌ها"""
    
    # Features:
    - type_text(text, interval=0.05, validate=True)
    - press_key(key, presses=1, interval=0.1)
    - hotkey(*keys)  # Ctrl+C, Alt+Tab, Win+D
    - hold_key(key, duration=1.0)
    - is_typing_safe(text) -> bool  # امنیت
```

**Special Features**:
- Persian/English auto-detection
- Special character handling
- Clipboard integration
- Undo safety

**Test File**: `tests/test_keyboard_control.py`
**Doc File**: `docs/KEYBOARD_CONTROL.md`

---

#### Task 1.3: Smart Wait System
**File**: `core/smart_wait.py`

```python
class SmartWaiter:
    """سیستم هوشمند انتظار با Vision Integration"""
    
    # Wait Strategies:
    - wait_for_element(image/text, timeout=10, check_interval=0.5)
    - wait_for_change(region, threshold=0.1, timeout=10)
    - wait_for_window(title, timeout=10)
    - wait_for_process(name, timeout=10)
    - wait_for_idle(cpu_threshold=10, duration=2)
    - wait_for_color(x, y, color, timeout=10)
    
    # Advanced:
    - retry_with_backoff(action, max_retries=3, backoff_factor=2)
    - poll_until(condition_func, timeout=10, interval=0.5)
```

**Test File**: `tests/test_smart_wait.py`
**Doc File**: `docs/SMART_WAIT.md`

---

### **Phase 2: Vision-Guided Actions** (Days 3-4)

#### Task 2.1: Enhanced Desktop Vision
**File**: `core/desktop_vision.py` (ENHANCE EXISTING)

**New Features**:
```python
class DesktopVision:
    # Template Matching
    def find_image(template_path, confidence=0.8) -> Optional[Box]
    def find_all_images(template_path, confidence=0.8) -> list[Box]
    
    # Color Detection
    def get_pixel_color(x, y) -> tuple[int, int, int]
    def find_color(color, region=None) -> Optional[tuple[int, int]]
    
    # UI Element Recognition
    def find_button(text) -> Optional[Box]
    def find_input_field() -> Optional[Box]
    def classify_element(region) -> ElementType
    
    # Visual Validation
    def verify_click_success(region) -> bool
    def verify_text_typed(expected_text) -> bool
```

**Test File**: `tests/test_desktop_vision_enhanced.py`
**Doc File**: Update `docs/DESKTOP_VISION.md`

---

#### Task 2.2: Action Controller (Orchestrator)
**File**: `core/action_controller.py`

```python
class ActionController:
    """کنترلر اصلی که Vision + Mouse + Keyboard + Wait را هماهنگ می‌کند"""
    
    def __init__(
        vision: DesktopVision,
        mouse: MouseController,
        keyboard: KeyboardController,
        waiter: SmartWaiter
    ):
        pass
    
    # High-Level Actions
    async def click_on_text(text: str, button='left', verify=True) -> ActionResult
    async def click_on_image(image_path: str, verify=True) -> ActionResult
    async def type_in_field(field_identifier, text, verify=True) -> ActionResult
    async def select_menu_item(menu_path: list[str]) -> ActionResult
    
    # Complex Workflows
    async def fill_form(fields: dict) -> ActionResult
    async def drag_and_drop(source, target) -> ActionResult
    async def navigate_ui(steps: list[dict]) -> ActionResult
```

**Test File**: `tests/test_action_controller.py`
**Doc File**: `docs/ACTION_CONTROLLER.md`

---

### **Phase 3: Action Schema & System Integration** (Days 5-6)

#### Task 3.1: Define Action Schema
**File**: `core/desktop_actions.py`

```python
# New Action Types (extend SystemAction)

@dataclass
class ClickAction(SystemAction):
    target: str | tuple[int, int]  # text or (x, y)
    button: str = 'left'
    clicks: int = 1
    verify: bool = True

@dataclass
class TypeAction(SystemAction):
    text: str
    target: Optional[str] = None  # element to type in
    verify: bool = True

@dataclass
class WaitAction(SystemAction):
    wait_type: str  # 'element', 'window', 'change', 'idle'
    target: Any
    timeout: float = 10.0

@dataclass
class DragDropAction(SystemAction):
    source: str | tuple[int, int]
    target: str | tuple[int, int]
    verify: bool = True

@dataclass
class HotkeyAction(SystemAction):
    keys: list[str]  # ['ctrl', 'c']
    verify: bool = False
```

**Test File**: `tests/test_desktop_actions.py`
**Doc File**: `docs/DESKTOP_ACTIONS.md`

---

#### Task 3.2: Update Intelligent Agent
**File**: `core/intelligent_agent.py` (ENHANCE)

**Additions**:
```python
class IntelligentSystemAgent:
    def __init__(self, ...):
        # Add new components
        self.action_controller = ActionController(...)
    
    async def process_request(self, user_request: str):
        # Enhanced parsing for desktop actions
        actions = await self.parser.parse_request(user_request)
        
        # Now supports:
        # - "Click on OK button"
        # - "Type 'hello' in search box"
        # - "Wait until window appears"
        # - "Drag file to folder"
```

**Test File**: `tests/test_intelligent_agent_enhanced.py`
**Doc File**: Update `docs/AI_WINDOWS_CONTROL.md`

---

### **Phase 4: Safety & Reliability** (Day 7)

#### Task 4.1: Action Safety Filter
**File**: `core/action_safety.py`

```python
class ActionSafetyFilter:
    """امنیت اقدامات Desktop"""
    
    # Boundaries
    def is_safe_click_area(x, y) -> bool
    def is_safe_text(text) -> bool
    
    # Rate Limiting
    def check_action_rate(action_type) -> bool
    
    # Validation
    def validate_desktop_action(action) -> tuple[bool, str, bool]
```

#### Task 4.2: Error Recovery
**File**: `core/action_recovery.py`

```python
class ActionRecovery:
    """بازیابی از خطا در اقدامات"""
    
    # Recovery Strategies
    async def retry_click(action, max_retries=3)
    async def fallback_to_keyboard(failed_mouse_action)
    async def recover_from_state(checkpoint)
    
    # Monitoring
    def detect_ui_freeze() -> bool
    def detect_permission_error() -> bool
```

---

### **Phase 5: Advanced Features** (Days 8-9)

#### Task 5.1: Multi-Monitor Support
**File**: `core/multi_monitor.py`

```python
class MultiMonitorManager:
    def get_monitors() -> list[MonitorInfo]
    def find_element_across_monitors(target) -> Optional[Box]
    def move_mouse_to_monitor(monitor_id, x, y)
```

#### Task 5.2: Context-Aware Actions
**File**: `core/context_aware_actions.py`

```python
class ContextAwareActionPlanner:
    """برنامه‌ریزی هوشمند بر اساس context"""
    
    async def plan_action_sequence(goal: str) -> list[Action]
    async def adapt_to_ui_change(original_plan) -> list[Action]
    async def learn_from_success(action, result)
```

---

### **Phase 6: Testing & Documentation** (Day 10)

#### Task 6.1: Comprehensive Testing
**Files**: `tests/integration/`
- `test_complete_workflow.py` - End-to-end scenarios
- `test_error_scenarios.py` - Edge cases
- `test_performance.py` - Benchmarks
- `test_safety.py` - Security validation

**Scenarios**:
1. باز کردن Notepad + تایپ + ذخیره
2. کلیک روی منو + انتخاب گزینه
3. پر کردن فرم چندفیلدی
4. کار با چند مانیتور
5. بازیابی از خطا

#### Task 6.2: Complete Documentation
**Files**:
- Update `README.md` - Week 2 features
- `docs/WEEK2_FEATURES.md` - Feature overview
- `docs/EXAMPLES.md` - Usage examples
- `docs/TROUBLESHOOTING.md` - Common issues
- `docs/API_REFERENCE.md` - Complete API

**Examples**:
```python
# Example 1: Simple Click
from core.intelligent_agent import IntelligentSystemAgent

agent = IntelligentSystemAgent()
await agent.process_request("Click on the OK button")

# Example 2: Complex Workflow
await agent.process_request("""
Open Notepad
Type 'Hello, AI!'
Save the file as test.txt
Close Notepad
""")

# Example 3: Form Filling
await agent.process_request("""
Fill the registration form:
- Name: John Doe
- Email: john@example.com
- Click Submit button
""")
```

---

## 🔧 Technical Stack

### Dependencies (Add to requirements.txt)
```txt
# Week 2 - Action Layer
pyautogui>=0.9.54        # Mouse/Keyboard control
pynput>=1.7.6            # Input monitoring
opencv-python>=4.8.0     # Template matching
Pillow>=10.0.0          # Image processing (existing)
pytesseract>=0.3.10     # OCR (existing)
pygetwindow>=0.0.9      # Window management (existing)
numpy>=1.24.0           # Image operations
```

### Environment Variables (.env)
```bash
# Action Layer Settings
ACTION_SAFETY_ENABLED=true
ACTION_VERIFY_BY_DEFAULT=true
ACTION_RETRY_COUNT=3
ACTION_TIMEOUT=10

# Vision Settings
VISION_CONFIDENCE_THRESHOLD=0.8
TEMPLATE_MATCH_METHOD=cv2.TM_CCOEFF_NORMED

# Mouse Settings
MOUSE_MOVE_DURATION=0.5
MOUSE_SMOOTH_MOVEMENT=true

# Keyboard Settings
KEYBOARD_TYPE_INTERVAL=0.05
KEYBOARD_VERIFY_TYPING=true
```

---

## 📊 Success Metrics

### Performance Targets
- ✅ Click accuracy: >95%
- ✅ Type speed: >100 WPM
- ✅ Element detection: <500ms
- ✅ Action verification: <1s
- ✅ Error recovery: >80% success

### Quality Targets
- ✅ Test coverage: >85%
- ✅ Documentation: 100% API coverage
- ✅ Code review: All PRs reviewed
- ✅ Security: No critical vulnerabilities

### User Experience
- ✅ Natural language commands work >90% of time
- ✅ Error messages are helpful
- ✅ No system crashes
- ✅ Graceful degradation

---

## 🎯 Week 2 Deliverables Checklist

### Code
- [ ] `core/mouse_control.py` ✓ Complete + Tests + Docs
- [ ] `core/keyboard_control.py` ✓ Complete + Tests + Docs
- [ ] `core/smart_wait.py` ✓ Complete + Tests + Docs
- [ ] `core/action_controller.py` ✓ Complete + Tests + Docs
- [ ] `core/desktop_actions.py` ✓ Complete + Tests + Docs
- [ ] Enhanced `core/desktop_vision.py` ✓ Tests + Docs
- [ ] Enhanced `core/intelligent_agent.py` ✓ Tests + Docs
- [ ] `core/action_safety.py` ✓ Complete + Tests + Docs
- [ ] `core/action_recovery.py` ✓ Complete + Tests + Docs

### Tests
- [ ] Unit tests for each module (>80% coverage)
- [ ] Integration tests (complete workflows)
- [ ] Performance benchmarks
- [ ] Security tests
- [ ] Edge case handling

### Documentation
- [ ] `docs/MOUSE_CONTROL.md`
- [ ] `docs/KEYBOARD_CONTROL.md`
- [ ] `docs/SMART_WAIT.md`
- [ ] `docs/ACTION_CONTROLLER.md`
- [ ] `docs/DESKTOP_ACTIONS.md`
- [ ] `docs/WEEK2_FEATURES.md`
- [ ] `docs/EXAMPLES.md`
- [ ] `docs/TROUBLESHOOTING.md`
- [ ] `docs/API_REFERENCE.md`
- [ ] Updated `README.md`

### Demo
- [ ] `examples/desktop_automation_demo.py`
- [ ] Video recording of capabilities
- [ ] Presentation slides

---

## 🚨 Risk Management

### Technical Risks
1. **Performance Issues**
   - Mitigation: Profiling, optimization, async operations
   
2. **OCR Accuracy**
   - Mitigation: Multiple detection methods, user feedback

3. **Security Vulnerabilities**
   - Mitigation: Strict safety filters, audit logging

4. **Platform Compatibility**
   - Mitigation: Windows-specific, extensive testing

### Project Risks
1. **Scope Creep**
   - Mitigation: Strict adherence to plan, MVP approach

2. **Time Management**
   - Mitigation: Daily checkpoints, priority-based development

3. **Quality vs Speed**
   - Mitigation: TDD approach, automated testing

---

## 📈 Next Steps (Week 3+)

### Potential Extensions
1. **AI Vision Enhancement**
   - YOLOv8 for object detection
   - GPT-4 Vision for UI understanding

2. **Cross-Platform Support**
   - Linux support (X11/Wayland)
   - macOS support

3. **Advanced Automation**
   - Macro recording & playback
   - Workflow templates
   - Conditional logic

4. **Cloud Integration**
   - Remote control
   - Distributed execution
   - Action marketplace

---

## 💡 Development Guidelines

### Code Style
- Follow PEP 8
- Type hints everywhere
- Comprehensive docstrings
- Error handling in all methods

### Testing
- Write tests FIRST (TDD)
- Mock external dependencies
- Test edge cases
- Performance benchmarks

### Documentation
- Clear examples
- API reference
- Troubleshooting guide
- Video tutorials

### Security
- Input validation
- Safe defaults
- Audit logging
- User consent for risky actions

---

## 🎓 Learning Resources

### Libraries to Study
1. **pyautogui**: [docs](https://pyautogui.readthedocs.io/)
2. **pynput**: [docs](https://pynput.readthedocs.io/)
3. **OpenCV**: [template matching](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html)

### Concepts
- UI Automation patterns
- Vision-based testing
- State machines
- Error recovery strategies

---

## 📞 Support & Collaboration

### Communication
- Daily standup (async)
- Weekly demo
- Code reviews via PR
- Documentation updates

### Tools
- Git for version control
- GitHub Issues for tracking
- Markdown for docs
- pytest for testing

---

**🎯 MISSION: ساخت قوی‌ترین سیستم Desktop Automation با AI که تا به حال ساخته نشده!**

**Timeline**: 10 روز کاری  
**Start Date**: [To be determined]  
**Status**: Ready to begin  
**Priority**: HIGH  

---

*این Plan یک نقشه راه کامل است. هر Task باید به ترتیب و با کیفیت بالا انجام شود.*  
*تست و مستندسازی به اندازه کد اهمیت دارند.*  
*امنیت در هر مرحله در اولویت است.*

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: December 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
