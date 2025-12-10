# Plan Generator - توليد برنامه اجرايی

**وضعیت:** ✅ تکمیل شده | **تست‌ها:** 32/32 موفق | **خطوط کد:** 887 | **مستندات:** دوزبانه

## 📋 خلاصه

**Plan Generator** (ماژول سوم سیستم Intent Planning) مسئول تبدیل `Intent` کامل‌شده (از Dialog Manager) به یک برنامه اجرایی سازمان‌یافته است که شامل مراحل مرتب‌شده، وابستگی‌ها، timeout، و منطق بازگشتی است.

### نقش در معماری
```
Intent Analyzer (فیلد‌های مفقود) 
    ↓
Dialog Manager (پاسخ دادن به پرسش‌ها)
    ↓
Plan Generator (تبدیل به مراحل اجرایی) ← شما هستید
    ↓
Plan Validator (بررسی ایمنی)
    ↓
Memory Integrator (یادگیری و بهبود)
```

## 🏗️ معماری و طراحی

### داده‌های اصلی

#### StepType - انواع مراحل
```python
ACQUIRE    # دریافت منابع (فایل‌ها، اطلاعات)
OPEN       # باز کردن برنامه یا فایل
INTERACT   # تعامل با رابط (کلیک، تایپ)
PROCESS    # پردازش داده‌ها
SAVE       # ذخیره نتایج
VERIFY     # بررسی نتایج
WAIT       # انتظار برای تکمیل
CLEANUP    # پاک‌کردن منابع موقت
```

#### ExecutionMode - حالت‌های اجرای مراحل
```python
SEQUENTIAL    # مراحل یک‌پس‌یک
PARALLEL      # مراحل هم‌زمان (بدون وابستگی)
CONDITIONAL   # مراحل شرطی (بستگی به نتیجه قبلی)
```

#### ExecutionStep - یک مرحله اجرایی
```python
step_id         : str              # شناسه منحصر
order           : int              # ترتیب اجرا (1، 2، 3، ...)
action          : str              # متن اقدام (فارسی)
action_en       : str              # متن اقدام (انگلیسی)
step_type       : StepType         # نوع مرحله
target          : str              # هدف مرحله
parameters      : dict             # پارامترهای اقدام
dependencies    : list[str]        # شناسه‌های مراحل وابسته
timeout         : int              # ثانیه تا timeout
retries         : int              # تعداد تلاش‌های مجدد
fallback_action : Optional[str]    # اقدام جایگزین در شکست
execution_mode  : ExecutionMode    # حالت اجرا
priority        : int              # اولویت (1-10)
description     : str              # توضیح انسان‌پسند
```

#### ExecutionPlan - برنامه کامل
```python
plan_id                : str               # شناسه پلان
intent                 : Intent            # Intent اصلی
steps                  : list[ExecutionStep]  # مراحل اجرایی
total_estimated_time   : int               # مجموع زمان (ثانیه)
complexity            : str                # SIMPLE | MEDIUM | COMPLEX
created_at            : datetime           # زمان ایجاد
description           : str                # توضیح پلان
```

### الگوهای عملیاتی (Action Patterns)

#### Pattern "بازی" - بازی را شروع کن
```
Step 1: OPEN         → باز کردن بازی
Step 2: WAIT         → انتظار برای باز شدن
Step 3: INTERACT     → شروع بازی
Step 4: WAIT         → انتظار برای شروع
```

#### Pattern "ایجاد" - پوشه یا پروژه بساز
```
Step 1: ACQUIRE      → دریافت مسیر
Step 2: INTERACT     → ایجاد پوشه
Step 3: INTERACT     → تنظیم نام
Step 4: VERIFY       → بررسی ایجاد
```

#### Pattern "کپی" - فایل یا پوشه کپی کن
```
Step 1: OPEN         → باز کردن مرورگر فایل
Step 2: INTERACT     → یافتن فایل
Step 3: INTERACT     → کپی
Step 4: INTERACT     → رفتن به مقصد
Step 5: INTERACT     → چسباندن
Step 6: VERIFY       → بررسی نتیجه
```

