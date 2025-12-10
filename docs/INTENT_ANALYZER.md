<div dir="rtl">

# 🧠 Intent Analyzer - راهنمای کامل

**تشخیص هدف و نیت کاربر از درخواست‌های طبیعی**

---

## 📖 معرفی

**Intent Analyzer** اولین و مهم‌ترین ماژول در **Intent Planning System** است.

وظیفه آن:
1. درخواست درخواست‌های کاربر را به صورت طبیعی دریافت کند
2. **Intent** (نیت/هدف) اصلی کاربر را شناسایی کند
3. پارامترهای مربوطه را استخراج کند
4. موارد نامشخص و نیازمند سؤال را شناسایی کند
5. اطمینان تشخیص را محاسبه کند

### مثال:

```python
>>> analyzer = IntentAnalyzer()
>>> result = await analyzer.analyze("بازی کن تا برگردم")

# نتیجه:
# Intent(
#   verb="بازی",
#   target="game",
#   parameters={"duration": "until_return"},
#   confidence=0.92
# )

# سؤالات مورد نیاز:
# missing_fields=["game_type"]  # کدام بازی؟
```

---

## 🎯 کاربردها

### ✅ کاربردهای اصلی

```python
# 1. بازی کردن
"بازی کن تا برگردم"
→ Intent: play game (until_return)

# 2. ایجاد فولدر
"در E: فولدر MyDocs بساز"
→ Intent: create folder (path=E:, name=MyDocs)

# 3. دریافت داده
"دیتای هوای تهران رو بگیر و Excel ذخیره کن"
→ Intent: get weather data (city=tehran, save_to=excel)

# 4. کارهای سیستمی
"CPU چقدره؟"
→ Intent: check system (resource=cpu)

# 5. کنترل برنامه
"نوت‌پد باز کن و متن این فایل رو بخون"
→ Intent: open notepad + read file
```

---

## 🏗️ معماری و جریان داده

### نمودار جریان:

```
Input (درخواست طبیعی)
    │
    ▼
┌─────────────────────────────┐
│ تشخیص زبان (Language)      │
│ "بازی کن" → "fa"            │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ استخراج فعل (Verb)         │
│ "بازی کن" → "بازی"          │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ استخراج هدف (Target)       │
│ "بازی کن" → "game"          │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ استخراج پارامترها          │
│ → {"duration": "..."}       │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ شناسایی محدودیت‌ها         │
│ → ["safe_mode", ...]        │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ محاسبه اطمینان              │
│ → 0.92 (92%)                │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ شناسایی موارد نامشخص        │
│ → ["game_type"]             │
└─────────────────────────────┘
    │
    ▼
Output (IntentAnalysisResult)
```

---

## 💻 نحوه استفاده

### ۱. نصب و راه‌اندازی

```python
from core.intent_analyzer import IntentAnalyzer

# ایجاد نمونه
analyzer = IntentAnalyzer()

# یا با AI Brain مخصوص
from core.ai_brain import AIBrain
ai = AIBrain()
analyzer = IntentAnalyzer(ai_brain=ai)
```

### ۲. تحلیل درخواست ساده

```python
import asyncio

async def main():
    analyzer = IntentAnalyzer()
    
    # تحلیل
    result = await analyzer.analyze("نوت‌پد باز کن")
    
    # دسترسی به نتایج
    print(f"فعل: {result.intent.verb}")           # "باز"
    print(f"هدف: {result.intent.target}")         # "notepad"
    print(f"اطمینان: {result.intent.confidence}") # 0.92
    
    if result.requires_clarification:
        print(f"سوالات: {result.missing_fields}")

asyncio.run(main())
```

### ۳. تحلیل با پارامترها

```python
result = await analyzer.analyze(
    "در E: فولدر MyDocs بساز"
)

intent = result.intent
print(intent.verb)           # "ایجاد"
print(intent.target)         # "folder"
print(intent.parameters)     # {"path": "E:", "name": "MyDocs"}
```

### ۴. بررسی اطمینان

```python
result = await analyzer.analyze("do something")

if result.intent.is_confident(threshold=0.70):
    print("✅ اطمینان کافی - می‌تونم اجرا کنم")
else:
    print("❓ نیاز به توضیح بیشتر")
    print(f"سوالات: {result.missing_fields}")
```

### ۵. تحلیل دسته‌ای

```python
requests = [
    "نوت‌پد باز کن",
    "بازی کن",
    "CPU چقدره؟",
    "E: فولدر بساز"
]

results = await analyzer.analyze_batch(requests)

for req, result in zip(requests, results):
    print(f"{req}")
    print(f"  → {result.intent.verb} {result.intent.target}")
```

---

## 📊 ساختار داده‌ها

### Intent کلاس

