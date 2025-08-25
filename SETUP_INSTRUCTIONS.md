# Windows Setup Instructions for PlayOK Checkerboard Extension

## Step 1: Download Extension Files
Download all files from this Replit to your Windows computer:
- manifest.json
- background.js  
- content.js
- popup.html
- kingrow_connector.py
- setup_extension.py
- calibrate_coordinates.py

## Step 2: Install Python Dependencies
Open Command Prompt as Administrator and run:
```cmd
pip install pyautogui psutil pygetwindow opencv-python pillow pytesseract pyperclip
```

## Step 3: Load Extension in Chrome
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked" 
4. Select the folder containing your extension files
5. Copy the Extension ID (32-character string under extension name)

## Step 4: Configure Native Messaging
1. Open Command Prompt as Administrator
2. Navigate to your extension folder
3. Run: `python setup_extension.py YOUR_EXTENSION_ID_HERE`
4. Restart Chrome completely

## Step 5: Calibrate Your Checkerboard Application
1. Start your checkerboard.exe application
2. Run: `python calibrate_coordinates.py`
3. Follow prompts to map board squares to screen coordinates

## Step 6: Set Checkerboard Path
Set environment variable for your checkerboard location:
```cmd
set CHECKERBOARD_PATH=C:\path\to\your\checkerboard.exe
```

## Step 7: Test Extension
1. Start your checkerboard.exe
2. Go to PlayOK.com and start a checkers game
3. When opponent moves, the extension will:
   - Execute the move in your checkerboard app
   - Wait for your engine's response
   - Play the engine's move back on PlayOK

## Troubleshooting
- Check `checkerboard_connector.log` for detailed error information
- Ensure checkerboard window title contains "checkerboard" or similar
- Verify coordinates are properly calibrated
- Make sure Chrome has been restarted after setup

The extension uses multiple methods to detect your engine's moves:
- Log file monitoring
- Screen capture with OCR
- Clipboard detection
- Temporary file monitoring