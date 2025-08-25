# PlayOK Checkerboard AutoPlayer

A Chrome extension that automatically plays checkers on PlayOK.com by interfacing with your local checkerboard.exe application for move calculation.

## How It Works

1. **Monitors PlayOK**: Extension watches for opponent moves on PlayOK.com
2. **Executes in Checkerboard**: Plays opponent's move in your local checkerboard.exe
3. **Waits for Engine**: Allows your checkerboard engine to calculate the best response
4. **Returns Move**: Detects the engine's move and plays it back on PlayOK.com
5. **Repeats**: Continues this cycle until the game ends

## Features

- **Automatic Integration**: Seamlessly connects PlayOK with your checkerboard application
- **Multiple Detection Methods**: Uses file monitoring, screen capture, OCR, and clipboard detection
- **Coordinate Calibration**: Precise click positioning for your specific checkerboard app
- **Real-time Processing**: Maintains game flow with proper timing
- **Comprehensive Logging**: Detailed logs for troubleshooting

## Prerequisites

1. **Google Chrome Browser**
2. **Your checkerboard.exe application** (any Windows checkers program)
3. **Python 3.7+** with required packages

## Quick Setup

### Step 1: Install Python Dependencies
```bash
pip install pyautogui psutil pygetwindow opencv-python pillow pytesseract pyperclip
```

### Step 2: Load Chrome Extension
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right toggle)
3. Click "Load unpacked" and select this folder
4. Copy the Extension ID (long string under the extension name)

### Step 3: Run Automated Setup
```bash
python setup_extension.py YOUR_EXTENSION_ID_HERE
```

### Step 4: Calibrate Coordinates
```bash
python calibrate_coordinates.py
```
Follow the prompts to calibrate click positions for your checkerboard app.

### Step 5: Configure Checkerboard Path
Set environment variable for your checkerboard.exe location:
```bash
set CHECKERBOARD_PATH=C:\path\to\your\checkerboard.exe
```

## Usage

1. **Start Your Checkerboard App**: Launch your checkerboard.exe
2. **Open PlayOK**: Go to PlayOK.com and start a checkers game
3. **Extension Activates**: The extension popup shows "Active & Monitoring"
4. **Automatic Play**: When opponent moves, the process begins automatically

## Move Detection Methods

The extension uses multiple methods to detect your engine's moves:

### Method 1: Log Files
- `checkerboard_moves.txt`
- `moves.log`
- `game.pdn`
- `history.txt`

### Method 2: Screen Capture + OCR
- Captures text from checkerboard window
- Uses OCR to read move notation
- Searches title bars, status areas, move history panels

### Method 3: Clipboard Monitoring
- Detects if your app copies moves to clipboard
- Automatically captures new clipboard content

### Method 4: Temporary Files
- Monitors for temp files created by your app
- Checks common locations for move output

## Coordinate Calibration

The calibration tool helps map checkerboard squares to screen coordinates:

1. **Interactive Mode**: Click on each board square (1-32)
2. **Manual Mode**: Enter coordinates for key squares
3. **Auto-saves**: Creates `checkerboard_calibration.json`
4. **Test Mode**: Verifies accuracy by moving cursor to squares

## Troubleshooting

### Extension Not Detecting Moves
- Check `checkerboard_connector.log` for errors
- Verify your checkerboard app is running
- Ensure window title contains "checkerboard" or similar
- Run calibration tool to verify coordinates

### Move Detection Issues
- Configure your checkerboard app to save moves to a text file
- Enable move copying to clipboard if available
- Check if your app has a move history display
- Verify OCR is working (install Tesseract if needed)

### Coordinate Problems
- Re-run the calibration tool
- Adjust square positions manually in the calibration file
- Check that your checkerboard window is not resized
- Ensure window is fully visible on screen

### Native Messaging Errors
- Verify the setup script completed successfully
- Check Chrome extension permissions
- Confirm Python executable path is correct
- Review native messaging host registration

## Configuration Files

- `checkerboard_calibration.json`: Square coordinate mappings
- `checkerboard_connector.log`: Detailed operation logs
- `com.playok.kingrow.json`: Native messaging host configuration

## Advanced Configuration

### Custom Window Detection
Edit `kingrow_connector.py` to add your specific window title:
```python
alt_titles = ["YourAppName", "Custom Title", "Checkerboard"]
```

### Coordinate Adjustment
Modify the coordinate system in `checkerboard_calibration.json`:
```json
{
  "square_positions": {
    "1": [50, 50],
    "2": [150, 50]
  }
}
```

### Timing Adjustments
Change wait times in the connector:
```python
time.sleep(2)  # Adjust engine wait time
pyautogui.PAUSE = 0.1  # Adjust click timing
```

## Support

Check the log file `checkerboard_connector.log` for detailed information about:
- Window detection status
- Move execution attempts
- Coordinate calculations
- Error diagnostics

The extension works with any Windows checkerboard application that accepts mouse clicks and displays moves in a readable format.