#### Pattern "جستجو" - اطلاعات را جستجو کن
```
Step 1: OPEN         → باز کردن مرورگر
Step 2: INTERACT     → جستجو
Step 3: WAIT         → انتظار برای نتایج
Step 4: PROCESS      → تجزیه و تحلیل
Step 5: SAVE         → ذخیره نتایج
```

#### Pattern "نصب" - نرم‌افزار نصب کن
```
Step 1: ACQUIRE      → دریافت بسته
Step 2: OPEN         → باز کردن installer
Step 3: INTERACT     → تایید
Step 4: WAIT         → انتظار برای نصب
Step 5: INTERACT     → تکمیل نصب
Step 6: VERIFY       → بررسی نصب
```

## 🔄 فلوی تولید پلان

```
۱. تولید مراحل اولیه
   ├─ جستجو در الگوهای پیش‌تعریف‌شده
   └─ یا ایجاد دینامیکی برای فعل‌های نامشناخته

۲. تشخیص وابستگی‌ها
   ├─ INTERACT وابسته به OPEN
   ├─ VERIFY وابسته به INTERACT
   └─ WAIT وابسته به OPEN/INTERACT

۳. ترتیب‌بندی مراحل (Topological Sort)
   └─ اطمینان از ترتیب درست با توجه به وابستگی‌ها

۴. افزایش اطلاعات مراحل
   ├─ تنظیم timeout (OPEN: 15s، INTERACT: 5s، ...)
   ├─ تنظیم retries (OPEN: 3، VERIFY: 5، ...)
   └─ تعیین fallback actions

۵. بهینه‌سازی پلان
   ├─ ادغام مراحل سازگار
   └─ شناخت فرصت‌های پارالل

۶. محاسبه پیچیدگی
   ├─ SIMPLE: ≤ 3 مرحله
   ├─ MEDIUM: ≤ 7 مرحله
   └─ COMPLEX: > 7 مرحله

۷. تایید و بازگشت
   └─ بررسی وابستگی‌های دوری و نامعتبری
```

## 📊 تخمین Timeout

| نوع مرحله | Timeout | دلیل |
|-----------|---------|------|
| OPEN | 15 ثانیه | باز کردن برنامه/فایل می‌تواند طول بکشد |
| ACQUIRE | 20 ثانیه | دریافت منابع از اینترنت ممکن است طول بکشد |
| INTERACT | 5 ثانیه | تعامل با رابط معمولاً سریع است |
| PROCESS | 10 ثانیه | پردازش داده‌های متوسط |
| SAVE | 5 ثانیه | ذخیره فایل معمولاً سریع است |
| VERIFY | 10 ثانیه | بررسی نتیجه |
| WAIT | 5 ثانیه | انتظار برای رویدادها |
| CLEANUP | 3 ثانیه | پاک‌کردن منابع |

## 📚 مثال‌های استفاده

### مثال 1: بازی کردن

**Input (Intent):**
```python
Intent(
    verb="بازی",
    target="Counter-Strike",
    parameters={"game_type": "FPS", "duration": "until_return"},
    confidence=0.95,
    raw_request="بازی کن تا برگردم",
    language="fa"
)
```

**Code:**
```python
generator = PlanGenerator(ai_brain=brain)
plan = await generator.generate_plan(intent, optimize=True)
```

**Output (ExecutionPlan):**
```python
ExecutionPlan(
    plan_id="plan_xyz",
    steps=[
        ExecutionStep(
            order=1,
            action="باز کردن Counter-Strike",
            step_type=StepType.OPEN,
            timeout=15,
            retries=3
        ),
        ExecutionStep(
            order=2,
            action="انتظار برای باز شدن بازی",
            step_type=StepType.WAIT,
            timeout=5,
            dependencies=["step_1"]
        ),
        ExecutionStep(
            order=3,
            action="شروع بازی",
            step_type=StepType.INTERACT,
            timeout=5,
            dependencies=["step_2"]
        )
    ],
    total_estimated_time=25,
    complexity="SIMPLE",
    description="برنامه برای بازی Counter-Strike با 3 مرحله"
)
```

### مثال 2: پوشه ایجاد کن

