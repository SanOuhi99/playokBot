@echo off
REM Windows batch script to install native messaging host

echo Installing PlayOK Checkerboard Native Messaging Host...

REM Create the native messaging directory
set "NATIVE_DIR=%LOCALAPPDATA%\Google\Chrome\User Data\NativeMessagingHosts"
if not exist "%NATIVE_DIR%" mkdir "%NATIVE_DIR%"

REM Get the current directory
set "CURRENT_DIR=%~dp0"

REM Create the connector batch file
echo @echo off > "%CURRENT_DIR%connector.bat"
echo python "%CURRENT_DIR%kingrow_connector.py" >> "%CURRENT_DIR%connector.bat"

REM Create the manifest file with a wildcard extension ID
(
echo {
echo   "name": "com.playok.kingrow",
echo   "description": "Checkerboard engine connector",
echo   "path": "%CURRENT_DIR%connector.bat",
echo   "type": "stdio",
echo   "allowed_origins": [
echo     "chrome-extension://*/"
echo   ]
echo }
) > "%NATIVE_DIR%\com.playok.kingrow.json"

echo Native messaging host installed successfully!
echo Manifest location: %NATIVE_DIR%\com.playok.kingrow.json
echo Connector script: %CURRENT_DIR%connector.bat
echo.
echo Please restart Chrome for changes to take effect.
pause