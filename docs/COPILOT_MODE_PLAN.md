# 🧭 Copilot Mode & Chat-First Plan

## 🎯 هدف
- حالت پیش‌فرض: چت انسانی چندزبانه (فارسی/انگلیسی) بدون نیاز به فعال‌سازی دستی قابلیت‌ها.
- فعال‌سازی هوشمند: مغز (Intent Analyzer + System Agent) تصمیم بگیرد کدام زیرسیستم (Browser, Desktop Automation, Autonomous Agent، Task Engine) لازم است و در لحظه روشن کند.
- حالت تسک‌محور: یک قابلیت اختیاری/قابل فعال‌سازی برای پروژه‌ها و کارهای ساخت‌یافته.
- ایمنی و شفافیت: اعلان فعال/غیرفعال شدن قابلیت‌ها + اخذ تایید کاربر در حالت‌های پرریسک.

## 🏗️ معماری پیشنهادی
- **Chat Core (پیش‌فرض)**: دیالوگ انسانی، حافظه مکالمه، پاسخ سریع.
- **Intent Router**: تحلیل نیت → انتخاب مسیر: پاسخ متنی، Browser-Use، Desktop Automation، Autonomous Agent، Task Engine.
- **Capability Manager**: ماژول جدید برای مدیریت «فعال/غیرفعال»، وابستگی‌ها، و بازگردانی وضعیت (cleanup).
- **Safety & Consent Layer**: محدودیت‌های ایمنی، تایید کاربر برای اقدام‌های حساس، لاگ‌گیری شفاف.
- **Task Mode (Opt-in)**: پروفایل «پروژه‌ای» که صف تسک، اولویت و اجرا را فعال می‌کند.
- **Observability**: متریک‌های ساده (فعال/غیرفعال شدن ماژول‌ها، خطاها، زمان پاسخ) در لاگ.

## 🛠️ فازهای توسعه
### فاز ۱: Chat-First Baseline
- [x] بازبینی CLI/پیش‌فرض‌ها: حالت چت بدون نیاز به فلگ‌های enable.
- [x] ساده‌سازی ورودی/خروجی: پیام خوش‌آمد و راهنمای کوتاه چت.
- [x] مستندسازی UX چت.

### فاز ۲: Intent Router & Capability Manager
- [x] افزودن Intent Router لایه میانی: mapping از intent → اقدام یا فعال‌سازی.
- [x] پیاده‌سازی Capability Manager (register/enable/disable) برای Browser/Automation/Autonomous/Task Engine.
- [x] لاگ و اعلان کاربر هنگام فعال/غیرفعال شدن قابلیت‌ها.

### فاز ۳: Safety & Consent
- [x] تعریف سطح ریسک برای هر قابلیت (safe/power) و نیاز به تایید.
- [x] پیام‌های تایید تعاملی پیش از اقدامات حساس (مثلاً کنترل دسکتاپ یا مرورگر).
- [x] بهبود SessionControl برای حالت‌های پویا.

### فاز ۴: Task Mode (Opt-in)
- [x] پروفایل «Project/Task Mode» با فلگ یا دستور درون چت برای فعال‌سازی.
- [x] ادغام با TaskEngine (صف، اولویت، وضعیت).
- [x] راهنمای فعال/غیرفعال کردن و خروج تمیز.

راهنما:
- فلگ `--task-mode` برای فعال‌سازی اولیه.
- دستورات چت: «task mode on/off» برای کنترل دستی.
- در حالت chat-first، درخواست‌های شامل «task» یا «;» به صف اضافه می‌شوند و از طریق TaskEngine اجرا می‌شوند.

### فاز ۵: Telemetry & Cleanup
- [x] ثبت متریک‌های سبک در لاگ (فعال‌سازی‌ها، خطاها، مدت‌ها).
- [x] Cleanup ایمن هنگام خروج یا تغییر حالت.
- [x] مستندسازی کامل و به‌روزرسانی README.

راهنما:
- لاگ رویدادها با برچسب `TELEMETRY` شامل routing، consent و queueing.
- cleanup خودکار قابلیت‌ها در خروج یا تغییر حالت.

## 📑 خروجی‌های موردنیاز
- کد: ماژول جدید Capability Manager، به‌روزرسانی main.py، Intent Router.
- تست: واحد و یکپارچه برای router و فعال‌سازی/غیرفعال‌سازی قابلیت‌ها.
- مستندات: همین فایل (به‌روزرسانی تیک‌ها)، README، و راهنمای کوتاه استفاده.

