# Memory Integrator - یکپارچه‌کننده حافظه

**بخش ۵ از Intent Planning System**

## خلاصه اجمالی

Memory Integrator نظام یادگیری و بهینه‌سازی برای سیستم است. این ماژول:

- 📊 **ثبت اجرا**: تمام جزئیات اجرای پلان‌ها را ذخیره می‌کند
- 📈 **یادگیری**: از موفقیت‌ها و شکست‌ها درس می‌گیرد
- 🎯 **تشخیص الگو**: الگوهای تکراری را شناخت می‌کند
- 💡 **بهینه‌سازی**: پیشنهادات بهبود می‌دهد
- 🔍 **جستجو**: پلان‌های مشابه از سابقه را می‌یابد

## معماری

```
اجرای پلان
    ↓
record_execution()
    ↓
محاسبه Performance Score
    ↓
ذخیره در SQLite
    ↓
learn_from_execution()
    ├─→ _learn_from_success() / _learn_from_failure()
    ├─→ _identify_patterns()
    └─→ _generate_optimizations()
    ↓
توصیه‌های آینده
```

## ساختار داده‌ها

### PlanStatus Enum
```python
SUCCESSFUL = "successful"      # موفق
FAILED = "failed"              # ناموفق
PARTIAL = "partial"            # جزئی
CANCELLED = "cancelled"        # لغو شده
TIMEOUT = "timeout"            # Timeout
UNKNOWN = "unknown"            # نامشخص
```

### LearningType Enum
```python
SUCCESS = "success"           # یادگیری از موفقیت
FAILURE = "failure"           # یادگیری از شکست
PATTERN = "pattern"           # شناسایی الگو
OPTIMIZATION = "optimization" # پیشنهاد بهینه‌سازی
```

### ExecutionHistory
```python
@dataclass
class ExecutionHistory:
    plan_id: str
    intent_hash: str
    start_time: datetime
    end_time: datetime
    status: PlanStatus
    steps_succeeded: int
    steps_failed: int
    total_steps: int
    actual_time_seconds: float
    estimated_time_seconds: float
    performance_score: float = 0.0
    error_message: Optional[str] = None
    feedback: str = ""
```

### OptimizationSuggestion
```python
@dataclass
class OptimizationSuggestion:
    suggestion_type: str  # "reduce_timeout", "increase_parallelization", "reduce_retries"
    description_fa: str
    description_en: str
    affected_steps: List[str]
    confidence: float  # 0-1
    estimated_improvement: float  # درصد بهبود
```

## Schema دیتابیس

### جدول `execution_history`
```sql
CREATE TABLE execution_history (
    id INTEGER PRIMARY KEY,
    plan_id TEXT,
    intent_hash TEXT,
    start_time TEXT,
    end_time TEXT,
    status TEXT,
    steps_succeeded INTEGER,
    steps_failed INTEGER,
    total_steps INTEGER,
    actual_time_seconds REAL,
    estimated_time_seconds REAL,
    performance_score REAL,
    error_message TEXT,
    feedback TEXT,
    created_at TEXT
)
```

### جدول `learned_patterns`
```sql
CREATE TABLE learned_patterns (
    id INTEGER PRIMARY KEY,
    pattern_hash TEXT UNIQUE,
    step_sequence TEXT,
    success_count INTEGER,
    total_count INTEGER,
    success_rate REAL,
    avg_execution_time REAL,
    created_at TEXT,
    last_used TEXT
)
```

### جدول `optimizations`
```sql
CREATE TABLE optimizations (
    id INTEGER PRIMARY KEY,
    plan_id TEXT,
    suggestion_type TEXT,
    description_fa TEXT,
    description_en TEXT,
    affected_steps TEXT,
    confidence REAL,
    estimated_improvement REAL,
    applied INTEGER,
    created_at TEXT
)
```

## متدهای اصلی

### `record_execution()`
```python
def record_execution(
    plan_id: str,
    intent: Intent,
    status: PlanStatus,
    steps_succeeded: int,
    steps_failed: int,
    total_steps: int,
    actual_time_seconds: float,
    estimated_time_seconds: float,
    error_message: Optional[str] = None,
    feedback: str = ""
) -> str:
    """
    ثبت اجرای پلان
    
    خروجی: ID ثبت (UUID)
    """
```

**محاسبه Performance Score:**
```
score = ((steps_succeeded / total_steps) * 50 +
         (min(actual_time, estimated_time) / max(actual_time, estimated_time)) * 50)
```

### `learn_from_execution()`
```python
async def learn_from_execution(
    history: ExecutionHistory,
    plan: ExecutionPlan,
    validation_report: ValidationReport
) -> List[LearningType]:
    """
    یادگیری از اجرای پلان
    
    مراحل:
    1. اگر موفق بود: _learn_from_success()
    2. اگر ناموفق بود: _learn_from_failure()
    3. شناسایی الگوها: _identify_patterns()
    4. تولید پیشنهادات: _generate_optimizations()
    
    خروجی: لیست نوع‌های یادگیری
    """
```

### `find_similar_plans()`
```python
def find_similar_plans(
    intent: Intent,
    threshold: float = 0.7
) -> List[Dict]:
    """
    پیدا کردن پلان‌های مشابه
    
    پارامترها:
    - intent: Intent برای جستجو
    - threshold: حداقل شباهت (0-1)
    
    خروجی: لیست پلان‌های مشابه با metadata
    """
```

### `get_statistics()`
```python
def get_statistics() -> Dict:
    """
    دریافت آمار کلی
    
    خروجی:
    {
        'total_executions': int,
        'successful': int,
        'failed': int,
        'success_rate': float,
        'avg_performance_score': float,
        'patterns_learned': int,
        'optimizations_suggested': int
    }
    """
```

### `get_recommendations()`
```python
def get_recommendations(intent: Intent) -> Dict:
    """
    دریافت توصیه‌ها برای intent جدید
    
    خروجی:
    {
        'similar_plans': int,
        'best_plan': Optional[Dict],
        'avg_execution_time': float,
        'success_rate': float,
        'optimizations': List[OptimizationSuggestion]
    }
    """
```

## مثال‌های کاربرد

### مثال ۱: ثبت و یادگیری
```python
from core.memory_integrator import MemoryIntegrator, PlanStatus
from core.intent_analyzer import Intent
from core.plan_generator import ExecutionPlan
from core.plan_validator import ValidationReport

memory = MemoryIntegrator("data/memories.sqlite3")

# ثبت اجرای موفق
record_id = memory.record_execution(
    plan_id="play_game_001",
    intent=Intent(verb="بازی", target="game", ...),
    status=PlanStatus.SUCCESSFUL,
    steps_succeeded=5,
    steps_failed=0,
    total_steps=5,
    actual_time_seconds=28.5,
    estimated_time_seconds=30.0,
    feedback="عالی! بازی شروع شد"
)

# یادگیری
history = ExecutionHistory(...)
learned = memory.learn_from_execution(history, plan, report)
print(f"یادگیری: {learned}")
# خروجی: ['success', 'pattern', 'optimization']
```

### مثال ۲: جستجوی پلان‌های مشابه
```python
# Intent برای جستجو
new_intent = Intent(verb="بازی", target="game", ...)

# پیدا کردن مشابه‌ها
similar = memory.find_similar_plans(new_intent, threshold=0.75)

print(f"تعداد پلان‌های مشابه: {len(similar)}")
for plan in similar:
    print(f"- {plan['plan_id']}: {plan['success_rate']}% موفق")
```

### مثال ۳: دریافت توصیه‌ها
```python
# توصیه‌ها برای Intent جدید
recommendations = memory.get_recommendations(new_intent)

print(f"بهترین پلان قبلی: {recommendations['best_plan']['plan_id']}")
print(f"نرخ موفقیت: {recommendations['success_rate']}%")
print(f"میانگین زمان: {recommendations['avg_execution_time']}s")

for opt in recommendations['optimizations']:
    print(f"💡 {opt.description_fa} ({opt.confidence*100:.0f}%)")
```

### مثال ۴: آمارها
```python
stats = memory.get_statistics()

print(f"تعداد کل اجراها: {stats['total_executions']}")
print(f"موفق: {stats['successful']}/{stats['total_executions']}")
print(f"نرخ موفقیت: {stats['success_rate']}%")
print(f"میانگین امتیاز: {stats['avg_performance_score']:.1f}/100")
print(f"الگوهای شناخت‌شده: {stats['patterns_learned']}")
```

## الگوریتم‌های اصلی

