# Changelog

تمام تغییرات قابل توجه در Software-AI در این فایل ثبت می‌شود.

قالب بر اساس [Keep a Changelog](https://keepachangelog.com/fa/1.1.0/).

---

## [1.1.0] — 2026-07-17

### Phase 11 — رفع باگ‌ها و بازسازی ماژول‌های قدیمی

#### Fixed
- **ProcessLauncher._find_application()**: اصلاح `break` شکسته که جستجو را متوقف می‌کرد. اضافه شدن مسیرهای Microsoft Office، `COMMONPROGRAMFILES`، `PROGRAMDATA`، و جستجوی Windows Registry
- **KeyboardController.type_text()**: متن فارسی/غیرASCII از طریق clipboard paste تایپ می‌شود (pyautogui.write فقط ASCII پشتیبانی می‌کند)
- **MouseController Bezier timing**: محاسبه صحیح مدت زمان حرکت (`duration / تعداد نقاط` به جای `duration * 0.05`)

#### Changed
- **MouseController** و **KeyboardController**: `action_history` از `list` به `deque(maxlen=100)` تغییر کرد (O(1) append به جای O(n) trim)
- **SafetyFilter**: اضافه شدن مسیرهای Microsoft Office به `allowed_paths` و executableهای Office به `allowed_apps`
- **Action Safety**: تبدیل تمام f-string logging به %-formatting (lazy evaluation)
- حذف ایموجی‌های غیرضروری از لاگ‌ها

---

## [1.0.0] — 2026-07-10

### Phase 8 — تاب‌آوری خطا و بهینه‌سازی زنجیره Failover

#### Added
- **Input Sanitization**: حذف کاراکترهای اضافی (backslash) از ورودی کاربر
- **`/providers` command**: نمایش لحظه‌ای وضعیت ارائه‌دهندگان API در CLI
- **`/status` command**: نمایش وضعیت کامل سیستم (ارائه‌دهندگان، سلامت مدل‌ها، حافظه)
- **`ModelCircuitBreaker`**: قفل خودکار مدل‌های 403 پس از ۳ بار شکست (قفل ۵ دقیقه‌ای)
- **`ModelHealthTracker`**: ردیابی تاریخچه موفقیت/شکست مدل‌ها و رتبه‌بندی بر اساس امتیاز سلامت
- **Sorted model fallback**: مدل‌ها بر اساس امتیاز سلامت + اولویت مرتب می‌شوند

#### Changed
- `ask_with_fallback()` اکنون از Circuit Breaker و Health Tracker استفاده می‌کند
- مدل‌های 403 دیگر بیش از یک بار تلاش نمی‌شوند

### Phase 9 — بهینه‌سازی عملکرد و تجربه کاربری

#### Added
- **`ResponseCache`**: کش ۱۰ دقیقه‌ای برای پاسخ‌های AI تکراری (حداکثر ۱۰۰ entry)
- **Context Compression**: فشرده‌سازی پیام‌های قدیمی‌تر در memory context
- **Progress Indicator**: نمایش "Analyzing request..." هنگام پردازش درخواست
- **Integration Tests**: ۱۳ تست یکپارچه‌سازی برای زنجیره failover، ورودی، حافظه و نسخه

#### Changed
- `_max_history` از ۵۰ به ۳۰ کاهش یافت (کاهش مصرف حافظه)
- پیام‌های قدیمی‌تر از ۳ پیام آخر خلاصه می‌شوند

### Fixed
- ورودی‌هایی با backslash ابتدایی (مثل `\What is my CPU?`) بدون خطا پردازش می‌شوند
- مدل‌های 403 دیگر باعث retry storm نمی‌شوند

---

## [0.9.0] — 2026-07-09

### Phase 7 — درک محیط ویندوز
- مسیریاب متمرکز برای تبدیل نام‌های طبیعی به مسیرهای فایل
- پشتیبانی از نام‌های محلی‌شده (فارسی و انگلیسی)
- شناسایی خودکار برنامه‌های نصب شده
- اطلاعات درایوها (برچسب، فضای کل و خالی)

---

## [0.8.0] — 2026-07-08

### Phase 6 — مدیریت نشست‌های مکالمه
- ایجاد، حذف، جستجو و سوئیچ بین نشست‌ها
- پشتیبانی از `SessionManager` و `ChatSession`

---

## [0.7.0] — 2026-07-07

### Phase 5 — حافظه پایدار
- یادآوری مکالمات قبلی
- یادگیری ترجیحات کاربر
- حافظه کوتاه‌مدت و بلندمدت

---

## [0.6.0] — 2026-07-06

### Phase 4 — برنامه‌ریزی چندمرحله‌ای هوشمند
- پشتیبانی از درخواست‌های پیچیده چندعملی
- WorkflowEngine و StepTracker

---

## [0.5.0] — 2026-07-05

### Phase 3 — حلقه بینایی خودمختار
- یکپارچه‌سازی DesktopVision
- اعتبارسنجی بصری و تلاش مجدد

---

## [0.4.0] — 2026-07-04

### Phase 2 — فراخوانی ابزار ساختاریافته
- جایگزینی پاسخ‌های چت با فراخوانی ابزار معتبر با schema

---

## [0.3.0] — 2026-07-03

### Phase 1 — معماری عامل‌محور
- حلقه عامل اصلی
- شناسایی هوشمند ارائه‌دهندگان API
- ۲۰ ابزار استاندارد
