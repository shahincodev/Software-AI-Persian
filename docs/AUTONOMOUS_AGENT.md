# Autonomous Agent - Vision-Based Windows Control

## 🎯 مفهوم

**Autonomous Agent** یه سیستم هوش مصنوعی هدف‌محوره که مثل **browser-use** کار می‌کنه، اما برای ویندوز!

### تفاوت با سیستم قبلی:

| ویژگی | سیستم قبلی (Action-Based) | Autonomous Agent (Goal-Based) |
|-------|---------------------------|-------------------------------|
| **ورودی** | دستورات دقیق | پرامپت‌های ساده |
| **مثال ورودی** | "LaunchApp notepad.exe" | "نوت‌پد باز کن" |
| **تصمیم‌گیری** | کاربر می‌گه چی کلیک کنه | خودش تصمیم می‌گیره |
| **بینایی** | محدود | کامل با OCR و Vision |
| **بازخورد** | ندارد | حلقه بازخورد مداوم |
| **پیچیدگی** | کارهای ساده | کارهای پیچیده چند مرحله‌ای |

---

## 🚀 مثال‌های واقعی

### مثال 1: پرامپت ساده
```python
تو: "برو This PC باز کن E:"

سیستم قبلی نیاز داشت:
  ❌ "LaunchApp explorer.exe"
  ❌ "Wait 2 seconds"
  ❌ "Click at (100, 200)"  # کاربر باید مختصات بده!
  ❌ "Type E:\\"

Autonomous Agent:
  ✅ خودش This PC رو پیدا می‌کنه
  ✅ خودش کلیک می‌کنه
  ✅ خودش E: رو پیدا می‌کنه
  ✅ خودش کلیک می‌کنه
```

### مثال 2: کار پیچیده
```python
تو: "فولدر MyDocs بساز توی E:"

Agent خودش این مراحل رو انجام میده:
  1. Screenshot می‌گیره (ببینه الان کجاست)
  2. This PC رو پیدا می‌کنه و کلیک می‌کنه
  3. صبر می‌کنه File Explorer باز بشه
  4. E: رو پیدا می‌کنه و کلیک می‌کنه
  5. صبر می‌کنه E: باز بشه
  6. Right Click می‌کنه
  7. "New Folder" رو پیدا می‌کنه و کلیک می‌کنه
  8. "MyDocs" رو تایپ می‌کنه
  9. Enter می‌زنه
```

### مثال 3: پرامپت مبتدی
```python
# کاربر مبتدی:
تو: "یه فولدر بساز"

Agent:
  - ✅ می‌فهمه کجا بسازه (Desktop یا location فعلی)
  - ✅ اسم پیش‌فرض میذاره (New Folder)
  - ✅ اگه مشکلی بود، دوباره تلاش می‌کنه
```

---

## 🧠 معماری سیستم

### 1. **Vision System (بینایی)**
```python
DesktopVision:
  - capture_screen() → اسکرین‌شات
  - read_screen_ocr() → خوندن متن با Tesseract
  - find_element(text) → پیدا کردن عنصر
```

### 2. **AI Brain (مغز)**
```python
AIBrain:
  - create_plan(goal) → تبدیل هدف به مراحل
  - analyze_screen(screenshot) → فهم وضعیت صفحه
  - decide_next_step() → تصمیم‌گیری
```

### 3. **Action Controllers (کنترلر)**
```python
MouseController: کلیک، Right Click، حرکت
KeyboardController: تایپ، کلیدها
SmartWaiter: انتظار هوشمند
```

### 4. **Autonomous Agent (هماهنگ‌کننده)**
```python
AutonomousAgent:
  1. execute_goal(goal) → دریافت هدف
  2. create_plan() → برنامه‌ریزی با AI
  3. execute_step() → اجرای هر مرحله
  4. verify_success() → بررسی موفقیت
  5. retry_if_failed() → تلاش مجدد
```

---

## 🔄 حلقه بازخورد (Feedback Loop)

```
1. Screenshot بگیر
   ↓
2. AI تحلیل کنه: "الان کجام؟"
   ↓
3. AI تصمیم بگیره: "بعدش چیکار کنم؟"
   ↓
4. Action انجام بده (کلیک، تایپ، ...)
   ↓
5. بررسی: موفق شد؟
   ↓
   ├─ ✅ آره → برو مرحله بعد
   └─ ❌ نه → دوباره تلاش کن
```

---

## 📋 نحوه استفاده

### روش 1: استفاده ساده
```python
from core.autonomous_agent import AutonomousAgent

agent = AutonomousAgent()

# پرامپت ساده
result = await agent.execute_goal("نوت‌پد باز کن")

if result['success']:
    print("✅ موفق!")
else:
    print(f"❌ ناموفق: {result['error']}")
```

### روش 2: کارهای پیچیده
```python
# workflow پیچیده
result = await agent.execute_goal("""
    Open File Explorer.
    Navigate to E: drive.
    Create a new folder called 'MyProjects'.
    Open that folder.
    Create a text file called 'README.txt'.
""")
```

### روش 3: حالت تعاملی
```python
# اجرای دمو
python examples/autonomous_demo.py

# انتخاب "Interactive Mode"
# بعدش هر چی بخوای بهش بگو!
```

