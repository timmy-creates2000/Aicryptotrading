@echo off
REM Quick start script for Windows

echo.
echo ===================================
echo   Crypto Trading Bot - Quick Start
echo ===================================
echo.

REM Check if venv exists
if not exist "env\" (
    echo Creating virtual environment...
    python -m venv env
)

REM Activate venv
echo Activating virtual environment...
call env\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt -q

REM Check if .env exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Creating from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env and add your API keys:
    echo   - BYBIT_API_KEY
    echo   - BYBIT_API_SECRET
    echo   - GEMINI_API_KEY
    echo   - TELEGRAM_BOT_TOKEN
    echo   - TELEGRAM_CHAT_ID
    echo.
    pause
)

REM Start bot
echo.
echo Starting crypto trading bot...
echo.
python main.py

pause
