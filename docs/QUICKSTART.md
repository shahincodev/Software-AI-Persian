# 🚀 راهنمای سریع شروع - Software-AI

این راهنما نحوه اجرای صحیح و تست کامل پروژه Software-AI را قدم به قدم توضیح می‌دهد.

---

## 📋 فهرست مطالب

1. [پیش‌نیازها](#پیش-نیازها)
2. [آماده‌سازی محیط](#آماده-سازی-محیط)
3. [تنظیم API Keys](#تنظیم-api-keys)
4. [اجرای اولیه](#اجرای-اولیه)
5. [دستورات تست آماده](#دستورات-تست-آماده)
6. [عیب‌یابی](#عیب-یابی)

---

## 🎯 پیش‌نیازها

### نرم‌افزارهای مورد نیاز:

```powershell
# بررسی نسخه Python (باید 3.10+ باشد)
python --version

# بررسی pip
pip --version

# بررسی git
git --version
```

**حداقل نیازها:**
- ✅ Python 3.10 یا بالاتر
- ✅ pip (نصب شده با Python)
- ✅ Git (برای clone کردن پروژه)
- ✅ اتصال اینترنت (برای API calls)

---

## 🛠️ آماده‌سازی محیط

### مرحله 1: دریافت کد

اگر هنوز clone نکرده‌اید:

```powershell
# Clone repository
git clone https://github.com/shahincodev/Software-AI-Persian.git

# وارد پوشه پروژه شوید
cd Software-AI-Persian
```

اگر قبلاً clone کرده‌اید:

```powershell
# بروزرسانی به آخرین نسخه
git pull origin main
```

---

### مرحله 2: نصب وابستگی‌ها

```powershell
# نصب تمام کتابخانه‌های مورد نیاز
pip install -r requirements.txt

# بررسی نصب موفق
pip list | Select-String "openai|google|groq"
```

**انتظار می‌رود ببینید:**
```
google-generativeai    x.x.x
groq                   x.x.x
openai                 x.x.x
```

---

### مرحله 3: پاکسازی داده‌های قدیمی (اختیاری)

برای شروع تمیز:

```powershell
# حذف داده‌های قدیمی (اگر وجود دارد)
if (Test-Path "data") { Remove-Item -Path "data" -Recurse -Force }

# پوشه‌ها خودکار ساخته می‌شوند
```

---

## 🔑 تنظیم API Keys

### مرحله 1: کپی فایل نمونه

```powershell
# کپی .env.example به .env
Copy-Item .env.example .env
```

---

### مرحله 2: دریافت کلیدهای API

#### 🔴 **ضروری - Google AI** (رایگان)

1. برو به: https://aistudio.google.com/app/apikey
2. کلیک کن روی **"Create API Key"**
3. کلید را کپی کن
4. در `.env` قرار بده:

```dotenv
GOOGLE_API_KEY=AIzaSy_YOUR_ACTUAL_GOOGLE_KEY_HERE
```

---

#### 🔴 **ضروری - Groq** (رایگان، سریع)

1. برو به: https://console.groq.com/keys
2. Sign up / Login
3. **Create API Key**
4. کلید را کپی کن
5. در `.env` قرار بده:

```dotenv
GROQ_API_KEY=gsk_YOUR_ACTUAL_GROQ_KEY_HERE
```

---

#### 🟡 **اختیاری - OpenAI via OpenRouter** (پولی)

برای مدل‌های قدرتمند‌تر:

1. برو به: https://openrouter.ai/
2. Sign up
3. **Keys** → **Create Key**
4. در `.env` قرار بده:

```dotenv
OPENAI_API_KEY=sk-or-v1-YOUR_OPENROUTER_KEY
```

---

### مرحله 3: بررسی فایل `.env`

```powershell
# باز کردن فایل برای ویرایش
notepad .env

# یا با VS Code
code .env
```

**حداقل محتوای لازم:**

```dotenv
# ========================================
# Master AI Controller - Configuration
# ========================================

# 🔑 Google AI (Required - رایگان)
GOOGLE_API_KEY=AIzaSy...کلید_واقعی_خودت

# 🔑 Groq AI (Required - رایگان)
GROQ_API_KEY=gsk_...کلید_واقعی_خودت

# 🔑 OpenAI via OpenRouter (Optional)
# OPENAI_API_KEY=sk-or-v1-...کلید_اگه_داری

# ⚙️ Browser Settings
BROWSER_HEADLESS=1
```

**⚠️ مهم:**
- کلیدها را بدون فاصله و بدون `" "` وارد کنید
- فایل `.env` را هرگز push نکنید (در `.gitignore` است)

---

## 🎬 اجرای اولیه

### روش 1: حالت پایه (فقط AI Chat)

```powershell
# اجرای ساده
python main.py

# با نمایش لاگ‌های بیشتر
python main.py --debug
```

**انتظار می‌رود:**
```
📝 Logging Information:
   Session Log: data\logs\sessions\session_20251207_HHMMSS.log
   Master Log:  data\logs\master.log
   ✓ All outputs will be saved to these files

🧠 Master AI Controller enabled
```

---

### روش 2: با Automation (کنترل Desktop)

```powershell
# فعال‌سازی کنترل Mouse, Keyboard, Vision
python main.py --enable-automation
```

**انتظار می‌رود:**
```
✅ Desktop automation features enabled
   Features: Mouse Control, Keyboard Control, Smart Wait, Enhanced Vision, Action Controller
```

---

### روش 3: حالت Autonomous (هدف‌محور)

```powershell
# فعال‌سازی Autonomous Agent
python main.py --enable-automation --enable-autonomous
```

**انتظار می‌رود:**
```
✅ Desktop automation features enabled
✅ Autonomous Agent enabled - Use 'goal <description>' command
```

---

## ✅ دستورات تست آماده

### 🧪 **تست 1: بررسی اولیه سیستم**

```powershell
# اجرا
python main.py
```

**دستورات در CLI:**
```
سلام
```
انتظار: پاسخ دوستانه از AI

```
exit
```

**نتیجه موفق:** ✅ AI پاسخ داد، برنامه بدون خطا بسته شد

---

### 🧪 **تست 2: قابلیت‌های سیستمی**

```powershell
python main.py
```

**دستورات:**
```
اطلاعات CPU رو بده
```
انتظار: اطلاعات پردازنده (مدل، هسته‌ها، درصد استفاده)

```
RAM چقدره؟
```
انتظار: مقدار حافظه کل و استفاده شده

```
فضای دیسک چقدر داریم؟
```
انتظار: اطلاعات درایوها

```
exit
```

**نتیجه موفق:** ✅ اطلاعات سیستم به درستی نمایش داده شد

---

### 🧪 **تست 3: مدل‌های مختلف AI**

```powershell
python main.py --debug
```

**دستورات:**
```
Python چیست؟
```
انتظار: توضیح کامل درباره Python

```
تفاوت Java و C++ چیه؟
```
انتظار: مقایسه دو زبان

```
یک جوک بگو
```
انتظار: یک جوک طنز

```
exit
```

**در لاگ بررسی کنید:**
- کدام مدل استفاده شد؟ (normal, fast, system)
- آیا fallback رخ داد؟
- زمان پاسخ‌دهی چقدر بود؟

**نتیجه موفق:** ✅ مدل‌های مختلف کار می‌کنند، fallback عمل می‌کند

---

### 🧪 **تست 4: Desktop Automation**

```powershell
python main.py --enable-automation
```

**دستورات:**

#### Mouse Testing:
```
mouse position
```
انتظار: موقعیت فعلی موس (x, y)

#### Keyboard Testing (⚠️ ابتدا Notepad باز کنید):
```
باز کن notepad
```
صبر کنید Notepad باز شود، سپس:

```
type سلام دنیا
```
انتظار: بعد از 3 ثانیه، متن در Notepad تایپ می‌شود

```
exit
```

**نتیجه موفق:** ✅ Mouse و Keyboard کار می‌کنند

---

### 🧪 **تست 5: Application Control**

```powershell
python main.py --enable-automation
```

**دستورات:**
```
باز کن notepad
```
انتظار: Notepad باز می‌شود

```
باز کن calculator
```
انتظار: ماشین حساب باز می‌شود

```
بستن calc
```
انتظار: Calculator بسته می‌شود

```
exit
```

**نتیجه موفق:** ✅ برنامه‌ها باز و بسته می‌شوند

---

### 🧪 **تست 6: Autonomous Agent (پیشرفته)**

```powershell
python main.py --enable-automation --enable-autonomous
```

**دستورات:**

#### تست ساده:
```
goal باز کن This PC
```
انتظار: File Explorer باز می‌شود و به This PC می‌رود

#### تست ترکیبی:
```
goal برو به درایو E: و یک پوشه به نام TestFolder بساز
```
انتظار: 
1. File Explorer باز شود
2. به E: برود
3. پوشه TestFolder ساخته شود

```
exit
```

**نتیجه موفق:** ✅ اهداف به صورت خودکار اجرا می‌شوند

---

### 🧪 **تست 7: Rate Limit & Error Handling**

```powershell
python main.py
```

**دستورات (ارسال سریع):**
```
سلام
چه خبر؟
Python چیه؟
Java چیه؟
C++ چیه؟
JavaScript چیه؟
```

**انتظار:**
- ممکن است بعد از 5 درخواست، Google API rate limit بخورد
- سیستم باید به Groq fallback کند
- پیام هشدار نمایش داده شود

```
exit
```

**نتیجه موفق:** ✅ سیستم خطاها را مدیریت می‌کند و fallback کار می‌کند

---

### 🧪 **تست 8: Logging System**

```powershell
python main.py
```

**دستورات:**
```
سلام
چند تا سوال بپرس
exit
```

**بررسی لاگ‌ها:**

```powershell
# لیست session logs
Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending

# باز کردن آخرین لاگ
code (Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName

# بررسی master log
code data\logs\master.log
```

**چک کنید:**
- ✅ فایل session log ساخته شده است
- ✅ تمام تعاملات ثبت شده‌اند
- ✅ Timestamps دقیق هستند
- ✅ Master log شامل همه sessions است

**نتیجه موفق:** ✅ سیستم لاگ‌گیری کامل کار می‌کند

---

## 📊 تست جامع (All-in-One)

برای تست کامل تمام قابلیت‌ها:

```powershell
# اجرای کامل
python main.py --enable-automation --enable-autonomous --debug
```

**سناریوی تست کامل:**

```
# 1. تست Chat
سلام، حالت چطوره؟

# 2. تست System Info
CPU چقدره؟

# 3. تست AI Knowledge
Python چیه؟

# 4. تست Mouse
mouse position

# 5. تست Application
باز کن notepad

# 6. تست Keyboard (در Notepad)
type سلام از ایران

# 7. تست Autonomous
goal باز کن This PC

# 8. خروج
exit
```

**بررسی نهایی:**

```powershell
# باز کردن لاگ
code (Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
```

**چک‌لیست موفقیت:**
- ✅ تمام دستورات اجرا شدند
- ✅ هیچ ERROR جدی وجود ندارد
- ✅ لاگ کامل ثبت شده است
- ✅ برنامه به درستی بسته شد

---

## 🐛 عیب‌یابی

### مشکل 1: `ModuleNotFoundError`

**علت:** وابستگی‌ها نصب نشده‌اند

**راه حل:**
```powershell
pip install -r requirements.txt --upgrade
```

---

### مشکل 2: `Missing API Key`

**علت:** فایل `.env` وجود ندارد یا کلیدها اشتباه است

**راه حل:**
```powershell
# بررسی فایل
Test-Path .env

# اگر False:
Copy-Item .env.example .env
notepad .env
# کلیدها را اضافه کنید
```

---

### مشکل 3: `429 Rate Limit`

**علت:** خیلی سریع درخواست فرستاده‌اید (Google: 5 req/min)

**راه حل:**
- ⏱️ 1-2 دقیقه صبر کنید
- یا Groq API Key اضافه کنید (بدون محدودیت سخت)

---

### مشکل 4: `Permission Denied`

**علت:** Python نمی‌تواند فایل بسازد

**راه حل:**
```powershell
# اجرای PowerShell به عنوان Administrator
# یا اطمینان از دسترسی به پوشه
```

---

### مشکل 5: برنامه Crash می‌کند

**راه حل:**

```powershell
# اجرا با debug mode
python main.py --debug

# بررسی لاگ
code (Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName

# ارسال لاگ به GitHub Copilot برای تحلیل
```

---

## 📈 Workflow توصیه شده

### روزانه (روتین تست):

```powershell
# 1. بروزرسانی کد
git pull origin main

# 2. بروزرسانی packages
pip install -r requirements.txt --upgrade

# 3. پاکسازی لاگ‌های قدیمی (هر هفته)
Get-ChildItem data\logs\sessions\ | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | Remove-Item

# 4. اجرا و تست
python main.py --enable-automation
```

---

### پیش از گزارش مشکل:

```powershell
# 1. تست با debug
python main.py --debug

# 2. تکرار مشکل
# [انجام کاری که باعث خطا می‌شود]

# 3. ذخیره لاگ
$latestLog = Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Copy-Item $latestLog.FullName "bug_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# 4. ارسال فایل لاگ به Copilot یا تیم
```

---

## 🎓 نکات پیشرفته

### اجرا با پارامترهای مختلف:

```powershell
# Voice input (نیاز به میکروفون)
python main.py --input-mode voice

# Text-to-Speech فعال
python main.py --tts-provider gtts

# حالت browser
python main.py --mode browser

# Concurrency بالا
python main.py --concurrency 5

# ترکیبی
python main.py --enable-automation --enable-autonomous --debug --concurrency 3
```

---

### مانیتورینگ Real-time:

```powershell
# Terminal 1: اجرای برنامه
python main.py --debug

# Terminal 2: نمایش لاگ لحظه‌ای
Get-Content data\logs\master.log -Wait -Tail 50
```

---

## ✅ چک‌لیست نهایی

قبل از تست حرفه‌ای:

- [ ] Python 3.10+ نصب است
- [ ] وابستگی‌ها نصب شده‌اند (`pip list`)
- [ ] فایل `.env` وجود دارد و کلیدها صحیح هستند
- [ ] پوشه `data` پاک شده (برای شروع تمیز)
- [ ] اتصال اینترنت فعال است
- [ ] PowerShell/Terminal آماده است

**اگر همه ✅ است، آماده‌اید! 🚀**

---

## 📚 مستندات مرتبط

- 📄 **API_KEYS_SETUP.md** - راهنمای کامل API Keys
- 📄 **LOGGING_GUIDE.md** - راهنمای سیستم لاگ
- 📄 **README.md** - معرفی پروژه
- 📄 **CONTRIBUTING.md** - راهنمای مشارکت

---

**موفق باشید! 🎉**

اگر مشکلی پیش آمد، لاگ session را برای تحلیل ارسال کنید.

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: November 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
