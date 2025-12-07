# 🧪 دستورات تست آماده - Software-AI

این فایل شامل تمام دستورات تست به صورت خالص است (بدون توضیحات).
فقط کپی و paste کنید.

---

## 📦 آماده‌سازی اولیه

```powershell
# بروزرسانی repository
git pull origin main

# نصب/بروزرسانی packages
pip install -r requirements.txt --upgrade

# پاکسازی data قدیمی
if (Test-Path "data") { Remove-Item -Path "data" -Recurse -Force }

# بررسی .env
if (-not (Test-Path ".env")) { Copy-Item .env.example .env; notepad .env }
```

---

## 🧪 تست 1: اجرای پایه

```powershell
python main.py
```

**دستورات:**
```
سلام
exit
```

---

## 🧪 تست 2: سیستم Info

```powershell
python main.py
```

**دستورات:**
```
اطلاعات CPU رو بده
RAM چقدره؟
فضای دیسک چقدر داریم؟
exit
```

---

## 🧪 تست 3: AI Knowledge

```powershell
python main.py --debug
```

**دستورات:**
```
Python چیست؟
تفاوت Java و C++ چیه؟
یک جوک بگو
exit
```

---

## 🧪 تست 4: Desktop Automation

```powershell
python main.py --enable-automation
```

**دستورات:**
```
mouse position
باز کن notepad
type سلام دنیا
exit
```

---

## 🧪 تست 5: Application Control

```powershell
python main.py --enable-automation
```

**دستورات:**
```
باز کن notepad
باز کن calculator
بستن calc
exit
```

---

## 🧪 تست 6: Autonomous Agent

```powershell
python main.py --enable-automation --enable-autonomous
```

**دستورات:**
```
goal باز کن This PC
goal برو به درایو E: و یک پوشه به نام TestFolder بساز
exit
```

---

## 🧪 تست 7: Rate Limit Testing

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
exit
```

---

## 🧪 تست 8: تست جامع (All-in-One)

```powershell
python main.py --enable-automation --enable-autonomous --debug
```

**دستورات:**
```
سلام، حالت چطوره؟
CPU چقدره؟
Python چیه؟
mouse position
باز کن notepad
type سلام از ایران
goal باز کن This PC
exit
```

---

## 📊 بررسی لاگ‌ها

```powershell
# لیست session logs
Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending

# باز کردن آخرین session log
code (Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName

# نمایش master log
code data\logs\master.log

# کپی آخرین لاگ به clipboard
Get-Content (Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName | Set-Clipboard

# ذخیره لاگ برای bug report
$latestLog = Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Copy-Item $latestLog.FullName "bug_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
```

---

## 🔍 تحلیل سریع لاگ

```powershell
# تعداد خطاها
(Get-Content (Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName | Select-String "ERROR").Count

# تعداد هشدارها
(Get-Content (Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName | Select-String "WARNING").Count

# نمایش فقط خطاها
Get-Content (Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName | Select-String "ERROR|CRITICAL"

# نمایش 20 خط اول
Get-Content (Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName -Head 20

# نمایش 20 خط آخر
Get-Content (Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName -Tail 20
```

---

## 🧹 پاکسازی

```powershell
# حذف session logs قدیمی‌تر از 7 روز
Get-ChildItem data\logs\sessions\ | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | Remove-Item

# حذف کل data directory
Remove-Item -Path "data" -Recurse -Force

# فقط حذف لاگ‌ها
Remove-Item -Path "data\logs\*" -Recurse -Force
```

---

## 🚀 دستورات سریع روزانه

```powershell
# Workflow کامل
git pull origin main
pip install -r requirements.txt --upgrade
if (Test-Path "data") { Remove-Item -Path "data" -Recurse -Force }
python main.py --enable-automation --debug
```

---

## 📤 ارسال لاگ به Copilot

```powershell
# باز کردن آخرین لاگ در VS Code
code (Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName

# یا کپی به clipboard
Get-Content (Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName | Set-Clipboard

# سپس در GitHub Copilot Chat بنویس:
# "لاگ کامل اجرای برنامه را می‌فرستم، لطفاً تحلیل کن و مشکلات را شناسایی کن:"
# [Ctrl+V paste log]
```

---

## 💡 Aliases مفید (اضافه کنید به PowerShell Profile)

```powershell
# باز کردن PowerShell Profile
notepad $PROFILE

# اضافه کردن این aliases:
function ai-run { python main.py --enable-automation --enable-autonomous --debug }
function ai-test { python main.py }
function ai-log { code (Get-ChildItem data\logs\sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName }
function ai-clean { Remove-Item -Path "data" -Recurse -Force }
function ai-update { git pull origin main; pip install -r requirements.txt --upgrade }

# بعد از ذخیره، reload کنید:
. $PROFILE

# حالا می‌توانید استفاده کنید:
# ai-run    → اجرای کامل
# ai-test   → اجرای ساده
# ai-log    → باز کردن آخرین لاگ
# ai-clean  → پاکسازی data
# ai-update → بروزرسانی پروژه
```

---

**موفق باشید! 🎉**

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: November 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION
