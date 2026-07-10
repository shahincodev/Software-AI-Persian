# ROADMAP.md — نقشه راه توسعه Software-AI

> **نکته مهم**: این فایل حافظه عملیاتی توسعه است. پس از هر فاز، وضعیت تکمیل اینجا ثبت می‌شود تا نیاز به خواندن Context از ابتدا نباشد.

---

## وضعیت فعلی

| آیتم | مقدار |
|------|-------|
| نسخه فعلی | 0.9.0 |
| نسخه هدف | 1.0.0 |
| فازهای تکمیل شده | Phase 1-7 |
| فاز جاری | Phase 8 |
| تاریخ آخرین به‌روزرسانی | 2026-07-10 |

---

## Phase 8 — تاب‌آوری خطا و بهینه‌سازی زنجیره Failover

**وضعیت**: 🔄 در حال انجام

**مشکل اصلی**: بر اساس `test_log.log`، زنجیره failover مدل‌ها کاملاً شکست می‌خورد:
- مدل‌های OpenRouter: خطای 403 "Access denied by security policy" (6 مدل)
- ارائه‌دهندگان غیرفعال: Google, Groq, Huggingface, Ollama (بدون API key)
- خطای TimeoutError در اولین مدل (tencent/hy3:free)
- **نتیجه نهایی**: "All 11 available models failed" پس از 3 تلاش

### زیرفازها

#### 8.1 — اصلاح ورودی کاربر (Input Sanitization)
- [x] حذف کاراکترهای اضافی از ورودی (backslash, special chars)
- [ ] اعتبارسنجی طول ورودی
- [ ] فیلتر کردن ورودی‌های خالی یا فقط فاصله
- **فایل‌ها**: `main.py` (agent_loop)
- **تست**: `tests/test_phase8_error_resilience.py`

#### 8.2 — بهینه‌سازی زنجیره Failover
- [x] اضافه کردن سازوکار "circuit breaker" برای مدل‌های 403
- [x] caching پاسخ‌های 403 برای جلوگیری از تلاش مجدد بی‌فایده
- [x] محدود کردن تعداد تلاش‌ها برای هر مدل خاص (نه فقط کل زنجیره)
- [x] بهبود پیام خطای کاربرپسند
- **فایل‌ها**: `core/ai_brain.py`, `core/model_config.py`

#### 8.3 — مدیریت هوشمند ارائه‌دهندگان
- [ ] بررسی اعتبار API key قبل از تلاش اتصال
- [ ] رتبه‌بندی مدل‌ها بر اساس تاریخچه موفقیت
- [ ] اضافه کردن مکانیزم "model health check" در ابتدا
- **فایل‌ها**: `core/ai_brain.py`, `core/model_orchestrator.py`

#### 8.4 — گزارش وضعیت ارائه‌دهندگان
- [x] نمایش لحظه‌ای وضعیت ارائه‌دهندگان در CLI
- [x] دستور `/providers` برای نمایش ارائه‌دهندگان فعال و غیرفعال
- **فایل‌ها**: `main.py`
- **تست**: `tests/test_phase8_error_resilience.py`

### فایل‌های تغییر یافته Phase 8
| فایل | تغییرات |
|------|---------|
| `main.py` | ✅ Input sanitization, ✅ `/providers` command with circuit breaker status |
| `core/ai_brain.py` | ✅ Circuit Breaker (ModelCircuitBreaker), integrated into ask_with_fallback |
| `core/model_config.py` | 🔄 Model health scoring, retry limits |
| `tests/test_phase8_error_resilience.py` | ✅ 39 تست (همه عبور) |
| `docs/PHASE8_ERROR_RESILIENCE_REPORT.md` | ✅ گزارش فاز |

### معیار تکمیل Phase 8
- [x] ورودی‌های خاص (backslash, empty) بدون خطا پردازش شوند
- [x] مدل‌های 403 بیش از یک بار تلاش نشوند
- [ ] پیام خطای کاربرپسند نمایش داده شود
- [x] دستور `/providers` کار کند
- [x] تست‌ها با موفقیت اجرا شوند (39/39)

---

## Phase 9 — بهینه‌سازی عملکرد و تجربه کاربری

**وضعیت**: 🔄 در حال انجام (9.1 ✅)

### زیرفازها

