@echo off
echo ===========================================================
echo 🩺 RUNNING OCR-MEDICAL APPLICATION
echo ===========================================================

:: Activate virtual environment
if exist .venv (
    call .venv\Scripts\activate
) else (
    echo ❌ Virtual environment not found. Please run setup_env.bat first.
    pause
    exit /b
)

:: Run main
python main.py
pause