```python
@dataclass
class Intent:
    verb: str                       # فعل اصلی
    target: str                     # هدف
    parameters: Dict[str, Any]      # پارامترهای تفصیلی
    constraints: List[str]          # محدودیت‌ها
    confidence: float               # اطمینان (0.0 - 1.0)
    raw_request: str                # درخواست اصلی
    language: str                   # زبان (en/fa)
```

#### متودهای Intent

```python
intent.is_confident(threshold=0.70)
# بررسی اطمینان بیش از حد (پیش‌فرض: 70%)
# Returns: bool
```

### IntentAnalysisResult کلاس

```python
@dataclass
class IntentAnalysisResult:
    intent: Intent                  # Intent تشخیص‌ داده شده
    missing_fields: List[str]       # فیلدهای نامشخص
    suggestions: List[str]          # پیشنهادهای سیستم
    requires_clarification: bool    # آیا نیاز به سؤال است
```

---

## 🔍 توضیح دقیق هر مرحله

### ۱. تشخیص زبان (Language Detection)

```python
result = await analyzer._detect_language("نوت‌پد باز کن")
# Returns: "fa" (فارسی)

result = await analyzer._detect_language("open notepad")
# Returns: "en" (انگلیسی)
```

**الگوریتم:**
- شمارش حروف فارسی و انگلیسی
- اگر بیش از 60% فارسی باشد → "fa"
- در غیر این‌صورت → "en"

### ۲. استخراج فعل (Verb Extraction)

**مرحله ۱: جستجو در known_verbs**
```python
known_verbs = {
    "باز": ["باز", "اجرا", "شروع"],
    "بازی": ["بازی", "شروع", "آغاز"],
    "ایجاد": ["ایجاد", "ساخت", "درست"],
    "حذف": ["حذف", "پاک"],
}
```

**مرحله ۲: اگر یافت نشد، از AI استفاده کن**
```
Prompt: "فعل اصلی درخواست '{request}' چیست؟"
Response: verb
Confidence: 0.70
```

### ۳. استخراج هدف (Target Extraction)

**Targets معروف:**
```python
common_targets = {
    "notepad": ["notepad", "نوت‌پد"],
    "steam": ["steam", "استیم"],
    "game": ["game", "بازی"],
    "folder": ["folder", "پوشه"],
    "file": ["file", "فایل"],
    "browser": ["browser", "مرورگر"],
}
```

### ۴. استخراج پارامترها (Parameter Extraction)

```python
# مثال ۱: مدت زمان
request = "بازی کن تا برگردم"
→ parameters = {"duration": "until_return"}

# مثال ۲: نام
request = 'create folder named "MyDocs"'
→ parameters = {"name": "MyDocs"}

# مثال ۳: مسیر
request = "create folder in E:\\"
→ parameters = {"path": "E:\\"}
```

### ۵. شناسایی محدودیت‌ها (Constraint Detection)

```python
request = "open notepad in safe mode"
→ constraints = ["safe_mode"]

request = "play with minimal cpu"
→ constraints = ["minimal_cpu"]

request = "run silently"
→ constraints = ["no_sound"]
```

### ۶. محاسبه اطمینان (Confidence Calculation)

**فرمول:**
```
confidence = 
    (verb_confidence + target_confidence) / 2 +  # بنیاد
    clarity_boost (تا 10%) +                     # بر اساس تعداد کلمات
    parameter_boost (تا 15%)                     # بر اساس تعداد پارامترها
    
    Maximum: 1.0
```

**مثال:**
```python
verb_conf = 0.90
target_conf = 0.85
param_count = 1
word_count = 4

confidence = (0.90 + 0.85) / 2 + 0.04 + 0.05 = 0.935
```

### ۷. شناسایی موارد نامشخص (Missing Fields)

```python
# مثال ۱: نوع بازی نامشخص
request = "بازی کن"
→ missing_fields = ["game_type"]

# مثال ۲: نام فولدر نامشخص
request = "فولدر بساز"
→ missing_fields = ["name"]

# مثال ۳: مسیر نامشخص
request = "فایل ذخیره کن"
→ missing_fields = ["path", "name"]
```

---

## 🧪 تست‌ها

### اجرای تست‌ها

```bash
# اجرای تمام تست‌ها
pytest tests/test_intent_analyzer.py -v

# اجرای تست خاص
pytest tests/test_intent_analyzer.py::TestVerbExtraction -v

# با coverage
pytest tests/test_intent_analyzer.py --cov=core.intent_analyzer
```

### گروه‌های تست

