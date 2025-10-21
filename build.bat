@echo off
chcp 65001 >nul
echo ===========================================================
echo 🚀 Building OCR-Medical Executable with PyInstaller
echo ===========================================================

set NAME=OCR-Medical
set ICON=ocr_medical\assets\logo\logo.ico
set MAIN=main.py
set DIST=dist
set EXE_PATH=%DIST%\%NAME%.exe

REM === Xóa build cũ ===
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q "%NAME%.spec" 2>nul

REM === Build bằng PyInstaller ===
pyinstaller ^
    --name "%NAME%" ^
    --onefile ^
    --noconsole ^
    --icon "%ICON%" ^
    --add-data "ocr_medical/assets;ocr_medical/assets" ^
    --add-data "ocr_medical/config;ocr_medical/config" ^
    --add-data "ocr_medical/core/models;ocr_medical/core/models" ^
    --add-data "ocr_medical/ui;ocr_medical/ui" ^
    --add-data "ocr_medical/utils;ocr_medical/utils" ^
    %MAIN%

if %errorlevel% neq 0 (
    echo ❌ Build failed. Check errors above.
    pause
    exit /b 1
)

echo.
echo ===========================================================
echo ✅ Build complete! Executable: %EXE_PATH%
echo ===========================================================

REM === Tạo shortcut trên Desktop ===
echo 🧩 Creating Desktop shortcut...
set SHORTCUT_NAME=%NAME%.lnk
set SHORTCUT_PATH=%USERPROFILE%\Desktop\%SHORTCUT_NAME%

REM === Dùng PowerShell để tạo shortcut ===
powershell -Command ^
    "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT_PATH%');" ^
    "$s.TargetPath='%~dp0%EXE_PATH%';" ^
    "$s.WorkingDirectory='%~dp0%DIST%';" ^
    "$s.IconLocation='%~dp0%ICON%';" ^
    "$s.Description='OCR-Medical AI OCR Desktop App';" ^
    "$s.Save()"

if exist "%SHORTCUT_PATH%" (
    echo ✅ Shortcut created on Desktop: %SHORTCUT_NAME%
) else (
    echo ⚠️ Could not create shortcut (maybe permissions issue).
)

echo ===========================================================
echo 🧠 DONE! You can now run OCR-Medical from Desktop Shortcut.
echo ===========================================================
pause
