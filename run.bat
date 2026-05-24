@echo off
REM =====================================================
REM BOT TELE - Windows Run Script
REM Run bot from virtual environment
REM =====================================================

setlocal enabledelayedexpansion

REM Check if venv exists
if not exist venv (
    echo ❌ Virtual environment not found!
    echo    Please run setup.bat first
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo ❌ .env file not found!
    echo    Please create .env with your Telegram API credentials
    echo    Copy from .env.example and fill in your details
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Clear screen
cls

REM Print header
echo.
echo ======================================
echo 🚀 BOT TELE v3.9 - STARTING
echo ======================================
echo.
echo 📍 Virtual Environment: ACTIVE
echo 📦 Python: 
python --version
echo.
echo ⏳ Initializing bot...
echo.

REM Run the bot
python main_script.py

REM If bot exits, show message
if errorlevel 1 (
    echo.
    echo ❌ Bot exited with error
    echo    Check logs/bot_activity.log for details
    pause
)
