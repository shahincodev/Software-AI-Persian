# Software-AI Demo Guide

## نحوه اجرای دمو برای ویدئو

### 1. حالت پایه (Basic)
```bash
python main.py
```
- تنها قابلیت‌های اصلی فعال است
- برای تست سریع مناسب است

### 2. حالت کامل (Full Features)
```bash
python main.py --full
```
- تمام قابلیت‌ها فعال می‌شوند:
  - Desktop Automation
  - Autonomous Agent
  - Intent Planning System

### 3. حالت Intent Planning (پیشنهادی برای دمو)
```bash
python main.py --intent-planning
```
- فقط سیستم برنامه‌ریزی هوشمند فعال است
- بهترین گزینه برای نمایش هوش مصنوعی

### 4. حالت Debug (برای توسعه)
```bash
python main.py --full --debug
```
- تمام قابلیت‌ها + لاگ‌های کامل

---

## دستورات دمو (Demo Commands)

### Intent Planning System
```
plan open notepad
plan create a folder on desktop
plan install python
stats
```

### Autonomous Agent
```
goal go to E: and create MyDocs folder
goal open This PC
```

### Desktop Automation
```
mouse position
type Hello World
vision screenshot
```

### Core Commands
```
help
clear
exit
```

---

## سناریوی پیشنهادی برای ویدئو

### مرحله 1: نمایش صفحه اول (30 ثانیه)
```bash
python main.py --intent-planning
```
- نمایش بنر زیبا
- نمایش لیست قابلیت‌ها
- نمایش دستورات موجود

### مرحله 2: تست Intent Planning (60 ثانیه)
```
plan open notepad
```
- نمایش 5 مرحله تحلیل:
  1. Analyzing intent
  2. Checking completeness
  3. Generating plan
  4. Validating plan
  5. Recording to memory

### مرحله 3: نمایش آمار (20 ثانیه)
```
stats
```
- نمایش آمار اجرا
- Success rate
- Execution time

### مرحله 4: تست دستور دیگر (40 ثانیه)
```
plan create a folder on desktop
```

### مرحله 5: خروج حرفه‌ای (10 ثانیه)
```
exit
```
- نمایش خلاصه session
- نمایش مسیر لاگ‌ها

**مجموع زمان: 2:40 دقیقه**

---

## نکات مهم برای ضبط ویدئو

1. ✅ **Terminal را Fullscreen کنید**
2. ✅ **Font را بزرگ کنید** (برای خوانایی)
3. ✅ **رنگ‌ها را تست کنید** (Colorama باید فعال باشد)
4. ✅ **قبل از ضبط یکبار تمرین کنید**
5. ✅ **از حالت `--debug` برای ویدئو استفاده نکنید** (خیلی شلوغ می‌شود)

---

## مشکلات احتمالی و راه‌حل

### مشکل: رنگ‌ها نمایش داده نمی‌شوند
```bash
pip install colorama
```

### مشکل: خطای import
```bash
pip install -r requirements.txt
```

### مشکل: دیتابیس قفل است
```bash
# حذف دیتابیس قبلی
rm data/memories.sqlite3
```

---

## تنظیمات Terminal پیشنهادی

### PowerShell
```powershell
# اندازه پنجره
$Host.UI.RawUI.WindowSize = New-Object Management.Automation.Host.Size(120, 30)

# رنگ پس‌زمینه
$Host.UI.RawUI.BackgroundColor = "Black"
```

### Font Size
- **حداقل**: 14pt
- **پیشنهادی**: 16pt یا 18pt

---

## چک‌لیست قبل از ضبط

- [ ] تمام dependencies نصب شده‌اند
- [ ] Terminal در حالت Fullscreen است
- [ ] Font size مناسب است
- [ ] رنگ‌ها به درستی نمایش داده می‌شوند
- [ ] Microphone خاموش است (برای جلوگیری از صدای کیبورد)
- [ ] Screen recording software آماده است
- [ ] یکبار تمرین کرده‌اید

---

**موفق باشید!** 🎥✨
