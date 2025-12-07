@echo off
REM ====================================
REM Master AI Controller - Complete Test
REM ====================================

chcp 65001 >nul
cls

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║    🧠 Master AI Controller - Complete Test Suite 🧪    ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo.

echo ⚠️  این تست کامل است و ممکن است چند دقیقه طول بکشد.
echo ⚠️  برخی برنامه‌ها (Notepad, Calculator) باز خواهند شد.
echo.
echo آیا ادامه می‌دهید؟ (Y/N)
set /p continue=

if /i "%continue%" NEQ "Y" (
    echo.
    echo ❌ تست لغو شد.
    echo.
    pause
    exit /b
)

echo.
echo 🚀 در حال اجرای تست کامل...
echo.

python tests\test_master_controller_complete.py

echo.
echo ✅ تست کامل تمام شد!
echo.
echo 📊 نتایج در بالا نمایش داده شده است.
echo.
pause
