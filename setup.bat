@echo off
REM =====================================================
REM BOT TELE - Windows Setup Script
REM Setup venv + install all requirements
REM =====================================================

setlocal enabledelayedexpansion

echo.
echo ======================================
echo 🚀 BOT TELE - WINDOWS SETUP
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is NOT installed!
    echo    Please install Python 3.9+ from: https://www.python.org
    echo    Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found: 
python --version

REM Create virtual environment
echo.
echo 📦 Creating virtual environment...
if exist venv (
    echo ⚠️  venv folder already exists
    set /p DELETE_VENV="Delete existing venv? (y/n): "
    if /i "!DELETE_VENV!"=="y" (
        echo Removing old venv...
        rmdir /s /q venv >nul 2>&1
    )
)

python -m venv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment created

REM Activate virtual environment
echo.
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo 📦 Upgrading pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1

REM Install requirements
echo.
echo 📥 Installing required packages...
echo    This may take a few minutes...
echo.

pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)

REM Install Playwright browsers
echo.
echo 🎬 Installing Playwright Firefox browser...
python -m playwright install firefox
if errorlevel 1 (
    echo ⚠️  Warning: Playwright browser installation may have issues
    echo    This is usually not critical
)

REM Create necessary directories
echo.
echo 📁 Creating directories...
if not exist logs mkdir logs
if not exist data mkdir data
if not exist HoSo_Bot_Vip mkdir HoSo_Bot_Vip

echo ✅ Directories created

REM Create .env file if not exists
echo.
echo 📝 Checking configuration...
if not exist .env (
    echo ⚠️  .env file not found
    echo    Creating from .env.example...
    
    if exist .env.example (
        copy .env.example .env >nul
        echo ✅ .env created from .env.example
        echo    Please edit .env with your credentials!
    ) else (
        echo ❌ .env.example not found
        echo    Please create .env manually with your Telegram API credentials
    )
) else (
    echo ✅ .env file already exists
)

REM Summary
echo.
echo ======================================
echo ✅ SETUP COMPLETE!
echo ======================================
echo.
echo 📌 Next Steps:
echo    1. Edit .env file with your Telegram API credentials
echo    2. Run: run.bat
echo.
echo 📖 For detailed instructions, see SETUP_GUIDE.md
echo.

pause