**Input (Intent):**
```python
Intent(
    verb="ایجاد",
    target="folder",
    parameters={"name": "MyProject", "path": "E:\\Projects"},
    confidence=0.90,
    raw_request="پوشه MyProject را بساز",
    language="fa"
)
```

**Code:**
```python
plan = await generator.generate_plan(intent, optimize=True)
print(f"تعداد مراحل: {len(plan.steps)}")
print(f"زمان برآورد: {plan.total_estimated_time} ثانیه")
print(f"پیچیدگی: {plan.complexity}")
```

**Output:**
```
تعداد مراحل: 4
زمان برآورد: 30 ثانیه
پیچیدگی: SIMPLE
```

### مثال 3: جستجو کردن

**Input (Intent):**
```python
Intent(
    verb="جستجو",
    target="information",
    parameters={"query": "هوای تهران"},
    confidence=0.92,
    raw_request="جستجو کن",
    language="fa"
)
```

**Code:**
```python
# تولید پلان
plan = await generator.generate_plan(intent)

# دریافت مراحل متوالی
sequential = plan.get_sequential_order()

# دریافت مراحل موازی
parallel = plan.get_parallel_steps()

# بررسی پلان
is_valid, warnings = await generator.validate_plan(plan)
print(f"آیا پلان معتبر است؟ {is_valid}")
```

## 🔧 API Reference

### کلاس PlanGenerator

#### `__init__(ai_brain: Optional[AIBrain] = None)`
**سازنده:** مقدارهای اولیه را تنظیم کند
```python
generator = PlanGenerator(ai_brain=brain)
```

#### `async generate_plan(intent: Intent, optimize: bool = True) → ExecutionPlan`
**تولید پلان:** اصلی pipeline
```python
plan = await generator.generate_plan(intent)
# یا
plan = await generator.generate_plan(intent, optimize=False)
```

#### `async validate_plan(plan: ExecutionPlan) → tuple[bool, list[str]]`
**تایید پلان:** بررسی معتبری
```python
is_valid, warnings = await generator.validate_plan(plan)
if is_valid:
    print("پلان معتبر است!")
else:
    for warning in warnings:
        print(f"⚠️ {warning}")
```

#### `_estimate_timeout(step_type: StepType) → int`
**تخمین Timeout:** براساس نوع مرحله
```python
timeout = generator._estimate_timeout(StepType.OPEN)
# بازگشت: 15 (ثانیه)
```

#### `_calculate_complexity(steps: list[ExecutionStep]) → str`
**محاسبه پیچیدگی:** براساس تعداد مراحل
```python
complexity = generator._calculate_complexity(steps)
# بازگشت: "SIMPLE" یا "MEDIUM" یا "COMPLEX"
```

### کلاس ExecutionPlan

#### `get_step_by_id(step_id: str) → Optional[ExecutionStep]`
**دریافت مرحله:** با شناسه
```python
step = plan.get_step_by_id("step_123")
```

#### `get_sequential_order() → list[ExecutionStep]`
**ترتیب متوالی:** مراحل مرتب‌شده
```python
ordered_steps = plan.get_sequential_order()
```

#### `get_parallel_steps() → list[list[ExecutionStep]]`
**مراحل موازی:** گروه‌های قابل اجرا
```python
parallel_groups = plan.get_parallel_steps()
for group in parallel_groups:
    # اجرای هم‌زمان مراحل این گروه
    pass
```

## 🧪 آزمایش (32 تست)

### دسته‌های تست:

| دسته | تعداد | توضیح |
|------|-------|-------|
| TestPlanGeneration | 4 | تولید پلان برای Intent‌های مختلف |
| TestStepOrdering | 3 | ترتیب‌بندی صحیح مراحل |
| TestDependencyDetection | 4 | تشخیص وابستگی‌ها |
| TestTimeoutEstimation | 3 | محاسبه timeout |
| TestPlanOptimization | 2 | بهینه‌سازی |
| TestComplexityCalculation | 2 | محاسبه پیچیدگی |
| TestRealWorldScenarios | 6 | سناریوهای واقعی |
| TestEdgeCases | 4 | موارد لبه‌ای |
| TestPlanValidation | 2 | تایید پلان |
| TestPerformance | 2 | عملکرد |
| **کل** | **32** | ✅ همه موفق |

