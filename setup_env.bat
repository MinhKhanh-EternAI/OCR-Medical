@echo off
echo ===========================================================
echo 🚀 SETUP ENVIRONMENT FOR OCR-MEDICAL / ENHANCER-IMAGE
echo ===========================================================
echo.

:: Detect Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+ and add to PATH.
    pause
    exit /b
)

echo ✅ Python detected.

:: Create virtual environment (if not exist)
if not exist .venv (
    echo 🌀 Creating virtual environment...
    python -m venv .venv
) else (
    echo ♻️ Virtual environment already exists.
)

:: Activate venv
call .venv\Scripts\activate

:: Upgrade pip
python -m pip install --upgrade pip

:: Install dependencies
if exist requirements.txt (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
) else (
    echo ⚠️ requirements.txt not found! Skipping dependency install.
)

:: Test Waifu2x loader
echo.
echo 🧠 Testing Waifu2x Loader...
python -m core.waifu2x_loader

if %errorlevel% neq 0 (
    echo ❌ Waifu2x test failed.
) else (
    echo ✅ Waifu2x loaded successfully.
)

echo.
echo ===========================================================
echo 🎉 SETUP COMPLETE! To start the app, run:
echo.
echo     run_app.bat
echo ===========================================================
pause
