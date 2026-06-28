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

mkdir "%SCRIPT_DIR%data\logs\cache" 2>NUL

echo Launching Software-AI...
python "%SCRIPT_DIR%main.py" %*

if errorlevel 1 (
    echo.
    echo Re-running with debug flags...
    python "%SCRIPT_DIR%main.py" --debug %*
)

if defined VIRTUAL_ENV (
    deactivate 2>NUL
)

exit /B %ERRORLEVEL%
