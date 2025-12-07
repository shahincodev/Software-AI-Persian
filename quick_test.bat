@echo off
REM ====================================
REM Master AI Controller - Quick Test
REM ====================================

chcp 65001 >nul
cls

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║       🧠 Master AI Controller - Quick Test 🧪           ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo.

echo 🚀 در حال اجرای تست سریع...
echo.

python tests\quick_test_master.py

echo.
echo ✅ تست تمام شد!
echo.
pause
