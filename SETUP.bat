@echo off
title PlayOK KingsRow Extension - Easy Setup
color 0A

echo ========================================
echo  PlayOK KingsRow Extension Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo [INFO] Python found - checking version...
python --version

echo.
echo [INFO] Installing required Python packages...
python -m pip install --user pyautogui psutil pygetwindow opencv-python pillow pytesseract pyperclip requests

if errorlevel 1 (
    echo [WARNING] Some packages may have failed to install
    echo You can continue, but the extension might not work properly
    echo.
)

echo.
echo [INFO] Running automated setup...
echo.
python setup_extension.py

if errorlevel 1 (
    echo.
    echo [ERROR] Setup failed!
    echo Check the error messages above and try again
    echo.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Setup completed successfully!
echo.
echo NEXT STEPS:
echo 1. Restart Google Chrome completely
echo 2. Load the extension in Chrome (chrome://extensions/)
echo 3. Go to PlayOK.com and start a checkers game
echo 4. The extension will automatically play moves
echo.
echo For troubleshooting, check:
echo - kingsrow_connector.log (in this folder)
echo - Chrome extension console (F12 in Chrome)
echo.

pause
