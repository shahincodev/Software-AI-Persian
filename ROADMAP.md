# ROADMAP.md — نقشه راه توسعه Software-AI

> **نکته مهم**: این فایل حافظه عملیاتی توسعه است. پس از هر فاز، وضعیت تکمیل اینجا ثبت می‌شود تا نیاز به خواندن Context از ابتدا نباشد.

---

## وضعیت فعلی

| آیتم | مقدار |
|------|-------|
| نسخه فعلی | 1.1.0 |
| نسخه هدف | 1.1.0 |
| فازهای تکمیل شده | Phase 1-11 ✅ |
| فاز جاری | — (تکمیل شده) |
| تاریخ آخرین به‌روزرسانی | 2026-07-17 |

---

## Phase 11 — رفع باگ‌ها و بازسازی ماژول‌های قدیمی

**وضعیت**: ✅ تکمیل

**مشکل اصلی**: بر اساس `test_log.log`:
- **خطای بحرانی**: `Application 'winword.exe' not found` — `ProcessLauncher._find_application()` قادر به یافتن Microsoft Word نبود
- **مشکل تایپ فارسی**: `KeyboardController.type_text()` از `pyautogui.write()` استفاده می‌کرد که فقط متن ASCII پشتیبانی می‌کند
- **باگ زمان‌بندی Bezier**: محاسبه نادرست مدت زمان حرکت موس
- **عملکرد ضعیف**: استفاده از `list` به جای `deque` برای history در کنترلرهای موس و کیبورد
- **سبک کدنویسی**: استفاده از f-string در فراخوانی‌های logging (ارزیابی تنبل)

### زیرفازها

#### 11.1 — اصلاح ProcessLauncher._find_application()
- [x] حذف `break` شکسته که جستجو را پس از اولین فایل متوقف می‌کرد
- [x] اضافه کردن مسیرهای Microsoft Office به جستجو (root\Office16, root\Office15)
- [x] اضافه کردن `COMMONPROGRAMFILES`, `APPDATA`, `PROGRAMDATA` به مسیرهای جستجو
- [x] اضافه کردن جستجوی Windows Registry به عنوان fallback
- **فایل**: `core/system_tools.py`

#### 11.2 — اصلاح SafetyFilter
- [x] حذف import تکراری `os`
- [x] اضافه کردن مسیرهای Microsoft Office به `allowed_paths`
- [x] اضافه کردن executableهای Office به `allowed_apps` و `always_allowed`
- [x] تبدیل f-string logging به %-formatting
- **فایل**: `core/safety_filter.py`

#### 11.3 — بازسازی Mouse Controller
- [x] اصلاح باگ زمان‌بندی Bezier curve (thermalduration / تعداد نقاط)
- [x] جایگزینی `list` با `deque(maxlen=100)` برای action_history
- [x] حذف `max_history` و `_log_action` trimming اضافی
- [x] اضافه کردن `__all__` exports
- **فایل**: `core/mouse_control.py`

#### 11.4 — بازسازی Keyboard Controller
- [x] اصلاح تایپ متن فارسی/غیرASCII از طریق clipboard paste
- [x] جایگزینی `list` با `deque(maxlen=100)` برای action_history
- [x] تبدیل تمام f-string logging به %-formatting
- [x] اضافه کردن `__all__` exports
- **فایل**: `core/keyboard_control.py`

#### 11.5 — بازسازی Action Safety
- [x] تبدیل تمام f-string logging به %-formatting
- [x] حذف ایموجی‌های غیرضروری از لاگ‌ها
- **فایل**: `core/action_safety.py`

### فایل‌های تغییر یافته Phase 11
| فایل | تغییرات |
|------|---------|
| `core/system_tools.py` | ✅ اصلاح `_find_application()` با جستجوی Office و Registry |
| `core/safety_filter.py` | ✅ مسیرهای Office، حذف import تکراری، %-formatting |
| `core/mouse_control.py` | ✅ اصلاح Bezier timing، deque، `__all__` |
| `core/keyboard_control.py` | ✅ تایپ فارسی از clipboard، deque، %-formatting، `__all__` |
| `core/action_safety.py` | ✅ %-formatting، حذف ایموجی |

