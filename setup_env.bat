@echo off
echo ============================================================
echo Setting up OCR-Medical environment
echo ============================================================

REM --- Check conda available ---
where conda >nul 2>nul
if %errorlevel%==0 (
    echo Conda detected. Creating environment...
    call conda create -y -n ocr-medical python=3.10
    call conda activate ocr-medical
) else (
    echo ⚠️ Conda not found. Using venv instead...
    python -m venv venv
    call venv\Scripts\activate
)

REM --- Install requirements ---
echo Installing dependencies from requirements.txt...
pip install --upgrade pip
pip install -r requirements.txt

echo ============================================================
echo Environment setup completed!
echo To start the app, run:  run_app.bat
echo ============================================================
pause