#### 9.1 — بهینه‌سازی حافظه و کش
- [x] پیاده‌سازی کش پاسخ‌های AI برای درخواست‌های تکراری
- [x] بهینه‌سازی حجم context (فشرده‌سازی system context)
- [x] محدود کردن اندازه conversation history بهینه
- **فایل‌ها**: `core/memory_integrator.py`, `core/ai_brain.py`

#### 9.2 — بهبود تجربه کاربری CLI
- [ ] نمایش پیشرفت درصدی برای عملیات طولانی
- [ ] رنگ‌بندی بهتر خروجی‌ها
- [ ] دستور `/status` برای نمایش وضعیت سیستم
- [ ] پشتیبانی از Tab completion برای دستورات
- **فایل‌ها**: `main.py`

#### 9.3 — تست‌های یکپارچه‌سازی
- [ ] تست خودکار زنجیره failover
- [ ] تست input sanitization
- [ ] تست /providers command
- [ ] تست memory context compression
- **فایل‌ها**: `tests/test_phase9_integration.py`

### معیار تکمیل Phase 9
- [ ] زمان پاسخ‌گویی برای درخواست‌های تکراری < 500ms
- [x] context size بهینه شده باشد
- [ ] CLI تجربه کاربری بهتری داشته باشد
- [ ] تست‌های یکپارچه‌سازی عبور کنند

---

## Phase 10 — آماده‌سازی انتشار 1.0.0

**وضعیت**: 📋 برنامه‌ریزی شده

### زیرفازها

#### 10.1 — مستندسازی نهایی
- [ ] به‌روزرسانی README.md با تمام قابلیت‌های Phase 8-9
- [ ] ایجاد CHANGELOG.md کامل
- [ ] به‌روزرسانی CONTRIBUTING.md
- [ ] بررسی تمام مستندات در docs/
- **فایل‌ها**: `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `docs/*`

#### 10.2 — تست نهایی و پاکسازی
- [ ] اجرای کامل تست‌ها
- [ ] بررسی lint و type hints
- [ ] پاکسازی فایل‌های اضافی
- [ ] به‌روزرسانی requirements.txt
- **فایل‌ها**: `requirements.txt`, `tests/*`

#### 10.3 — انتشار و برچسب‌گذاری
- [ ] تغییر نسخه به 1.0.0 در `main.py` و `README.md`
- [ ] ایجاد Git tag v1.0.0
- [ ] نوشتن release notes
- [ ] ایجاد GitHub Release
- **فایل‌ها**: `main.py`, `README.md`

### معیار تکمیل Phase 10
- [ ] نسخه 1.0.0 در تمام فایل‌ها یکسان باشد
- [ ] تمام تست‌ها عبور کنند
- [ ] مستندات کامل و به‌روز باشند
- [ ] Git tag ایجاد شده باشد

---

## ساختار فایل‌ها پس از هر فاز

```
پس از Phase 8:
├── ROADMAP.md                          ← این فایل (به‌روزرسانی وضعیت)
├── README.md                           ← نسخه 1.0.0
├── main.py                             ← Input sanitization + /providers
├── core/ai_brain.py                    ← Circuit breaker + model health
├── core/model_config.py                ← Health scoring
├── docs/PHASE8_ERROR_RESILIENCE_REPORT.md  ← گزارش فاز
└── tests/test_phase8_error_resilience.py   ← تست‌های جدید

پس از Phase 9:
├── core/memory_integrator.py           ← Context compression
├── docs/PHASE9_PERFORMANCE_REPORT.md   ← گزارش فاز
└── tests/test_phase9_integration.py    ← تست‌های یکپارچه‌سازی

پس از Phase 10:
├── CHANGELOG.md                        ← تاریخچه تغییرات
├── docs/PHASE10_RELEASE_REPORT.md      ← گزارش انتشار
└── Git tag: v1.0.0
```

---

## قوانین توسعه (غیرقابل تغییر)

1. **پس از هر فاز**: این فایل (ROADMAP.md) به‌روزرسانی شود
2. **پس از هر فاز**: گزارش در `docs/` ذخیره شود
3. **پس از هر فاز**: تست در `tests/` ایجاد شود
4. **پس از هر فاز**: commit و push انجام شود
5. **نسخه**: در `README.md` و `main.py` یکسان باشد
6. **تست‌ها**: قبل از commit اجرا شوند
