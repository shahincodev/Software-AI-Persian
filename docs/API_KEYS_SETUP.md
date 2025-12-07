# 🔑 راهنمای تنظیم API Keys

این راهنما نحوه تنظیم کلیدهای API برای استفاده از Master AI Controller را توضیح می‌دهد.

## 📋 فهرست مطالب
- [پیش‌نیازها](#پیش‌نیازها)
- [مراحل تنظیم](#مراحل-تنظیم)
- [دریافت API Keys](#دریافت-api-keys)
- [تست پیکربندی](#تست-پیکربندی)
- [عیب‌یابی](#عیب‌یابی)

---

## 🎯 پیش‌نیازها

برای استفاده کامل از Master AI Controller به کلیدهای API زیر نیاز دارید:

### ضروری (Essential):
- ✅ **Google API Key** - برای مدل‌های هوش مصنوعی اصلی
- ✅ **Groq API Key** - برای مدل‌های سریع

### اختیاری (Optional):
- ⚪ **OpenAI API Key** - برای مدل‌های GPT (اختیاری)
- ⚪ **Browser Use API Key** - برای عملیات مرورگر
- ⚪ **ElevenLabs API Key** - برای تبدیل متن به گفتار با کیفیت بالا

---

## 🚀 مراحل تنظیم

### مرحله 1: کپی فایل نمونه

**PowerShell:**
```powershell
Copy-Item .env.example .env
```

**یا به صورت دستی:**
1. فایل `.env.example` را کپی کنید
2. نام آن را به `.env` تغییر دهید

---

### مرحله 2: ویرایش فایل .env

فایل `.env` را با یک ویرایشگر متن باز کنید:

```powershell
notepad .env
```

یا با VS Code:
```powershell
code .env
```

---

### مرحله 3: اضافه کردن کلیدهای API

در فایل `.env` کلیدهای واقعی خود را جایگزین کنید:

```dotenv
# ✅ REQUIRED - Google API Key
GOOGLE_API_KEY=AIzaSy_YOUR_ACTUAL_GOOGLE_API_KEY_HERE

# ✅ REQUIRED - Groq API Key
GROQ_API_KEY=gsk_YOUR_ACTUAL_GROQ_API_KEY_HERE

# ⚪ OPTIONAL - OpenAI API Key
OPENAI_API_KEY=sk-YOUR_OPENAI_KEY_IF_YOU_HAVE_ONE

# ⚪ OPTIONAL - Browser Use API Key
BROWSER_USE_API_KEY=bu_YOUR_BROWSER_USE_KEY_IF_NEEDED
```

**⚠️ نکات مهم:**
- کلیدها را بدون فاصله و بدون علامت نقل قول وارد کنید
- فایل `.env` را **هرگز** به Git push نکنید (در `.gitignore` است)
- کلیدهای خود را با کسی به اشتراک نگذارید

---

## 🔑 دریافت API Keys

### 1. Google API Key (ضروری)

**گام 1:** به Google AI Studio بروید
```
https://aistudio.google.com/app/apikey
```

**گام 2:** روی "Create API Key" کلیک کنید

**گام 3:** کلید ایجاد شده را کپی کنید

**گام 4:** در فایل `.env` قرار دهید:
```dotenv
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXX
```

---

### 2. Groq API Key (ضروری)

**گام 1:** به سایت Groq بروید
```
https://console.groq.com/keys
```

**گام 2:** ثبت نام کنید یا وارد شوید

**گام 3:** یک API Key جدید ایجاد کنید

**گام 4:** کلید را کپی کرده و در `.env` قرار دهید:
```dotenv
GROQ_API_KEY=gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**💡 مزیت Groq:** مدل‌های رایگان با سرعت بالا!

---

### 3. OpenAI API Key (اختیاری)

**گام 1:** به OpenAI Platform بروید
```
https://platform.openai.com/api-keys
```

**گام 2:** "Create new secret key" را کلیک کنید

**گام 3:** کلید را کپی کنید (فقط یک بار نمایش داده می‌شود!)

**گام 4:** در `.env` اضافه کنید:
```dotenv
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**⚠️ توجه:** OpenAI API پولی است و نیاز به اعتبار دارد.

---

## ✅ تست پیکربندی

بعد از تنظیم کلیدها، تست کنید:

### تست سریع:
```powershell
.\quick_test.bat
```

### تست کامل:
```powershell
.\complete_test.bat
```

**نتایج مورد انتظار:**
- ✅ نباید خطای "Missing API Key" ببینید
- ✅ تست‌ها باید با موفقیت اجرا شوند
- ✅ مدل‌های AI باید پاسخ بدهند

---

## 🐛 عیب‌یابی

### مشکل: "Missing key inputs argument"

**علت:** Google API Key تنظیم نشده است

**راه حل:**
```powershell
# بررسی فایل .env
Get-Content .env | Select-String "GOOGLE_API_KEY"

# باید چیزی شبیه این ببینید:
# GOOGLE_API_KEY=AIzaSy...
```

اگر خالی است:
1. فایل `.env` را باز کنید
2. کلید Google را اضافه کنید
3. فایل را ذخیره کنید
4. دوباره تست کنید

---

### مشکل: "Unknown message type"

**علت:** فرمت پیام به AI اشتباه است

**راه حل:** مطمئن شوید که:
1. فایل `.env` در ریشه پروژه است (کنار `main.py`)
2. کلیدها بدون فاصله اضافی وارد شده‌اند
3. کلیدها معتبر هستند (منقضی نشده‌اند)

---

### مشکل: "All models failed"

**علت:** هیچ کلید API معتبری پیدا نشد

**بررسی:**
```powershell
# چک کنید که فایل .env وجود دارد
Test-Path .env

# باید True برگرداند
```

اگر False است:
```powershell
Copy-Item .env.example .env
notepad .env
# کلیدها را اضافه کنید
```

---

### مشکل: "API call failed after 0.00s"

**علت:** کلید API نامعتبر یا منقضی شده

**راه حل:**
1. به سایت مربوطه بروید
2. کلید جدیدی ایجاد کنید
3. در `.env` جایگزین کنید
4. دوباره تست کنید

---

## 📝 نمونه فایل .env کامل

```dotenv
# ========================================
# Master AI Controller - Configuration
# ========================================

# 🔑 Google AI (Required)
GOOGLE_API_KEY=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI

# 🔑 Groq AI (Required)
GROQ_API_KEY=gsk_aBc123XyZ789DeF456GhI012JkL345

# 🔑 OpenAI (Optional)
OPENAI_API_KEY=sk-proj-AbC123XyZ789...

# 🔑 Browser Use (Optional)
BROWSER_USE_API_KEY=bu_1234567890abcdef

# 🔑 ElevenLabs TTS (Optional)
ELEVENLABS_API_KEY=your_elevenlabs_key_here

# ⚙️ Browser Settings
BROWSER_HEADLESS=1

# ⚙️ Google Cloud (Optional)
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# ⚙️ Tesseract OCR (Optional)
TESSERACT_PATH=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
```

---

## 🎉 بعد از تنظیم موفق

بعد از اینکه همه چیز کار کرد:

1. ✅ فایل `.env` را **backup** کنید (در یک مکان امن)
2. ✅ هرگز `.env` را به Git اضافه نکنید
3. ✅ در صورت به اشتراک گذاری کد، فقط `.env.example` را ارسال کنید

---

## 🆘 نیاز به کمک؟

اگر مشکلی داشتید:
1. لاگ‌های تست را بررسی کنید: `data/logs/`
2. مطمئن شوید که فایل `.env` در همان پوشه `main.py` است
3. کلیدها را در سایت‌های مربوطه دوباره ایجاد کنید

---

**✨ موفق باشید!**

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: November 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
