# 🧪 راهنمای تست Master AI Controller

این پوشه شامل تست‌های جامع برای Master AI Controller است.

---

## 🚀 روش‌های اجرا

### 1️⃣ تست سریع (توصیه می‌شود برای شروع)

**Windows:**
```bash
quick_test.bat
```

**یا:**
```bash
python tests/quick_test_master.py
```

**زمان اجرا:** ~30 ثانیه  
**تعداد تست:** 5 تست اصلی

---

### 2️⃣ تست کامل

**Windows:**
```bash
complete_test.bat
```

**یا:**
```bash
python tests/test_master_controller_complete.py
```

**زمان اجرا:** 5-10 دقیقه  
**تعداد تست:** 25+ تست جامع

⚠️ **توجه:** برنامه‌هایی مثل Notepad و Calculator باز می‌شوند!

---

### 3️⃣ تست دستی با main.py

```bash
python main.py --enable-automation
```

بعد از اجرا، دستورات زیر رو تست کن:

```
سلام
CPU چقدره؟
باز کن notepad
هوش مصنوعی چیست؟
```

---

## 📋 فایل‌های تست

| فایل | توضیحات | تعداد تست |
|------|---------|----------|
| `quick_test_master.py` | تست سریع قابلیت‌های اصلی | 5 تست |
| `test_master_controller_complete.py` | تست جامع تمام سناریوها | 25+ تست |
| `test_master_controller.py` | تست اولیه routing | 5 تست |

---

## 📊 خروجی تست‌ها

### تست سریع:

```
🧪 تست: گفتگو ساده
   👤 درخواست: "سلام، حالت چطوره؟"
   🔧 ابزار: chat
   ✅ موفقیت: بله
   💬 پاسخ: سلام! من یک دستیار هوش مصنوعی هستم...
```

### تست کامل:

```
📊 خلاصه نتایج تست
═══════════════════════════════════════════

📝 تعداد کل تست‌ها: 25
✅ تست‌های موفق: 23
❌ تست‌های ناموفق: 2
📈 درصد موفقیت: 92.0%

Progress: [████████████████████████████████████░░░░] 92.0%
```

---

## 🎯 دستورات تست آماده

برای تست دستی، از این دستورات استفاده کن:

### CHAT (گفتگو):
```
سلام، حالت چطوره؟
هوش مصنوعی چیست؟
تفاوت Python و Java چیه؟
```

### SYSTEM (اطلاعات سیستم):
```
CPU چقدره؟
چقدر RAM دارم؟
فضای دیسک چقدره؟
```

### DESKTOP (کنترل دسکتاپ):
```
باز کن notepad
اجرا کن Calculator
باز کن This PC
```

📖 **لیست کامل:** [MASTER_CONTROLLER_TEST_COMMANDS.md](../docs/MASTER_CONTROLLER_TEST_COMMANDS.md)

---

## ✅ چک‌لیست قبل از تست

- [ ] Python 3.8+ نصب است
- [ ] Dependencies نصب شده (`pip install -r requirements.txt`)
- [ ] فایل `.env` با API keys موجود است
- [ ] اتصال اینترنت برقرار است

---

## 🐛 مشکلات رایج

### ❌ خطا: "Missing key inputs argument"

**راه‌حل:** API keys را در `.env` ست کنید:
```env
GOOGLE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### ❌ خطا: "ModuleNotFoundError"

**راه‌حل:**
```bash
pip install -r requirements.txt
```

### ❌ همه تست‌ها fail می‌شوند

**راه‌حل:**
1. Debug mode را فعال کنید
2. لاگ‌ها را در `data/logs/` بررسی کنید
3. اتصال اینترنت را چک کنید

---

## 📈 معیارهای موفقیت

| درصد موفقیت | وضعیت | اقدام |
|-------------|-------|-------|
| 90%+ | 🟢 عالی | همه چیز عالیه! |
| 70-90% | 🟡 خوب | نیاز به بهبود جزئی |
| <70% | 🔴 ضعیف | بررسی کامل لازم است |

---

## 🔥 Quick Start (شروع سریع)

اگر عجله داری:

```bash
# Windows
quick_test.bat

# Linux/Mac
python tests/quick_test_master.py
```

اگر تمام 5 تست موفق بود = Master Controller سالمه! ✅

---

## 📞 گزارش مشکل

اگر مشکلی پیدا کردی:

1. لاگ‌ها را ذخیره کن (`data/logs/`)
2. در GitHub Issue بساز
3. فایل لاگ و دستورات تست را ضمیمه کن

---

## 💡 نکته مهم

**اولین بار تست می‌کنی؟**

از `quick_test.bat` شروع کن. اگر همه چیز کار کرد، بعد `complete_test.bat` رو اجرا کن.

---

<div align="center">

**ساخته شده برای تست Master AI Controller v1.1.0**

[📚 مستندات کامل](../docs/MASTER_CONTROLLER.md) | [📝 دستورات تست](../docs/MASTER_CONTROLLER_TEST_COMMANDS.md)

</div>
