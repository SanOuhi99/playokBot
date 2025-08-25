
# PlayOK Checkerboard Extension Installation Instructions

## Prerequisites
1. Google Chrome browser
2. Your checkerboard.exe application
3. Python 3.7+ with required packages

## Installation Steps

### Step 1: Install Required Python Packages
```bash
pip install pyautogui psutil pygetwindow opencv-python pillow pytesseract pyperclip
```

### Step 2: Install the Chrome Extension
1. Open Chrome and go to chrome://extensions/
2. Enable "Developer mode" in the top right
3. Click "Load unpacked" and select this directory
4. Note the Extension ID (long string of letters/numbers)

### Step 3: Run the Setup Script
```bash
python setup_extension.py YOUR_EXTENSION_ID_HERE
```

### Step 4: Configure Checkerboard Path
Set the environment variable for your checkerboard.exe location:
```bash
set CHECKERBOARD_PATH=C:\path\to\your\checkerboard.exe
```

### Step 5: Test the Extension
1. Open PlayOK.com and start a checkers game
2. The extension should automatically detect opponent moves
3. Your checkerboard.exe will open and play the moves
4. The extension will detect the engine's response and play it on PlayOK

## Troubleshooting

### Move Detection Issues
The extension uses multiple methods to detect engine moves:
1. Log files (checkerboard_moves.txt, moves.log, game.pdn)
2. Screen capture with OCR
3. Clipboard monitoring
4. Temporary files

You can help by configuring your checkerboard app to:
- Save moves to a text file
- Copy moves to clipboard
- Display moves in a readable format

### Window Detection Issues
If the extension can't find your checkerboard window, try:
- Renaming the window title to include "checkerboard"
- Setting the window title manually in the script
- Adjusting the coordinate mapping for your specific app

### Coordinate Calibration
The click coordinates may need adjustment for your specific checkerboard app.
Edit the `square_positions` dictionary in kingrow_connector.py to match your board layout.

## Support
Check the log file `checkerboard_connector.log` for detailed error information.
