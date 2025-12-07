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

echo ⚠️  This is a complete test and may take several minutes.
echo ⚠️  Some applications (Notepad, Calculator) will be launched.
echo.
echo Do you want to continue? (Y/N)
set /p continue=

if /i "%continue%" NEQ "Y" (
    echo.
    echo ❌ Test cancelled.
    echo.
    pause
    exit /b
)

echo.
echo 🚀 Running complete test...
echo.

python tests\test_master_controller_complete.py

echo.
echo ✅ Complete test finished!
echo.
echo 📊 Results are displayed above.
echo.
pause
