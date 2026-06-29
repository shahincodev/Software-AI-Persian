@echo off
chcp 65001 >NUL
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"

if not exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
    echo Creating virtual environment .venv...
    python -m venv "%SCRIPT_DIR%.venv" 2>NUL || python3 -m venv "%SCRIPT_DIR%.venv"
)

call "%SCRIPT_DIR%.venv\Scripts\activate.bat"

python -m pip install --upgrade pip >NUL 2>&1
if exist "%SCRIPT_DIR%requirements.txt" (
    echo Installing requirements...
    python -m pip install -r "%SCRIPT_DIR%requirements.txt"
)

if not exist "%SCRIPT_DIR%.env" (
    if exist "%SCRIPT_DIR%.env.example" (
        copy "%SCRIPT_DIR%.env.example" "%SCRIPT_DIR%.env" >NUL
        echo Created .env from .env.example. Edit it with your API keys before use.
    ) else (
        echo Warning: .env not found and .env.example not present.
    )
)

REM Check for placeholder API keys in .env
if exist "%SCRIPT_DIR%.env" (
    findstr /C:"sk-your" "%SCRIPT_DIR%.env" >NUL 2>&1
    if not errorlevel 1 (
        echo [WARNING] Placeholder API keys detected in .env
        echo [WARNING] Edit .env and replace placeholder keys with real ones.
        echo [WARNING] See .env.example for instructions.
    )
    findstr /C:"YOUR_" "%SCRIPT_DIR%.env" >NUL 2>&1
    if not errorlevel 1 (
        echo [WARNING] Placeholder API keys detected in .env
        echo [WARNING] Edit .env and replace placeholder keys with real ones.
    )
)

mkdir "%SCRIPT_DIR%data\logs\cache" 2>NUL

echo Launching Software-AI...
python "%SCRIPT_DIR%main.py" %*
set "EXIT_CODE=%ERRORLEVEL%"

if %EXIT_CODE% neq 0 (
    echo.
    echo [HINT] If you see authentication errors, check your API keys in .env
    echo [HINT] Run: python main.py --debug to see detailed logs
)

exit /B %EXIT_CODE%

if defined VIRTUAL_ENV (
    deactivate 2>NUL
)

exit /B %ERRORLEVEL%
