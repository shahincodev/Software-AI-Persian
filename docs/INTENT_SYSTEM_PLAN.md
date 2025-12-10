<div dir="rtl">

# 🧠 Intent Planning System - نقشه راه توسعه جامع

> **هدف**: ساخت موتور هوشمند برای تحلیل درخواست‌های کاربر و تبدیل آن‌ها به پلن‌های قابل اجرا

**وضعیت**: 📝 در حال توسعه  
**مدت زمان**: 6-8 هفته  
**اولویت**: 🔴 بسیار زیاد (بنیاد سیستم)

---

## 📋 فهرست مطالب

1. [معرفی و مفهوم](#معرفی)
2. [معماری سیستم](#معماری)
3. [ماژول‌های مورد نیاز](#ماژول‌ها)
4. [جدول زمانی دقیق](#جدول-زمانی)
5. [استانداردهای کدنویسی](#استانداردها)
6. [تست‌های مورد نیاز](#تست‌ها)

---

## 🎯 معرفی

### چرا Intent Planning؟

**مثال قبل** (سیستم فعلی):
```
کاربر: "بازی کن تا برگردم"
سیستم: ❌ نمی‌دونم دقیقاً باید چی کار کنم
```

**مثال بعد** (با Intent Planning):
```
کاربر: "بازی کن تا برگردم"

سیستم:
  ✅ Intent: Play a game
  ✅ Game Type: Not specified (ask or use last played)
  ✅ Duration: Until user returns (open-ended)
  ✅ Actions: 
     1. Open Steam
     2. Find Counter-Strike
     3. Start match
     4. Play until manual stop signal
  ✅ Safety: Enable pause on emergency
```

### اهداف کلیدی

```
🎯 کاملیت (Completeness)
   └─ هر درخواست رو متوجه شده و plan ساخته بشه

🎯 قابلیت اجرا (Executability)
   └─ پلن رو بتوان مرحله به مرحله اجرا کرد

🎯 انعطاف‌پذیری (Flexibility)
   └─ درخواست‌های مختلف و پیچیده رو handle کند

🎯 بازخورد (Feedback)
   └─ اگر مرحله شکست خورد، بتواند recovery کند

🎯 یادگیری (Learning)
   └─ از تجربیات قبلی یاد بگیرد
```

---

## 🏗️ معماری

### معماری کلی سیستم

```
┌────────────────────────────────────────────────────────────────┐
│                      🎤 User Input Layer                        │
│            (Text, Voice, Commands, Dialogs)                    │
└────────────────────────────────────────────────────────────────┘
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                  🧠 Intent Planning System (NEW)                │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. Intent Analyzer - درک درخواست کاربر                  │  │
│  │    • تشخیص intent اصلی                                  │  │
│  │    • استخراج پارامترهای کلیدی                             │  │
│  │    • تشخیص موارد نامشخص                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ▼                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 2. Dialog Manager - مکالمه برای جزئیات                  │  │
│  │    • سؤال کردن برای موارد نامشخص                         │  │
│  │    • تایید تصمیمات                                      │  │
│  │    • رعایت preference کاربر                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ▼                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 3. Plan Generator - ساخت پلن                            │  │
│  │    • تقسیم‌بندی به steps                                 │  │
│  │    • مرتب‌کردن Sequential/Parallel                        │  │
│  │    • اضافه کردن condition checks                         │  │
│  │    • تعیین timeout و retry logic                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ▼                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 4. Plan Validator - بررسی صحت پلن                       │  │
│  │    • چک کردن feasibility                                 │  │
│  │    • بررسی dependencies                                  │  │
│  │    • تحلیل risk                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ▼                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 5. Memory Integrator - یادآوری                           │  │
│  │    • بازیابی similar tasks                               │  │
│  │    • یادگیری از خطاهای گذشته                             │  │
│  │    • ذخیره‌سازی successful patterns                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                  🎬 Execution Layer                             │
│  (AutonomousAgent, Master Controller, Action Controllers)      │
└────────────────────────────────────────────────────────────────┘
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                  💾 Learning & Memory Layer                     │
│  (Memory System, History, Feedback Collection)                 │
└────────────────────────────────────────────────────────────────┘
```

### جریان داده

```
User Request
    │
    ▼
[Intent Analyzer] → Detected Intent + Parameters
    │
    ▼─── Missing Info? ──→ [Dialog Manager] → Ask User → User Response
    │
    ▼
[Plan Generator] → Sequence of Steps
    │
    ▼
[Plan Validator] → Validate & Optimize
    │
    ▼
[Memory Integrator] → Add Historical Context
    │
    ▼
Executable Plan
    │
    ▼
[Execution Engine]
```

---

## 📦 ماژول‌های مورد نیاز

### 1. Intent Analyzer (`core/intent_analyzer.py`)

**هدف**: تشخیص intent و استخراج اطلاعات اساسی

```python
# ساختار:
class Intent:
    """نمایش intent کاربر"""
    verb: str              # "open", "play", "create", etc.
    target: str            # "steam", "notepad", "folder"
    parameters: Dict[str, Any]  # {game: "counter-strike", duration: "until_i_return"}
    constraints: List[str] # ["no_sound", "minimal_cpu", "safe_mode"]
    confidence: float      # 0.0-1.0
    
class IntentAnalyzer:
    async def analyze(request: str) -> Intent
    async def extract_parameters(intent: Intent) -> Dict
    async def detect_missing_info(intent: Intent) -> List[str]
```

**نمونه استفاده**:
```python
analyzer = IntentAnalyzer()
intent = await analyzer.analyze("بازی کن تا برگردم")
# Returns: Intent(
#   verb="play",
#   target="game",
#   parameters={"game_type": "last_played", "duration": "until_return"},
#   constraints=[],
#   confidence=0.95
# )
```

---

### 2. Dialog Manager (`core/dialog_manager.py`)

**هدف**: مکالمه برای جمع‌آوری اطلاعات ناگزیر

```python
class DialogContext:
    """زمینه مکالمه"""
    intent: Intent
    missing_fields: List[str]
    conversation_history: List[Tuple[str, str]]  # (question, answer)
    
class DialogManager:
    async def collect_missing_info(intent: Intent, context: DialogContext) -> Dict
    async def ask_user(question: str) -> str
    async def confirm_understanding(intent: Intent) -> bool
```

**نمونه**:
```
سیستم: "میخوای کدام بازی را باز کنی؟"
کاربر: "Counter-Strike 2"

سیستم: "برای مدت‌زمان نامحدود بازی کنم؟"
کاربر: "بله"

سیستم: "حالا درخواستت رو متوجه شدم. شروع کنم؟"
```

---

### 3. Plan Generator (`core/plan_generator.py`)

**هدف**: تبدیل intent به مراحل قابل اجرا

```python
class ExecutionStep:
    """یک مرحله در پلن"""
    step_id: str
    description: str
    action_type: str  # "open", "click", "type", "wait", "verify"
    action_target: str  # "steam", "play_button", etc.
    parameters: Dict[str, Any]
    preconditions: List[str]  # "steam_must_be_open"
    postconditions: List[str]  # "game_must_be_running"
    timeout: int  # seconds
    retry_count: int
    
class ExecutionPlan:
    """پلن کامل"""
    goal: Intent
    steps: List[ExecutionStep]
    estimated_duration: int  # seconds
    required_resources: List[str]  # "internet", "gpu", etc.
    safety_level: str  # "safe", "moderate", "risky"
    
class PlanGenerator:
    async def generate(intent: Intent) -> ExecutionPlan
    async def optimize(plan: ExecutionPlan) -> ExecutionPlan
    async def estimate_duration(plan: ExecutionPlan) -> int
```

---

### 4. Plan Validator (`core/plan_validator.py`)

**هدف**: بررسی صحت و امنیت پلن

```python
class ValidationResult:
    """نتیجه validation"""
    is_valid: bool
    issues: List[str]  # ["missing_steam", "insufficient_disk_space"]
    warnings: List[str]  # ["will_use_high_cpu"]
    suggestions: List[str]  # ["install_steam_first"]
    
class PlanValidator:
    async def validate(plan: ExecutionPlan) -> ValidationResult
    async def check_dependencies(plan: ExecutionPlan) -> bool
    async def check_safety(plan: ExecutionPlan) -> bool
    async def check_resources(plan: ExecutionPlan) -> bool
```

---

### 5. Memory Integrator (`core/memory_integrator.py`)

**هدف**: یادگیری از تجربیات و بهبود پلن‌ها

```python
class TaskHistory:
    """تاریخچه task"""
    task_id: str
    original_request: str
    generated_plan: ExecutionPlan
    execution_result: Dict  # success, duration, errors
    learned_patterns: List[str]
    
class MemoryIntegrator:
    async def find_similar_tasks(request: str) -> List[TaskHistory]
    async def learn_from_success(task: TaskHistory) -> None
    async def learn_from_failure(task: TaskHistory) -> None
    async def improve_plan(plan: ExecutionPlan) -> ExecutionPlan
```

---

## ⏱️ جدول زمانی دقیق

### هفته ۱: بنیاد و Intent Analyzer (۷-۱۰ ساعت)

**روز ۱-۲: طراحی و ساختار** (2 ساعت)
```
- کتاب خواندن قابلیت‌های AI موجود
- طراحی data structures
- نوشتن docstrings و comments
```

**روز ۳-۴: Intent Analyzer اصلی** (4 ساعت)
```
- نوشتن `core/intent_analyzer.py`
- تابع `analyze()` اصلی
- تابع `extract_parameters()`
- تابع `detect_missing_info()`
```

**روز ۵: تست‌ها** (2 ساعت)
```
- نوشتن `tests/test_intent_analyzer.py`
- کمپل کردن و اجرا
```

**روز ۶: مستندات** (1 ساعت)
```
- نوشتن `docs/INTENT_ANALYZER.md`
- اضافه کردن نمونه‌ها
```

**روز ۷: Integration** (1 ساعت)
```
- اضافه کردن به `main.py`
- تست عملی
```

---

### هفته ۲: Dialog Manager (۶-۸ ساعت)

**روز ۱-۲: طراحی** (2 ساعت)
```
- تعریف DialogContext
- طراحی conversation flow
```

**روز ۳-۵: پیاده‌سازی** (4 ساعت)
```
- نوشتن `core/dialog_manager.py`
- تابع `collect_missing_info()`
- تابع `ask_user()`
- تابع `confirm_understanding()`
```

**روز ۶-۷: تست و مستندات** (2 ساعت)
```
- تست‌های مربوطه
- نوشتن `docs/DIALOG_MANAGER.md`
```

---

### هفته ۳: Plan Generator (۸-۱۰ ساعت)

**روز ۱-۲: طراحی دقیق** (2 ساعت)
```
- تعریف ExecutionStep
- تعریف ExecutionPlan
- الگوهای مختلف task
```

**روز ۳-۶: پیاده‌سازی** (5 ساعت)
```
- نوشتن `core/plan_generator.py`
- تابع `generate()`
- تابع `optimize()`
```

**روز ۷: تست و integration** (3 ساعت)
```
- تست‌های مربوطه
- مستندات
```

---

### هفته ۴: Plan Validator (۴-۶ ساعت)

**روز ۱-۲: طراحی** (1 ساعت)
```
- تعریف validation rules
```

**روز ۳-۵: پیاده‌سازی** (3 ساعت)
```
- نوشتن `core/plan_validator.py`
- check functions
```

**روز ۶-۷: تست** (2 ساعت)

---

### هفته ۵: Memory Integrator (۶-۸ ساعت)

**روز ۱-۶: پیاده‌سازی و ادغام** (6 ساعت)
```
- نوشتن `core/memory_integrator.py`
- ادغام با Memory System موجود
```

**روز ۷: تست و آپتیمایزاسیون** (2 ساعت)

---

### هفته ۶-۷: Integration و Testing (۱۰-۱۲ ساعت)

**روز ۱-۳: Integration** (4 ساعت)
```
- ادغام کامل با main.py
- تست end-to-end
- debugging
```

**روز ۴-۶: Testing و Optimization** (4 ساعت)
```
- تست جامع
- بهبود performance
- error handling
```

**روز ۷-۸: Documentation** (4 ساعت)
```
- نوشتن `docs/INTENT_SYSTEM.md`
- نوشتن `docs/INTEGRATION_GUIDE.md`
- به‌روز رسانی `README.md`
```

---

## 📝 استانداردهای کدنویسی

### الف) زبان کدنویسی

**قوانین**:
- ✅ **Comments و Docstrings**: دوزبانه (English + فارسی)
- ✅ **Variable Names**: انگلیسی
- ✅ **Class Names**: انگلیسی
- ✅ **Type Hints**: اجباری
- ✅ **Async/Await**: برای عملیات طولانی

**نمونه**:
```python
class IntentAnalyzer:
    """Intent Analyzer - تشخیص هدف و نیت کاربر
    
    این کلاس درخواست‌های طبیعی را تحلیل می‌کند
    و intention مقصود کاربر را استخراج می‌کند.
    
    Example:
        >>> analyzer = IntentAnalyzer()
        >>> intent = await analyzer.analyze("بازی کن")
        >>> print(intent.verb)  # "play"
    """
    
    async def analyze(self, request: str) -> Intent:
        """درخواست کاربر را تحلیل می‌کند و Intent ساخته می‌شود
        
        Args:
            request: درخواست متنی کاربر
            
        Returns:
            Intent: intent تشخیص داده شده
            
        Raises:
            ValueError: اگر request خالی باشد
        """
        if not request:
            raise ValueError("Request cannot be empty")
        
        # تحلیل با AI...
```

### ب) ساختار فایل‌ها

```
core/
├── intent_analyzer.py      # تشخیص intent
├── dialog_manager.py       # مدیریت گفتگو
├── plan_generator.py       # تولید پلن
├── plan_validator.py       # تایید پلن
└── memory_integrator.py    # یادگیری

tests/
├── test_intent_analyzer.py
├── test_dialog_manager.py
├── test_plan_generator.py
├── test_plan_validator.py
└── test_memory_integrator.py

docs/
├── INTENT_ANALYZER.md
├── DIALOG_MANAGER.md
├── PLAN_GENERATOR.md
├── PLAN_VALIDATOR.md
├── MEMORY_INTEGRATOR.md
├── INTENT_SYSTEM.md       # مستندات کامل
└── INTEGRATION_GUIDE.md  # راهنمای ادغام
```

### ج) استانداردهای تست

**نیاز برای هر ماژول**:
```
- Minimum 5 test cases per function
- 80% code coverage
- Happy path + Error cases
- مثال‌های واقعی فارسی
```

---

## 🧪 تست‌های مورد نیاز

### Unit Tests

```python
# test_intent_analyzer.py
async def test_simple_intent():
    """تست parsing درخواست ساده"""
    intent = await analyzer.analyze("باز کن نوت‌پد")
    assert intent.verb == "open"
    assert intent.target == "notepad"

async def test_complex_intent():
    """تست درخواست پیچیده"""
    intent = await analyzer.analyze("بازی کن تا برگردم")
    assert intent.verb == "play"
    assert intent.parameters["duration"] == "until_return"

async def test_missing_info():
    """تست شناسایی اطلاعات نامشخص"""
    intent = await analyzer.analyze("بازی کن")
    missing = await analyzer.detect_missing_info(intent)
    assert "game_type" in missing
```

### Integration Tests

```python
async def test_full_intent_to_plan():
    """تست کامل: intent → dialog → plan → validation"""
    # User request
    intent = await analyzer.analyze("دیتای هوا رو بگیر")
    
    # Dialog for missing info
    missing = await dialog.collect_missing_info(intent)
    assert "city" in missing
    
    # Generate plan
    plan = await generator.generate(intent)
    assert len(plan.steps) > 0
    
    # Validate
    result = await validator.validate(plan)
    assert result.is_valid
```

### End-to-End Tests

```python
async def test_real_world_scenarios():
    """تست سناریوهای واقعی"""
    # Scenario 1: "دیتای هوای تهران را دریافت کن"
    # Scenario 2: "Counter-Strike باز کن و بازی کن"
    # Scenario 3: "MyDocs فولدر در E: بساز"
```

---

## 📊 معیارهای موفقیت

| معیار | هدف |
|-------|------|
| **Code Coverage** | ≥ 80% |
| **Test Pass Rate** | 100% |
| **Intent Accuracy** | ≥ 95% |
| **Plan Validity** | 100% |
| **Documentation** | مکمل و دقیق |
| **Performance** | < 2 sec per intent |

---

## 🚀 مرحله بعد

پس از اتمام Intent Planning System:

1. **Intent-based Autonomous Agent**
   - استفاده از Intent plans در Autonomous Agent
   - بهبود execution accuracy

2. **Multi-step Reasoning**
   - پشتیبانی tasks دارای وابستگی‌های پیچیده
   - Parallel step execution

3. **User Learning**
   - یادگیری preference‌های کاربر
   - ساختن shortcuts و macros

---

## 📞 نکات مهم

⚠️ **توجه**:
- هر ماژول باید **مستقل** و **testable** باشد
- **Comments دوزبانه** اجباری است
- هر commit باید شامل مستندات باشد
- مستندات **قبل** یا **همزمان** با کد نوشته شود
- تست‌ها **قبل** یا **همزمان** با کد نوشته شوند

</div>
