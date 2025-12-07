# 🤖 Autonomous Agent - مثل browser-use اما برای ویندوز!

## چیه این؟

**Autonomous Agent** یه سیستم هوش مصنوعی هدف‌محوره که با پرامپت‌های ساده می‌تونه کل ویندوز رو کنترل کنه!

### قبل و بعد:

**قبل (Action-Based):**
```python
تو: "LaunchApp notepad.exe"
تو: "Wait 2 seconds"
تو: "Click at (500, 300)"  # باید مختصات دقیق بدی!
تو: "Type Hello"
```

**بعد (Goal-Based):**
```python
تو: "نوت‌پد باز کن بنویس سلام"

Agent خودش:
  ✅ برنامه می‌ریزه
  ✅ نوت‌پد رو پیدا می‌کنه
  ✅ باز می‌کنه
  ✅ سلام رو تایپ می‌کنه
```

---

## 🚀 شروع سریع

### نصب
```bash
pip install pillow pytesseract pyautogui pygetwindow opencv-python
```

### اجرا
```python
from core.autonomous_agent import AutonomousAgent

agent = AutonomousAgent()

# پرامپت ساده
result = await agent.execute_goal("برو E: فولدر MyDocs بساز")

if result['success']:
    print("✅ انجام شد!")
```

### دمو تعاملی
```bash
python examples/autonomous_demo.py

# انتخاب گزینه 7: Interactive Mode
# بعدش هر چی بخوای بهش بگو!
```

---

## 💡 مثال‌ها

### ساده
```python
await agent.execute_goal("نوت‌پد باز کن")
await agent.execute_goal("Open Calculator")
await agent.execute_goal("بنویس سلام دنیا")
```

### متوسط
```python
await agent.execute_goal("برو This PC باز کن E:")
await agent.execute_goal("Create a folder called MyDocs")
await agent.execute_goal("Type test.txt and press Enter")
```

### پیچیده
```python
await agent.execute_goal("""
    Open File Explorer.
    Navigate to E: drive.
    Create a new folder called 'MyProjects'.
    Open that folder.
    Create a text file called 'README.txt'.
""")
```

---

## 🎯 چطور کار می‌کنه؟

```
1. پرامپت می‌گیره
   ↓
2. AI برنامه می‌ریزه (مراحل رو می‌سازه)
   ↓
3. Screenshot می‌گیره (می‌بینه الان کجاست)
   ↓
4. عنصر رو پیدا می‌کنه (با OCR)
   ↓
5. Action انجام میده (کلیک، تایپ، ...)
   ↓
6. بررسی می‌کنه موفق شد؟
   ↓
   ✅ آره → برو مرحله بعد
   ❌ نه → دوباره تلاش کن
```

---

## 🆚 مقایسه با browser-use

| ویژگی | browser-use | Autonomous Agent |
|-------|-------------|------------------|
| پلتفرم | Browser | Windows Desktop |
| بینایی | Playwright | OCR + Screenshot |
| پرامپت ساده | ✅ | ✅ |
| خودتصمیم‌گیری | ✅ | ✅ |
| فارسی | ❌ | ✅ |

---

## 📋 قابلیت‌ها

### ✅ چیزایی که خوب کار می‌کنه:
- باز کردن برنامه‌ها
- کلیک روی دکمه‌ها (با متن)
- تایپ کردن
- File Explorer navigation
- کارهای چند مرحله‌ای (5-10 مرحله)

### ⚠️ چیزایی که هنوز چالش داره:
- عناصر بدون متن (آیکون‌های خالص)
- منوهای خیلی پیچیده
- کارهای خیلی طولانی (20+ مرحله)

---

## 🔧 تنظیمات

### API Keys لازمه:
```bash
# .env
GOOGLE_API_KEY=your_key
OPENAI_API_KEY=your_key
```

### OCR باید نصب باشه:
```
Tesseract OCR:
https://github.com/UB-Mannheim/tesseract/wiki
```

---

## 📚 مستندات کامل

- **[AUTONOMOUS_AGENT.md](docs/AUTONOMOUS_AGENT.md)** - توضیحات کامل
- **[autonomous_demo.py](examples/autonomous_demo.py)** - مثال‌های کاربردی
- **[test_autonomous_agent.py](tests/test_autonomous_agent.py)** - تست‌ها

---

## 🎮 مثال واقعی

```python
# اجرای دمو
python examples/autonomous_demo.py

# انتخاب "Interactive Mode"

🎯 Your command: برو This PC باز کن E:

🤖 Executing: برو This PC باز کن E:
----------------------------------------
📋 Plan created: 6 steps
  Step 1: Take screenshot to see current state
  Step 2: Click on This PC icon
  Step 3: Wait for File Explorer to open
  Step 4: Click on E: drive
  Step 5: Wait for E: to open
  Step 6: Take screenshot to verify

🔧 Executing Step 1: Take screenshot to see current state
📸 Screenshot saved: data/screenshots/agent_20251206_143022.png

🔧 Executing Step 2: Click on This PC icon
🔍 Searching for element: This PC
✅ Found exact match: This PC at (150, 200)

🔧 Executing Step 3: Wait for File Explorer to open
...

✅ Success! Completed 6 steps
```

---

## 💪 مزایا

1. **پرامپت‌های ساده**: نیازی به دستورات دقیق نیست
2. **خودتصمیم‌گیری**: خودش می‌فهمه کجا کلیک کنه
3. **بازخورد مداوم**: اگه فیل شد، دوباره تلاش می‌کنه
4. **فارسی**: کامل پشتیبانی می‌کنه
5. **یادگیری**: تاریخچه رو یادش می‌مونه

---

## 🚧 در حال توسعه

- [ ] تشخیص آیکون (بدون متن)
- [ ] Gaming automation (WASD + Mouse)
- [ ] Self-healing (خودش راه جدید پیدا کنه)
- [ ] Web Browser integration
- [ ] Voice control

---

## 🎯 خلاصه

با **Autonomous Agent**:
- ✅ پرامپت ساده بده
- ✅ Agent خودش برنامه می‌ریزه
- ✅ خودش اجرا می‌کنه
- ✅ خودش بررسی می‌کنه
- ✅ اگه فیل شد retry می‌کنه

**بدون اینکه تو بگی "کجا کلیک کن"!** 🚀

---

**ساخته شده با ❤️ توسط Shahin Company**

برای راهنمایی بیشتر: [docs/AUTONOMOUS_AGENT.md](docs/AUTONOMOUS_AGENT.md)

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: November 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