### شناسایی الگو
```python
def _identify_patterns(self, history: ExecutionHistory, plan: ExecutionPlan):
    # 1. ایجاد MD5 hash از دنباله مراحل
    step_sequence = "|".join([s.step_id for s in plan.steps])
    pattern_hash = hashlib.md5(step_sequence.encode()).hexdigest()
    
    # 2. جستجو در دیتابیس
    # 3. اپدیت success_rate
    # 4. ذخیره الگوی جدید
```

### تولید بهینه‌سازی
```python
# نوع ۱: کاهش Timeout
if actual_time < estimated_time * 0.7:
    # پیشنهاد کاهش timeout
    
# نوع ۲: Parallelization
if percentage_independent_steps > 50:
    # پیشنهاد parallelization
    
# نوع ۳: کاهش Retries
if step.retries > 3 and success_rate > 90:
    # پیشنهاد کاهش تعداد retry
```

## تست‌ها

۲۸ تست جامع:

| دسته | تعداد | توضیح |
|------|-------|-------|
| TestExecutionRecording | 3 | ثبت موفق/ناموفق، امتیاز |
| TestLearning | 3 | یادگیری، الگو‌ها |
| TestSimilaritySearch | 2 | جستجوی مشابه |
| TestOptimization | 2 | بهینه‌سازی |
| TestStatistics | 3 | آمار و شاخص‌ها |
| TestCleanup | 1 | پاک‌کردن سابقه قدیمی |
| TestRecommendations | 2 | توصیه‌ها |
| TestIntentHash | 2 | Hash Intent |
| TestDataPersistence | 1 | ماندگاری داده‌ها |
| TestPerformance | 2 | سرعت عملکرد |
| TestPlanStatusProcessing | 3 | وضعیت‌های مختلف |
| TestErrorHandling | 2 | مدیریت خطا |
| TestConcurrency | 2 | همزمانی |

**نتیجه: ۲۸/۲۸ تست پاس ✅**

## بهترین‌کارها

### ✅ DO:
- **ثبت تمام اجراها**: حتی شکست‌ها برای یادگیری
- **بازخورد منظم**: شامل feedback کاربر
- **تحلیل شکست‌ها**: برای بهبود آینده
- **استفاده از توصیه‌ها**: برای بهینه‌سازی
- **پاک‌کردن دوره‌ای**: مدیریت فضای دیتابیس

### ❌ DON'T:
- **نادیده‌گرفتن خطاها**: همه اجراها مهم هستند
- **بی‌فکر بهینه‌سازی**: بر اساس توصیه‌ها
- **حفظ سابقه‌های قدیمی**: پاک‌کردی منظم ضروری
- **ایجاد patterns با داده‌های کم**: حداقل ۵ اجرا

## ادغام با دیگر ماژول‌ها

```
Intent Analyzer
    ↓
Dialog Manager
    ↓
Plan Generator
    ↓
Plan Validator ──→ ValidationReport
    ↓               ↓
ExecutionPlan  Memory Integrator
                    ↓
            Recommendations & Stats
```

## عملکرد

| عملیات | سرعت | بارند‌اشت |
|--------|------|-----------|
| ثبت اجرا | < 10ms | ۱ بار/اجرا |
| دریافت آمار | < 50ms | دستی/خودکار |
| جستجوی مشابه | < 100ms | بر حسب تعداد |
| یادگیری | < 200ms | بعد از اجرا |

## نکات نمایندگی

- **بیلنگوال**: 100% فارسی و انگلیسی
- **Type Hints**: تمام پارامترها و خروجی‌ها
- **Async Ready**: آماده برای async operations
- **Database**: SQLite برای تک‌نشستی
- **Logging**: تمام فعالیت‌های مهم ثبت‌شده

## مرجع سریع

```python
# اولیه‌سازی
memory = MemoryIntegrator("data/memories.sqlite3")

# ثبت
record_id = memory.record_execution(...)

# یادگیری
learned = memory.learn_from_execution(history, plan, report)

# جستجو
similar = memory.find_similar_plans(intent, threshold=0.7)

# آمار
stats = memory.get_statistics()

# توصیه‌ها
recommendations = memory.get_recommendations(intent)

# پاک‌کردن
deleted = memory.cleanup_old_records(days=30)
```

---

**نسخه**: 1.0.0  
**وضعیت**: Production Ready ✅  
**آخرین به‌روزرسانی**: 1402/10/15
