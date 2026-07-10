# Phase 8 — Error Resilience & Failover Optimization Report

**تاریخ**: 2026-07-10
**وضعیت**: 🔄 در حال انجام
**نسخه**: 0.9.0 → 1.0.0

---

## خلاصه اجرایی

تحلیل `test_log.log` نشان‌دهنده شکست کامل زنجیره failover مدل‌ها در سناریوهای واقعی است. این فاز مشکلات زیر را هدف قرار می‌دهد:

1. **شکست 100% زنجیره Failover**: تمام 11 مدل موجود شکست خوردند
2. **ورودی نامعتبر کاربر**: کاراکتر backslash در ورودی باعث خطا می‌شود
3. **عدم نمایش وضعیت ارائه‌دهندگان**: کاربر نمی‌داند کدام ارائه‌دهنده فعال است

---

## تحلیل مشکلات از test_log.log

### 1. شکست مدل‌های OpenRouter (6 مدل — 403 Forbidden)

| مدل | خطا | تعداد تلاش |
|-----|------|-----------|
| tencent/hy3:free | TimeoutError + 403 | 3 |
| nvidia/nemotron-3-ultra-550b-a55b:free | 403 Forbidden | 3 |
| poolside/laguna-m.1:free | 403 Forbidden | 3 |
| google/gemma-4-31b-it:free | 403 Forbidden | 3 |
| cohere/north-mini-code:free | 403 Forbidden | 3 |
| openrouter/free | 403 Forbidden | 3 |

**Root Cause**: مدل‌های free OpenRouter ممکن است محدودیت دسترسی منطقه‌ای یا سیاست امنیتی داشته باشند.

### 2. ارائه‌دهندگان غیرفعال (5 ارائه‌دهنده)

| ارائه‌دهنده | متغیر محیطی | وضعیت |
|------------|------------|-------|
| Google | GOOGLE_API_KEY | ❌ تنظیم نشده |
| Groq | GROQ_API_KEY | ❌ تنظیم نشده |
| Huggingface | HUGGINGFACE_API_KEY | ❌ تنظیم نشده |
| Ollama | — | ❌ نصب نشده |
| OpenRouter | OPENROUTER_API_KEY | ⚠️ تنظیم شده ولی 403 |

### 3. خطای TimeoutError

خطای `TimeoutError` در مدل اول `tencent/hy3:free` نشان‌دهنده مشکل اتصال یا پاسخ‌گویی کند سرور است.

### 4. مشکل ورودی کاربر

ورودی `\What is my CPU usage right now?` با backslash شروع می‌شود که ممکن است در پردازش مشکل ایجاد کند.

---

## تغییرات اعمال شده

### 8.1 — Input Sanitization (main.py)

```python
# Phase 8: Input sanitization — strip leading backslashes and control chars
user_text = user_text.lstrip("\\").strip()
if not user_text:
    continue
```

**اثر**: ورودی‌هایی مانند `\What is my CPU?` به `What is my CPU?` تبدیل می‌شوند.

### 8.2 — دستور /providers (main.py)

دستور جدید `/providers` وضعیت تمام ارائه‌دهندگان API را نمایش می‌دهد:

```
> /providers

API Provider Status:
  ACTIVE         openrouter     (key: OPENROUTER_API_KEY)
  INACTIVE       google         (no key)
  INACTIVE       groq           (no key)
  INACTIVE       openai         (no key)
  INACTIVE       anthropic      (no key)
  INACTIVE       huggingface    (no key)

  1 active provider(s)
```

### 8.3 — Circuit Breaker (ai_brain.py) — در حال انجام

سازوکار circuit breaker برای جلوگیری از تلاش مجدد مدل‌های 403:

- پس از 2 بار شکست متوالی، مدل از لیست تلاش حذف می‌شود
- وضعیت مدل‌ها در حافظه cache می‌شود
- پس از 5 دقیقه، مجدد تلاش می‌شود

### 8.4 — Model Health Scoring (model_config.py) — در حال انجام

رتبه‌بندی مدل‌ها بر اساس تاریخچه موفقیت:

```python
@dataclass
class ModelHealth:
    name: str
    success_count: int = 0
    failure_count: int = 0
    last_failure_type: str = ""  # "403", "timeout", "error"
    last_success: float = 0.0
    is_circuit_open: bool = False
```

---

## معیارهای تکمیل

| معیار | وضعیت |
|-------|-------|
| ورودی backslash بدون خطا پردازش شود | ✅ تکمیل |
| دستور /providers کار کند | ✅ تکمیل |
| Circuit breaker برای مدل‌های 403 | 🔄 در حال انجام |
| Model health scoring | 🔄 در حال انجام |
| تست‌های Phase 8 عبور کنند | 🔄 در حال انجام |

---

## فایل‌های تغییر یافته

| فایل | تغییرات |
|------|---------|
| `main.py` | Input sanitization, `/providers` command, help text |
| `ROADMAP.md` | Phase 8-10 roadmap |
| `README.md` | Version 0.9.0 → 1.0.0, Phase 8-10 |

---

## فازهای بعدی

- **Phase 9**: بهینه‌سازی عملکرد و تجربه کاربری
- **Phase 10**: آماده‌سازی انتشار 1.0.0
