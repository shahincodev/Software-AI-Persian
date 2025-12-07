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

echo 🚀 Running quick test...
echo.

REM Create log directory if not exists
if not exist "data\logs" mkdir data\logs

REM Generate timestamp for log filename
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set timestamp=%datetime:~0,8%_%datetime:~8,6%
set logfile=data\logs\quick_test_%timestamp%.log

echo 📝 Log file: %logfile%
echo.

REM Run test and save output to log file
python tests\quick_test_master.py > %logfile% 2>&1

REM Display the log file content
type %logfile%

echo.
echo ✅ Test completed!
echo 💾 Results saved to: %logfile%
echo.
pause