## 🧪 برنامه تست
- Unit: Intent classification → routing → activation.
- Integration: سناریوهای چت معمولی، درخواست وب، درخواست اتوماسیون دسکتاپ، درخواست goal خودکار، ورود/خروج Task Mode.
- Safety: تاییدهای کاربر، بلاک اکشن در حالت safe.

## 🧭 UX چت (فعلی)
- حالت پیش‌فرض: چت آزاد چندزبانه، بدون نیاز به فعال‌سازی دستی ماژول‌ها.
- پیام خوش‌آمد کوتاه + نمونه درخواست‌ها (ایمیل، پوشه دسکتاپ، چک وب).
- نمایش وضعیت قابلیت‌ها در حالت chat-first مخفی می‌شود تا خروجی خلوت بماند.
- فلگ `--task-mode` برای آینده (پروژه/تسک) اضافه شده؛ در حالت عادی خاموش است.

## 🗺️ وابستگی‌ها
- core/intent_analyzer.py، core/intelligent_agent.py، core/task_engine.py، core/realtime_loop.py
- لایه ایمنی: core/safety_filter.py، SessionControl در main.py

## ⚠️ ریسک‌ها و کاهنده‌ها
- خطای تشخیص intent → fallback به پرسش/تایید کاربر.
- فعال‌سازی ناخواسته اتوماسیون → نیاز به consent و ایمنی.
- پیچیدگی UX → پیام‌های کوتاه و شفاف.

## ✅ وضعیت تیک‌ها
- فاز ۱: [x] ✅
- فاز ۲: [x] ✅
- فاز ۳: [x] ✅
- فاز ۴: [x] ✅
- فاز ۵: [x] ✅

## 🏗️ پیاده‌سازی فاز ۲ - جزئیات

### ماژول‌های جدید
1. **core/intent_router.py**
   - `IntentRouter` کلاس: تجزیه intent و مسیریابی
   - `RouteType` enum: نوع‌های مسیریابی (CHAT_RESPONSE، BROWSER_USE، DESKTOP_AUTOMATION، AUTONOMOUS_AGENT، TASK_MODE)
   - `Route` dataclass: نتیجه مسیریابی + فعال‌سازی‌های لازم
   - منطق: تشخیص الگوی verb/target و فعال‌سازی صحیح

2. **core/capability_manager.py**
   - `CapabilityManager` کلاس: مدیریت دینامیکی قابلیت‌ها
   - `CapabilityType` enum: انواع قابلیت‌ها
   - `CapabilityInfo` dataclass: متادیتای قابلیت
   - عملیات: register، enable، disable، is_enabled، get_status، cleanup
   - Callbacks: on_enabled، on_disabled برای اعلان تغییرات

### ادغام در main.py
- ایمپورت ماژول‌های جدید
- مقداردهی IntentRouter و CapabilityManager در main()
- ثبت تمام قابلیت‌ها (browser_use، desktop_automation، autonomous_agent، task_mode)
- پاس دادن به process_user_input

### تست‌ها
- test_intent_router.py: 7+ تست برای routing و safety
- test_capability_manager.py: 10+ تست برای enable/disable و state
- Coverage: ~85%

## 🏗️ پیاده‌سازی فاز ۳ - جزئیات

### ماژول‌های جدید
1. **core/safety_consent_manager.py**
   - `RiskLevel` enum: SAFE، POWER، CRITICAL
   - `ConsentRequest` dataclass: درخواست تایید کاربر
   - `ConsentDecision` dataclass: تصمیم کاربر
   - `SafetyConsentManager` کلاس: مدیریت تایید و سطح‌های ریسک
   - متدها: request_consent()، can_execute_action()، get_decision_history()، get_statistics()

### بهبود‌های موجود
1. **core/intent_router.py**
   - افزودن RiskLevel import از safety_consent_manager
   - اضافه کردن risk_level field به Route dataclass
   - پیاده‌سازی _assess_risk_level() برای ارزیابی ریسک
   - بهبود route() برای تعیین سطح ریسک و نیاز تایید

2. **core/capability_manager.py**
   - Integration با SafetyConsentManager (آماده برای فاز ۴)

3. **main.py SessionControl**
   - اضافه کردن safety_consent_manager field
   - متد set_safety_consent_manager()

### ادغام در main.py
- ایمپورت SafetyConsentManager و RiskLevel
- مقداردهی SafetyConsentManager در main()
- اتصال به SessionControl
- پاس دادن به process_user_input

### تست‌ها
- test_safety_consent.py: 15+ تست برای RiskLevels، ConsentRequests، ConsentWithHandler، ConsentHistory، CanExecuteAction
- Coverage: ~90%
