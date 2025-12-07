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

REM Create log directory if not exists
if not exist "data\logs" mkdir data\logs

REM Generate timestamp for log filename
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set timestamp=%datetime:~0,8%_%datetime:~8,6%
set logfile=data\logs\complete_test_%timestamp%.log

echo 📝 Log file: %logfile%
echo.

REM Run test and save output to log file
python tests\test_master_controller_complete.py > %logfile% 2>&1

REM Display the log file content
type %logfile%

echo.
echo ✅ Complete test finished!
echo.
echo 📊 Results are displayed above.
echo 💾 Full results saved to: %logfile%
echo.
pause
