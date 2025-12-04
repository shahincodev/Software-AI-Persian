# 🧪 راهنمای تست جامع Software-AI

## 📋 فهرست

1. [تست سریع](#تست-سریع)
2. [تست جامع](#تست-جامع)
3. [تفسیر نتایج](#تفسیر-نتایج)
4. [حل مشکلات رایج](#حل-مشکلات-رایج)

---

## 🚀 تست سریع

برای یک **بررسی سریع** که فقط API connection رو چک می‌کنه:

```bash
python test_api_connection.py
```

**خروجی:**
- ✅/❌ وضعیت .env file
- ✅/❌ وضعیت API keys
- ✅/❌ اتصال واقعی به Google API
- ✅/❌ Git status
- ✅/❌ Tesseract OCR

**زمان:** ~5 ثانیه

---

## 🔬 تست جامع

برای **بررسی کامل** همه چیز (مو رو از ماست بکشیم بیرون! 😁):

```bash
python test_comprehensive.py
```

### این فایل چی‌ها رو تست می‌کنه؟

#### **Category 1: Environment & Dependencies** 🔧
- وجود فایل `.env`
- نسخه Python (باید 3.10+)
- کتابخانه‌های حیاتی:
  - `browser-use`
  - `python-dotenv`
  - `Pillow`
  - `pyautogui`
  - `psutil`
  - `langchain`

#### **Category 2: API Keys & Authentication** 🔑
- `GOOGLE_API_KEY` (ضروری)
- `OPENAI_API_KEY` (اختیاری)
- `GROQ_API_KEY` (اختیاری)
- بررسی placeholder ها
- بررسی format کلیدها

#### **Category 3: Google API Real Connection** 🌐
- **اتصال واقعی** به Google Gemini
- ارسال یک پیام تست
- بررسی response
- تشخیص انواع خطا:
  - `API_KEY_INVALID` - کلید نامعتبر
  - `403 FORBIDDEN` - مشکل دسترسی/region
  - `FAILED_PRECONDITION` - billing یا location

#### **Category 4: Core System Imports** 📦
تست import همه ماژول‌های کور:
- `core.ai_brain.AIBrain`
- `core.desktop_vision.DesktopVision`
- `core.desktop_vision.TextBox` ← Fix v0.9.2
- `core.desktop_vision.WindowInfo` ← Fix v0.9.2
- `core.action_controller.ActionController`
- `core.intelligent_agent.IntelligentSystemAgent`
- `core.mouse_control.MouseController`
- `core.keyboard_control.KeyboardController`

#### **Category 5: Dataclass Structures** 🏗️
تست دقیق dataclass های اصلاح شده در v0.9.2:

**TextBox:**
```python
TextBox(
    text="test",
    x=10, y=20,
    width=100, height=50,
    confidence=0.9
)
# Properties: center, top_left, bottom_right
```

**WindowInfo:**
```python
WindowInfo(
    title="Test",
    x=0, y=0,
    width=800, height=600,
    is_active=True
)
# Properties: center, bounds
```

#### **Category 6: Action Controller & Approval** 🎮
- `ActionResult` enum (SUCCESS, FAILED, BLOCKED)
- ساخت ActionController
- سیستم approval (Fix v0.9.2)

#### **Category 7: Vision System** 👁️
- **Tesseract OCR:**
  - بررسی `TESSERACT_PATH`
  - وجود executable
- **Screenshot:**
  - گرفتن screenshot
  - بررسی validity

#### **Category 8: AI Brain & Model Selection** 🧠
- ساخت AIBrain
- `get_model()` برای انواع مختلف
- تحلیل پیچیدگی task

#### **Category 9: Git Repository** 📚
- Working directory clean یا نه
- آخرین commit
- Version tag (v0.9.2)

#### **Category 10: Real-World Simulation** 🚀
تست **واقعی** با AI:
- "open notepad"
- "what is my CPU?"
- بررسی response های AI

---

## 📊 تفسیر نتایج

### کدهای رنگی:

```
✅ سبز  = PASS    - همه چیز کامل
⚠️  زرد  = WARNING - کار می‌کنه ولی بهینه نیست
❌ قرمز = FAIL    - مشکل جدی
```

### System Health:

| Health | معنی | شرایط |
|--------|------|-------|
| **EXCELLENT** 🎉 | عالی | 0 Failed, 0 Warnings |
| **GOOD** 👍 | خوب | 0 Failed, چند Warning |
| **FAIR** ⚡ | قابل قبول | 1-2 Failed |
| **POOR** ⚠️ | ضعیف | 3-5 Failed |
| **CRITICAL** 💥 | بحرانی | 5+ Failed |

### خروجی JSON:

فایل `test_comprehensive_results.json` شامل:
```json
{
  "timestamp": "2025-12-04T...",
  "duration_seconds": 12.34,
  "total_tests": 45,
  "passed": 40,
  "failed": 2,
  "warnings": 3,
  "health": "GOOD",
  "details": [...]
}
```

---

## 🔧 حل مشکلات رایج

### ❌ Google API: "API_KEY_INVALID"

**علت:** کلید شما placeholder است یا expired

**راه حل:**
1. برو به: https://aistudio.google.com/app/apikey
2. یک کلید جدید بساز
3. در `.env` جایگزین کن:
   ```
   GOOGLE_API_KEY=AIzaSyAaBbCc123...  # کلید واقعی
   ```

### ❌ Google API: "403 FORBIDDEN"

**علت:** Region شما block شده یا billing فعال نیست

**راه حل:**
1. فیلترشکن روشن کن
2. یا از VPN استفاده کن
3. یا billing رو در Google Cloud فعال کن

### ⚠️ Tesseract: "not configured"

**علت:** OCR نصب نیست

**راه حل:**
1. دانلود: https://github.com/UB-Mannheim/tesseract/wiki
2. نصب
3. در `.env` مسیر رو set کن:
   ```
   TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

### ❌ Dependencies: "not installed"

**راه حل:**
```bash
pip install -r requirements.txt
```

### ❌ Git: "uncommitted changes"

**راه حل:**
```bash
git add .
git commit -m "Test changes"
```

---

## 📈 مقایسه قبل/بعد از v0.9.2

### قبل از Fix (v0.9.1):
```
❌ WindowInfo: NameError (30+ errors)
❌ TextBox: TypeError (15+ errors)
❌ Approval: اجرا قبل از تایید
System Health: CRITICAL (20-25% کارآیی)
```

### بعد از Fix (v0.9.2):
```
✅ WindowInfo: تعریف شده با همه properties
✅ TextBox: dataclass کامل
✅ Approval: blocking wait قبل از اجرا
System Health: GOOD-EXCELLENT (60-80% با API)
```

---

## 🎯 چک‌لیست پیش از استفاده در Production:

- [ ] همه تست‌های Category 1-4 PASS
- [ ] Google API connection موفق
- [ ] System Health حداقل GOOD
- [ ] Git working directory clean
- [ ] Version tag درست (v0.9.2+)

---

## 📞 پشتیبانی

اگر تست شما fail شد:
1. خروجی ترمینال رو کپی کن
2. فایل `test_comprehensive_results.json` رو باز کن
3. بخش `details` رو بررسی کن
4. error های FAIL رو پیدا کن
5. از بخش "حل مشکلات رایج" استفاده کن

---

**موفق باشی! 🚀**

مو رو از ماست کشیدیم بیرون! 😁
