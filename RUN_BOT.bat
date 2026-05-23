@echo off
chcp 65001 > nul
title 🤖 Bot San Code - Firefox v3.9

cd /d "%~dp0"
cls

echo.
echo ============================================================
echo       🤖 BOT SĂN CODE - FIREFOX v3.9
echo ============================================================
echo.
echo ✨ FEATURES:
echo   ✓ Firefox persistent profiles
echo   ✓ Desktop viewport 1024x768
echo   ✓ Cookies lưu được (reuse profiles)
echo   ✓ Database tracking
echo   ✓ Rate limiting
echo   ✓ Stealth mode + Fingerprint spoofing
echo   ✓ 100%% AUTO-SUBMIT
echo   ✓ Nhanh 5x (3-5s mở browser)
echo.
echo 📍 IMPORTANT:
echo   - Firefox profiles PERSISTENT
echo   - Saved at: HoSo_Bot_Vip/browser_profiles/username/
echo   - Cookies auto lưu + restore
echo   - Desktop viewport (không bị ẩn form)
echo   - Delay tối ưu: 0.8s (TỐC ĐỘ MAX)
echo.

echo ⏳ Chờ 3 giây...
timeout /t 3 /nobreak

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ============================================================
    echo ❌ ERROR: Python không được cài đặt hoặc không trong PATH
    echo ============================================================
    echo.
    echo Hãy cài đặt Python từ: https://www.python.org/downloads/
    echo Chắc chắn chọn "Add Python to PATH" khi cài
    echo.
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

REM Check/Create virtual environment
if exist venv\ (
    echo ✅ VENV found
) else (
    echo ⚙️  Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create VENV
        pause
        exit /b 1
    )
    echo ✅ VENV created
)

echo.
echo ✅ Activating VENV...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate VENV
    pause
    exit /b 1
)

echo.
echo 📥 Installing/Updating requirements...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)

echo ✅ Requirements installed
echo.

echo 📥 Installing Playwright browsers (Firefox)...
playwright install firefox
if errorlevel 1 (
    echo ❌ Failed to install Playwright Firefox
    pause
    exit /b 1
)

echo ✅ Playwright Firefox installed
echo.

echo ============================================================
echo      🚀 BOT STARTING - FIREFOX v3.9
echo ============================================================
echo.
echo ⏱️  Build: 2026-05-22
echo 🎯 Browser: Firefox (tối ưu CF bypass)
echo 📊 ViewPort: 1024x768 (Desktop)
echo 🍪 Profiles: Persistent + Cookies lưu được
echo 💨 Speed: 3-5s mở browser (fast 5x)
echo.
echo 📍 LẦN ĐẦU TIÊN:
echo   1. Chạy: python setup_profiles.py
echo   2. Tích checkbox + test form
echo   3. Rồi chạy bot bình thường
echo.
echo 📡 Listening to Telegram channels...
echo.

python run.py

echo.
echo ============================================================
echo 🛑 Bot stopped
echo ============================================================
pause