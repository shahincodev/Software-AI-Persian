# Intent Planning System - مستندات کامل یکپارچه‌سازی

## خلاصه

**Intent Planning System** سیستمی 5 لایه برای درک، برنامه‌ریزی، اعتبارسنجی و یادگیری از درخواست‌های کاربر است.

## معماری کلی

```
┌─────────────────────────────────────────────────────────────────┐
│                    درخواست کاربر                                │
│              "بازی کن تا برگردم"                                 │
└───────────────────────┬─────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. Intent Analyzer - تحلیل نیت                                 │
│     ورودی: متن فارسی/انگلیسی                                    │
│     خروجی: Intent{verb, target, parameters, confidence}        │
│     ✅ 611 خط کد | 41 تست                                       │
└───────────────────────┬─────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Dialog Manager - مکالمه برای تکمیل اطلاعات                  │
│     ورودی: Intent ناقص                                          │
│     خروجی: Intent کامل + سؤالات                                 │
│     ✅ 487 خط کد | 42 تست                                       │
└───────────────────────┬─────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Plan Generator - تولید پلان مرحله‌به‌مرحله                 │
│     ورودی: Intent کامل                                          │
│     خروجی: ExecutionPlan{steps[], dependencies, timing}        │
│     ✅ 887 خط کد | 32 تست                                       │
└───────────────────────┬─────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Plan Validator - اعتبارسنجی و امتیازدهی                     │
│     ورودی: ExecutionPlan                                        │
│     خروجی: ValidationReport{scores, issues, suggestions}       │
│     ✅ 742 خط کد | 25 تست                                       │
└───────────────────────┬─────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. Memory Integrator - ثبت و یادگیری                           │
│     ورودی: ExecutionHistory + ValidationReport                  │
│     خروجی: LearningResults + Recommendations                   │
│     ✅ 505 خط کد | 28 تست                                       │
└─────────────────────────────────────────────────────────────────┘
```

## جریان داده‌ها

### مثال واقعی: "بازی کن تا برگردم"

```python
# مرحله 1: تحلیل
analyzer = IntentAnalyzer()
intent = await analyzer.analyze("بازی کن تا برگردم")
# Intent(verb="بازی", target="game", parameters={}, confidence=0.92)

# مرحله 2: گفتگو
dialog = DialogManager()
needs_dialog, missing = dialog.needs_clarification(intent)
# needs_dialog=True, missing=["game_name"]

question = dialog.generate_question(intent)
# "کدام بازی را می‌خواهید اجرا کنید؟"

completed = dialog.process_answer(intent, question, "شطرنج")
# intent.parameters["game_name"] = "Chess"

# مرحله 3: پلان
generator = PlanGenerator()
plan = await generator.generate_plan(intent)
# ExecutionPlan with 3 steps:
#   1. Open Chess application
#   2. Start game
#   3. Set auto-play mode

# مرحله 4: اعتبارسنجی
validator = PlanValidator()
validation = await validator.validate(plan, intent, ValidationLevel.STRICT)
# ValidationReport(
#   is_valid=True,
#   safety_score=95,
#   reliability_score=88,
#   efficiency_score=92
# )

# مرحله 5: اجرا + یادگیری
memory = MemoryIntegrator("data/memories.sqlite3")

# شبیه‌سازی اجرای موفق
record_id = memory.record_execution(
    plan_id=plan.plan_id,
    intent=intent,
    status=PlanStatus.SUCCESSFUL,
    steps_succeeded=3,
    steps_failed=0,
    total_steps=3,
    actual_time_seconds=12.5,
    estimated_time_seconds=15.0
)

# یادگیری
history = ExecutionHistory(...)
learned = memory.learn_from_execution(history, plan, validation)
# ['success', 'pattern'] - الگوی موفق ثبت شد

# برای درخواست بعدی
recommendations = memory.get_recommendations(intent)
# {
#   'similar_plans': 5,
#   'success_rate': 100.0,
#   'avg_execution_time': 12.3,
#   'optimizations': [...]
# }
```

## آمار کلی سیستم

| ماژول | خطوط کد | تست‌ها | وضعیت |
|------|---------|--------|-------|
| Intent Analyzer | 611 | 41 ✅ | تکمیل |
| Dialog Manager | 487 | 42 ✅ | تکمیل |
| Plan Generator | 887 | 32 ✅ | تکمیل |
| Plan Validator | 742 | 25 ✅ | تکمیل |
| Memory Integrator | 505 | 28 ✅ | تکمیل |
| **جمع کل** | **3,232** | **168** | **100%** |