| گروه | توضیح | تعداد تست |
|---|---|---|
| **TestVerbExtraction** | استخراج فعل | 4 |
| **TestTargetExtraction** | استخراج هدف | 4 |
| **TestParameterExtraction** | استخراج پارامترها | 4 |
| **TestLanguageDetection** | تشخیص زبان | 3 |
| **TestConstraintDetection** | شناسایی محدودیت‌ها | 4 |
| **TestConfidence** | محاسبه اطمینان | 4 |
| **TestMissingFields** | شناسایی موارد نامشخص | 3 |
| **TestRealWorldExamples** | مثال‌های واقعی | 5 |
| **TestEdgeCases** | موارد خاص | 5 |
| **TestBatchProcessing** | پردازش دسته‌ای | 2 |
| **TestPerformance** | عملکرد | 2 |
| **TestHelperMethods** | متودهای کمکی | 1 |
| **Total** | | **41 تست** |

### مثال‌های تست

```python
# تست ۱: فعل انگلیسی
@pytest.mark.asyncio
async def test_simple_verb_english(analyzer):
    result = await analyzer.analyze("open notepad")
    assert result.intent.verb == "open"

# تست ۲: فعل فارسی
@pytest.mark.asyncio
async def test_simple_verb_persian(analyzer):
    result = await analyzer.analyze("نوت‌پد باز کن")
    assert result.intent.verb == "باز"

# تست ۳: دسته‌ای
@pytest.mark.asyncio
async def test_batch_analysis(analyzer):
    requests = ["open notepad", "نوت‌پد باز کن"]
    results = await analyzer.analyze_batch(requests)
    assert len(results) == 2
```

---

## 🎯 بهترین روش‌های استفاده

### ✅ درست

```python
# ۱. بررسی اطمینان قبل از اجرا
result = await analyzer.analyze(request)
if result.intent.is_confident(threshold=0.70):
    execute(result.intent)
else:
    ask_user_for_clarification(result.missing_fields)

# ۲. استفاده از context برای بهتر شدن نتایج
context = {"last_game": "counter-strike", "preferred_path": "E:"}
result = await analyzer.analyze(request, context)

# ۳. مدیریت exception‌ها
try:
    result = await analyzer.analyze(request)
except ValueError as e:
    print(f"درخواست نامعتبر: {e}")
```

### ❌ غلط

```python
# ۱. نپذیری exception‌ها
result = await analyzer.analyze(request)  # ممکن است fail کند

# ۲. فرض کردن اطمینان بالا
result = await analyzer.analyze("do something")
execute(result.intent)  # ممکن است اشتباه باشد

# ۳. نادیده گرفتن موارد نامشخص
if result.requires_clarification:
    # باید سؤال کنی!
    pass
```

---

## 📈 عملکرد

### سرعت

- **تحلیل ساده**: ~0.1-0.3 ثانیه (با known words)
- **تحلیل با AI**: ~0.5-2 ثانیه (با API call)
- **دسته‌ای (10 درخواست)**: ~3-5 ثانیه

### دقت

| موقعیت | دقت |
|---|---|
| **Verb شناخته شده** | 95%+ |
| **Target شناخته شده** | 90%+ |
| **پارامترها** | 85%+ |
| **زبان** | 98%+ |
| **موارد نامشخص** | 80%+ |

### مثال‌های اطمینان

```
"نوت‌پد باز کن"            → 0.95 (بسیار بالا)
"بازی کن"                 → 0.80 (بالا)
"فایل MyDocs.txt بخون"   → 0.75 (متوسط)
"کاری کن"                 → 0.50 (پایین)
"xyz abc"                 → 0.30 (خیلی پایین)
```

---

## 🔗 ارتباط با سایر ماژول‌ها

```
IntentAnalyzer
    │
    ├─ Output → Dialog Manager
    │         (موارد نامشخص)
    │
    ├─ Output → Plan Generator
    │         (Intent کامل)
    │
    └─ Uses → AI Brain
             (برای فعل/هدف نامشناخته)
```

---

## 🚀 نکات اضافی

### Bilingual Support

```python
# انگلیسی
result = await analyzer.analyze("open steam")
# فارسی
result = await analyzer.analyze("استیم باز کن")
# مختلط
result = await analyzer.analyze("notepad را باز کن")
```

### Context Awareness

```python
context = {
    "last_game": "counter-strike",
    "last_folder": "E:\\MyDocs",
    "user_preferences": {"default_app": "notepad"}
}
result = await analyzer.analyze("بازی کن", context)
```

### Extensibility

```python
# افزودن فعل جدید
analyzer.known_verbs["pause"] = ["pause", "متوقف", "توقف"]

# افزودن هدف جدید
analyzer.known_targets["discord"] = ["discord", "دیسکورد"]
```

---

## 📚 منابع و مثال‌های بیشتر

برای مثال‌های بیشتر، ببینید:
- `examples/intent_analyzer_demo.py`
- `tests/test_intent_analyzer.py`
- `docs/INTENT_SYSTEM_PLAN.md`

</div>