### معیار تکمیل Phase 11
- [x] `winword.exe` از مسیرهای Office قابل یافتن باشد
- [x] متن فارسی از طریق clipboard paste تایپ شود
- [x] حرکت موس با منحنی Bezier در مدت زمان صحیح انجام شود
- [x] history در هر دو کنترلر O(1) append باشد
- [x] تمام لاگ‌ها از %-formatting استفاده کنند

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

پس از Phase 11:
├── core/system_tools.py                ← اصلاح _find_application()
├── core/safety_filter.py               ← مسیرهای Office + %-formatting
├── core/mouse_control.py               ← اصلاح Bezier + deque
├── core/keyboard_control.py            ← تایپ فارسی + deque + %-formatting
├── core/action_safety.py               ← %-formatting
├── README.md                           ← نسخه 1.1.0
└── ROADMAP.md                          ← این فایل (Phase 11)
```

---

## Phase 8 — تاب‌آوری خطا و بهینه‌سازی زنجیره Failover

**وضعیت**: ✅ تکمیل

**مشکل اصلی**: بر اساس `test_log.log`، زنجیره failover مدل‌ها کاملاً شکست می‌خورد:
- مدل‌های OpenRouter: خطای 403 "Access denied by security policy" (6 مدل)
- ارائه‌دهندگان غیرفعال: Google, Groq, Huggingface, Ollama (بدون API key)
- خطای TimeoutError در اولین مدل (tencent/hy3:free)
- **نتیجه نهایی**: "All 11 available models failed" پس از 3 تلاش

### زیرفازها

#### 8.1 — اصلاح ورودی کاربر (Input Sanitization)
- [x] حذف کاراکترهای اضافی از ورودی (backslash, special chars)
- [x] اعتبارسنجی طول ورودی
- [x] فیلتر کردن ورودی‌های خالی یا فقط فاصله
- **فایل‌ها**: `main.py` (agent_loop)
- **تست**: `tests/test_phase8_error_resilience.py`

#### 8.2 — بهینه‌سازی زنجیره Failover
- [x] اضافه کردن سازوکار "circuit breaker" برای مدل‌های 403
- [x] caching پاسخ‌های 403 برای جلوگیری از تلاش مجدد بی‌فایده
- [x] محدود کردن تعداد تلاش‌ها برای هر مدل خاص (نه فقط کل زنجیره)
- [x] بهبود پیام خطای کاربرپسند
- **فایل‌ها**: `core/ai_brain.py`, `core/model_config.py`

#### 8.3 — مدیریت هوشمند ارائه‌دهندگان
- [x] بررسی اعتبار API key قبل از تلاش اتصال
- [x] رتبه‌بندی مدل‌ها بر اساس تاریخچه موفقیت
- [x] اضافه کردن مکانیزم "model health check" در ابتدا
- **فایل‌ها**: `core/ai_brain.py`, `core/model_config.py`

#### 8.4 — گزارش وضعیت ارائه‌دهندگان
- [x] نمایش لحظه‌ای وضعیت ارائه‌دهندگان در CLI
- [x] دستور `/providers` برای نمایش ارائه‌دهندگان فعال و غیرفعال
- **فایل‌ها**: `main.py`
- **تست**: `tests/test_phase8_error_resilience.py`

### فایل‌های تغییر یافته Phase 8
| فایل | تغییرات |
|------|---------|
| `main.py` | ✅ Input sanitization, ✅ `/providers` command with circuit breaker status |
| `core/ai_brain.py` | ✅ Circuit Breaker, ✅ Health tracking integration, ResponseCache |
| `core/model_config.py` | ✅ ModelHealthTracker, health scoring, sorted by health |
| `tests/test_phase8_error_resilience.py` | ✅ 61 تست (همه عبور) |
| `docs/PHASE8_ERROR_RESILIENCE_REPORT.md` | ✅ گزارش فاز |

### معیار تکمیل Phase 8
- [x] ورودی‌های خاص (backslash, empty) بدون خطا پردازش شوند
- [x] مدل‌های 403 بیش از یک بار تلاش نشوند
- [x] پیام خطای کاربرپسند نمایش داده شود
- [x] دستور `/providers` کار کند
- [x] تست‌ها با موفقیت اجرا شوند (61/61)

---

## Phase 9 — بهینه‌سازی عملکرد و تجربه کاربری

**وضعیت**: ✅ تکمیل (9.1 ✅, 9.2 ✅, 9.3 ✅)

### زیرفازها

#### 9.1 — بهینه‌سازی حافظه و کش
- [x] پیاده‌سازی کش پاسخ‌های AI برای درخواست‌های تکراری
- [x] بهینه‌سازی حجم context (فشرده‌سازی system context)
- [x] محدود کردن اندازه conversation history بهینه
- **فایل‌ها**: `core/memory_integrator.py`, `core/ai_brain.py`

#### 9.2 — بهبود تجربه کاربری CLI
- [x] نمایش پیشرفت درصدی برای عملیات طولانی
- [x] رنگ‌بندی بهتر خروجی‌ها
- [x] دستور `/status` برای نمایش وضعیت سیستم
- [x] پشتیبانی از Tab completion برای دستورات
- **فایل‌ها**: `main.py`

#### 9.3 — تست‌های یکپارچه‌سازی
- [x] تست خودکار زنجیره failover
- [x] تست input sanitization
- [x] تست /providers command
- [x] تست memory context compression
- **فایل‌ها**: `tests/test_phase9_integration.py`

### معیار تکمیل Phase 9
- [x] زمان پاسخ‌گویی برای درخواست‌های تکراری < 500ms
- [x] context size بهینه شده باشد
- [x] CLI تجربه کاربری بهتری داشته باشد
- [x] تست‌های یکپارچه‌سازی عبور کنند

---

## Phase 10 — آماده‌سازی انتشار 1.0.0

**وضعیت**: ✅ تکمیل

### زیرفازها

#### 10.1 — مستندسازی نهایی
- [x] به‌روزرسانی README.md با تمام قابلیت‌های Phase 8-9
- [x] ایجاد CHANGELOG.md کامل
- [x] به‌روزرسانی CONTRIBUTING.md
- [x] بررسی تمام مستندات در docs/
- **فایل‌ها**: `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `docs/*`