## ویژگی‌های کلیدی

### 🌐 دوزبانه کامل (100%)
- تمام پیام‌ها، خطاها، و مستندات به فارسی و انگلیسی
- پشتیبانی از ورودی مختلط (Pinglish)
- Auto-detection زبان

### 🔒 امنیت چندلایه
- تشخیص عملیات خطرناک (delete, format, registry)
- بررسی مسیرهای حساس (System32, Windows)
- سطوح اعتبارسنجی: BASIC, STRICT, PARANOID
- امتیازدهی امنیتی (0-100)

### 🧠 یادگیری خودکار
- ثبت تاریخچه اجراها
- شناسایی الگوهای موفق
- پیشنهادات بهینه‌سازی
- یادگیری از شکست‌ها

### ⚡ عملکرد بالا
- تحلیل: <100ms
- پلان: <200ms
- اعتبارسنجی: <100ms
- کل pipeline: <500ms

### 🔄 مقیاس‌پذیری
- دیتابیس SQLite برای حافظه
- معماری async/await
- ماژولار و قابل گسترش

## API کامل

### 1. Intent Analyzer

```python
analyzer = IntentAnalyzer()

# تحلیل درخواست
intent = await analyzer.analyze("یک فایل بساز")

# دسترسی به نتایج
print(intent.verb)          # "ایجاد"
print(intent.target)        # "file"
print(intent.confidence)    # 0.95
print(intent.language)      # "fa"
```

### 2. Dialog Manager

```python
dialog = DialogManager()

# بررسی نیاز به گفتگو
needs_dialog, missing = dialog.needs_clarification(intent)

if needs_dialog:
    # تولید سؤال
    question = dialog.generate_question(intent)
    
    # پردازش پاسخ کاربر
    completed = dialog.process_answer(intent, question, user_answer)
```

### 3. Plan Generator

```python
generator = PlanGenerator()

# تولید پلان
plan = await generator.generate_plan(intent)

# دسترسی به مراحل
for step in plan.steps:
    print(f"{step.order}. {step.action}")
    print(f"   Dependencies: {step.dependencies}")
    print(f"   Timeout: {step.timeout}s")
```

### 4. Plan Validator

```python
validator = PlanValidator()

# اعتبارسنجی
validation = await validator.validate(
    plan,
    intent,
    validation_level=ValidationLevel.STRICT,
    check_security=True,
    check_resources=True
)

# دسترسی به نتایج
print(f"Valid: {validation.is_valid}")
print(f"Safety Score: {validation.safety_score}/100")
print(f"Issues: {len(validation.issues)}")
```

### 5. Memory Integrator

```python
memory = MemoryIntegrator("data/memories.sqlite3")

# ثبت اجرا
record_id = memory.record_execution(
    plan_id=plan.plan_id,
    intent=intent,
    status=PlanStatus.SUCCESSFUL,
    steps_succeeded=5,
    steps_failed=0,
    total_steps=5,
    actual_time_seconds=10.0,
    estimated_time_seconds=12.0
)

# دریافت آمار
stats = memory.get_statistics()

# جستجوی مشابه
similar = memory.find_similar_plans(new_intent, threshold=0.7)

# توصیه‌ها
recommendations = memory.get_recommendations(new_intent)
```

## سناریوهای واقعی

### سناریو 1: ایجاد فایل

```python
# درخواست
request = "یک فایل متنی به اسم notes.txt در دسکتاپ بساز"

# 1. تحلیل
intent = await analyzer.analyze(request)
# Intent(verb="ایجاد", target="file", parameters={"filename": "notes.txt", "location": "Desktop"})

# 2. بدون نیاز به گفتگو (پارامترها کامل است)

# 3. پلان
plan = await generator.generate_plan(intent)
# 3 مرحله: navigate to Desktop → create file → open file

# 4. اعتبارسنجی
validation = await validator.validate(plan, intent)
# VALID: safety=95, reliability=90, efficiency=88

# 5. اجرا + یادگیری
record_id = memory.record_execution(...)
learned = memory.learn_from_execution(...)
```

### سناریو 2: باز کردن برنامه

```python
request = "Notepad را باز کن"

intent = await analyzer.analyze(request)
# Intent(verb="باز", target="notepad")

plan = await generator.generate_plan(intent)
# 2 مرحله: find notepad → launch application

validation = await validator.validate(plan, intent)
# VALID: safe operation

# اجرا
execute_plan(plan)
memory.record_execution(...)
```

### سناریو 3: عملیات خطرناک