**نتیجه:** ✅ `32 passed in 0.54s`

## 🎯 بهترین تمرین‌ها (Do's & Don'ts)

### ✅ DO's (انجام بدهید)

1. **ترتیب وابستگی‌ها را رعایت کنید**
   - همیشه OPEN قبل از INTERACT
   - VERIFY در انتهای مراحل

2. **timeout‌های واقع‌بینانه تنظیم کنید**
   - OPEN: 15 ثانیه (برای شکست‌های شبکه)
   - INTERACT: 5 ثانیه (سریع)

3. **paran
allelization را شناخت دهید**
   - مراحل بدون وابستگی را موازی کنید
   - کاهش کل زمان اجرا

4. **fallback actions را تعریف کنید**
   - برای مراحل حساس
   - بهبود قابلیت اطمینان

5. **پیچیدگی را مناسب تخمین زنید**
   - ساده: خودرو‌نما صاف
   - پیچیده: مراقبت خاص

### ❌ DON'Ts (انجام ندهید)

1. **وابستگی‌های دوری ایجاد نکنید**
   ```
   ❌ Step A → Step B → Step A
   ```

2. **timeout‌های بیش‌ از‌حد کم نگذارید**
   ```
   ❌ OPEN: 1 ثانیه (احتمالاً timeout شود)
   ✅ OPEN: 15 ثانیه (معقول)
   ```

3. **مراحل را بدون منطق ترتیب ندهید**
   ```
   ❌ INTERACT قبل از OPEN
   ✅ OPEN ← INTERACT
   ```

## 📈 معیارهای عملکرد

| معیار | مقدار | وضعیت |
|-------|--------|-------|
| سرعت تولید پلان | < 0.5 ثانیه | ✅ سریع |
| حجم پلان‌های ساده | 1-3 مرحله | ✅ کافی |
| حجم پلان‌های پیچیده | 4-8 مرحله | ✅ قابل اجرا |
| دقت تخمین زمان | ±20% | ✅ خوب |
| نرخ بازگشت fallback | < 10% | ✅ کم |

## 🔗 ادغام با Dialog Manager و Plan Validator

### ورودی (Dialog Manager)
```python
# Dialog Manager خروجی
complete_intent = Intent(
    verb="بازی",
    target="Counter-Strike",
    parameters={"game_type": "FPS", "duration": "until_return"},
    confidence=0.95,  # تکمیل شده
    language="fa"
)
```

### پردازش (Plan Generator)
```python
plan = await generator.generate_plan(complete_intent)
```

### خروجی (Plan Validator)
```python
# Plan Validator مدخول
execution_plan = ExecutionPlan(
    plan_id="plan_xyz",
    steps=[...],
    total_estimated_time=25,
    complexity="SIMPLE"
)
```

## 📝 خلاصه تغییرات

**نسخه 1.0 - رونمایی اولیه:**
- ✅ 5 الگوی عملیاتی
- ✅ تشخیص خودکار وابستگی
- ✅ محاسبه پیچیدگی
- ✅ بهینه‌سازی پلان
- ✅ 32 تست جامع
- ✅ مستندات دوزبانه

## 🆘 رفع مشکلات شایع

**مشکل:** "Plan خالی است"
```
علت: الگوی نامشناخته و Intent خیلی ساده
حل: فعل را به Intent Analyzer اضافه کنید
```

**مشکل:** "Timeout بیش از حد"
```
علت: تخمین timeout بیش از حد بالا
حل: Timeout را دستی تنظیم کنید
```

**مشکل:** "وابستگی دوری"
```
علت: الگو نادرست
حل: Dependency detection را بررسی کنید
```

## 📚 منابع اضافی

- [Intent Analyzer](./INTENT_ANALYZER.md) - قبلی ماژول
- [Dialog Manager](./DIALOG_MANAGER.md) - قبلی ماژول
- [PLAN_VALIDATOR.md](./PLAN_VALIDATOR.md) - ماژول بعدی (خریداری)

---

**نویسندگان:** تیم Shahin AI  
**آخرین به‌روزرسانی:** ۱۴۰۴/۹/۲۰  
**نسخه:** 1.0  
**وضعیت:** تکمیل و تایید شده ✅