#### 10.2 — تست نهایی و پاکسازی
- [x] اجرای کامل تست‌ها (74/74 pass)
- [x] بررسی lint و type hints
- [x] پاکسازی فایل‌های اضافی
- [x] به‌روزرسانی requirements.txt
- **فایل‌ها**: `requirements.txt`, `tests/*`

#### 10.3 — انتشار و برچسب‌گذاری
- [x] تغییر نسخه به 1.0.0 در `main.py` و `README.md`
- [x] ایجاد Git tag v1.0.0
- [x] نوشتن release notes
- [x] ایجاد GitHub Release
- **فایل‌ها**: `main.py`, `README.md`

### معیار تکمیل Phase 10
- [x] نسخه 1.0.0 در تمام فایل‌ها یکسان باشد
- [x] تمام تست‌ها عبور کنند (74/74)
- [x] مستندات کامل و به‌روز باشند
- [x] Git tag ایجاد شده باشد

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

پس از Phase 11:
├── core/system_tools.py                ← اصلاح _find_application()
├── core/safety_filter.py               ← مسیرهای Office + %-formatting
├── core/mouse_control.py               ← اصلاح Bezier + deque
├── core/keyboard_control.py            ← تایپ فارسی + deque + %-formatting
├── core/action_safety.py               ← %-formatting
├── README.md                           ← نسخه 1.1.0
└── ROADMAP.md                          ← این فایل (Phase 11)
```

---

## قوانین توسعه (غیرقابل تغییر)

1. **پس از هر فاز**: این فایل (ROADMAP.md) به‌روزرسانی شود
2. **پس از هر فاز**: گزارش در `docs/` ذخیره شود
3. **پس از هر فاز**: تست در `tests/` ایجاد شود
4. **پس از هر فاز**: commit و push انجام شود
5. **نسخه**: در `README.md` و `main.py` یکسان باشد
6. **تست‌ها**: قبل از commit اجرا شوند