```python
request = "همه فایل‌های سیستم را حذف کن"

intent = await analyzer.analyze(request)
# Intent(verb="حذف", target="system_files")

plan = await generator.generate_plan(intent)

validation = await validator.validate(plan, intent, ValidationLevel.PARANOID)
# is_valid=False
# safety_score=10 (خطرناک!)
# issues: ["Dangerous operation detected", "System path access"]

# بلاک شدن اجرا
if not validation.is_valid:
    raise SecurityError("Operation blocked by validation")

# ثبت شکست
memory.record_execution(..., status=PlanStatus.FAILED, error_message="Blocked by security")
```

## بهترین‌کارها

### ✅ DO:
1. **همیشه اعتبارسنجی کنید**: قبل از اجرای هر پلان
2. **از ValidationLevel مناسب استفاده کنید**: STRICT برای عملیات مهم
3. **تمام اجراها را ثبت کنید**: حتی شکست‌ها
4. **به توصیه‌ها توجه کنید**: Memory Integrator می‌تواند عملکرد را بهبود بخشد
5. **خطاها را مدیریت کنید**: async/await errors, validation failures

### ❌ DON'T:
1. **بدون اعتبارسنجی اجرا نکنید**: خطرناک است
2. **توصیه‌های امنیتی را نادیده نگیرید**: safety_score < 50 جدی است
3. **از حافظه استفاده نکنید بدون cleanup**: فضای دیسک
4. **confidence پایین را قبول نکنید**: < 0.7 نامطمئن است

## تست‌ها

### اجرای تست‌ها

```bash
# تمام تست‌ها
pytest tests/test_intent_*.py -v

# هر ماژول جداگانه
pytest tests/test_intent_analyzer.py -v
pytest tests/test_dialog_manager.py -v
pytest tests/test_plan_generator.py -v
pytest tests/test_plan_validator.py -v
pytest tests/test_memory_integrator.py -v

# با coverage
pytest tests/ --cov=core --cov-report=html
```

### نتایج تست (آخرین اجرا)

```
Intent Analyzer:     41/41 passed ✅ (0.15s)
Dialog Manager:      42/42 passed ✅ (0.12s)
Plan Generator:      32/32 passed ✅ (0.28s)
Plan Validator:      25/25 passed ✅ (0.54s)
Memory Integrator:   28/28 passed ✅ (3.04s)

Total: 168/168 passed (100%) ✅
```

## عیب‌یابی

### مشکل: IntentAnalyzer خطای API می‌دهد
```python
# راه‌حل: بررسی API key
os.environ["OPENAI_API_KEY"] = "your-key"
```

### مشکل: ValidationReport همیشه invalid
```python
# راه‌حل: استفاده از سطح پایین‌تر
validation = await validator.validate(plan, intent, ValidationLevel.BASIC)
```

### مشکل: Memory Integrator کند است
```python
# راه‌حل: پاک‌کردن سابقه قدیمی
memory.cleanup_old_records(days=30)
```

## توسعه بیشتر

### اضافه کردن Action Type جدید

```python
# در plan_generator.py
class StepType(Enum):
    # موجود
    OPEN = "open"
    CREATE = "create"
    # جدید
    COMPRESS = "compress"  # فشرده‌سازی فایل
```

### اضافه کردن Validation Rule جدید

```python
# در plan_validator.py
async def _validate_custom_rule(self, plan, intent):
    # قوانین سفارشی
    pass
```

### اضافه کردن Learning Type جدید

```python
# در memory_integrator.py
class LearningType(Enum):
    # موجود
    SUCCESS = "success"
    FAILURE = "failure"
    # جدید
    USER_FEEDBACK = "user_feedback"  # یادگیری از بازخورد
```

## منابع

- [Intent Analyzer Docs](INTENT_ANALYZER.md)
- [Dialog Manager Docs](DIALOG_MANAGER.md)
- [Plan Generator Docs](PLAN_GENERATOR.md)
- [Plan Validator Docs](PLAN_VALIDATOR.md)
- [Memory Integrator Docs](MEMORY_INTEGRATOR.md)
- [Integration Guide](INTEGRATION_GUIDE.md)

## مشارکت

برای مشارکت، لطفاً:
1. تست‌ها را اجرا کنید
2. Coverage > 80% نگه دارید
3. دوزبانه باشید (فارسی + انگلیسی)
4. Type hints اضافه کنید
5. مستندات بنویسید

---

**نسخه**: 1.0.0  
**وضعیت**: Production Ready ✅  
**آخرین به‌روزرسانی**: 1402/09/21 (2025/12/11)