---

## 🎮 مثال‌های کاربردی

### 1. اتوماسیون روزانه
```python
await agent.execute_goal("""
    Open Chrome.
    Go to gmail.com.
    Click on 'Compose' button.
""")
```

### 2. مدیریت فایل
```python
await agent.execute_goal("""
    برو Desktop.
    تمام فایل‌های txt رو پیدا کن.
    ببرشون توی فولدر 'Text Files'.
""")
```

### 3. نصب نرم‌افزار
```python
await agent.execute_goal("""
    Open installer.exe.
    Click Next on each screen.
    Click Install when ready.
    Wait for completion.
    Click Finish.
""")
```

### 4. گیمینگ 🎮
```python
await agent.execute_goal("""
    استیم رو باز کن.
    کانتر رو پیدا کن.
    روش کلیک کن.
    Play رو بزن.
""")
```

---

## 🔧 ویژگی‌های پیشرفته

### 1. **خودکارسازی با بینایی**
- Agent اسکرین‌شات می‌گیره و متن‌ها رو می‌خونه
- عناصر رو با OCR پیدا می‌کنه
- موقعیت دکمه‌ها رو تشخیص میده

### 2. **برنامه‌ریزی هوشمند**
- AI هدف رو تجزیه می‌کنه به مراحل
- مراحل ساده و atomic هستن
- اگه یه مرحله فیل شد، دوباره تلاش می‌کنه

### 3. **بازخورد مداوم**
- بعد هر Action بررسی می‌کنه موفق بود؟
- اگه نه، استراتژی رو عوض می‌کنه
- یاد می‌گیره چه مسیری بهتره

### 4. **فهم زبان طبیعی**
- فارسی و انگلیسی
- پرامپت‌های مبتدی
- دستورات غیر دقیق ("یه فولدر بساز" بدون اسم)

---

## 🆚 مقایسه با browser-use

| ویژگی | browser-use | Autonomous Agent |
|-------|-------------|------------------|
| **پلتفرم** | وب (Browser) | ویندوز (Desktop) |
| **بینایی** | Playwright Vision | OCR + Screenshot |
| **کنترل** | JavaScript + DOM | Mouse + Keyboard |
| **پرامپت ساده** | ✅ | ✅ |
| **خودتصمیم‌گیری** | ✅ | ✅ |
| **بازخورد** | ✅ | ✅ |
| **زبان فارسی** | ❌ | ✅ |

---

## 📊 محدودیت‌های فعلی

### کارهایی که خوب کار می‌کنه:
- ✅ باز کردن برنامه‌ها
- ✅ کلیک روی دکمه‌ها (اگه متن داشته باشن)
- ✅ تایپ متن
- ✅ File Explorer navigation
- ✅ کارهای ساده چند مرحله‌ای

### کارهایی که هنوز چالش داره:
- ⚠️ عناصری که متن ندارن (آیکون‌های خالص)
- ⚠️ منوهای پیچیده
- ⚠️ تشخیص موفقیت Action (بعضی وقت‌ها)
- ⚠️ کارهای خیلی پیچیده (10+ مرحله)

---

## 🚀 برنامه توسعه آینده

### نسخه بعدی (v1.0):
- [ ] تشخیص آیکون با Computer Vision
- [ ] یادگیری از تاریخچه (RL)
- [ ] پشتیبانی از Web Browser
- [ ] Multi-window management
- [ ] Voice control integration

### نسخه پیشرفته (v2.0):
- [ ] Gaming automation (WASD + Mouse)
- [ ] Complex workflows (20+ steps)
- [ ] Self-healing (اگه فیل شد، خودش راه جدید پیدا کنه)
- [ ] Learning from user corrections

---

## 💡 نکات مهم

### 1. **OCR باید نصب باشه**
```bash
# نصب Tesseract OCR
# دانلود از: https://github.com/UB-Mannheim/tesseract/wiki
```

### 2. **API Keys لازمه**
```bash
# .env فایل
GOOGLE_API_KEY=your_key
OPENAI_API_KEY=your_key
```

### 3. **صبر کن!**
- Agent زمان نیاز داره (هر مرحله ~2-5 ثانیه)
- اسکرین‌شات + OCR + AI planning زمان می‌بره
- اما خودکاره! 😊

---

## 🎯 خلاصه

**Autonomous Agent = browser-use برای ویندوز**

با یه پرامپت ساده مثل:
```
"برو E: فولدر بساز"
```

Agent خودش:
- ✅ تصمیم می‌گیره
- ✅ برنامه می‌ریزه
- ✅ اجرا می‌کنه
- ✅ بررسی می‌کنه
- ✅ اگه فیل شد retry می‌کنه

**بدون اینکه تو بگی "کجا کلیک کن"!** 🚀

---

## 📚 منابع بیشتر

- `core/autonomous_agent.py` - کد اصلی
- `examples/autonomous_demo.py` - مثال‌های کاربردی
- `docs/DESKTOP_VISION.md` - توضیحات Vision System
- `docs/AI_WINDOWS_CONTROL.md` - کنترل ویندوز با AI

---

**ساخته شده با ❤️ توسط Shahin Company**

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: December 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
