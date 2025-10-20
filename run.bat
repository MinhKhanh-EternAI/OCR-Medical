@echo off
echo ============================================================
echo 🚀 Launching OCR-Medical Application
echo ============================================================

REM --- Activate environment ---
where conda >nul 2>nul
if %errorlevel%==0 (
    call conda activate ocr-medical
) else (
    call venv\Scripts\activate
)

REM --- Run main ---
python ocr_medical\main.py

echo ============================================================
echo 🏁 Application closed
echo ============================================================
pause
