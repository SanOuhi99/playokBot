#!/usr/bin/env python3
"""
Setup script for PlayOK Checkerboard Chrome Extension
This script configures the native messaging host and creates necessary files
"""

import os
import json
import sys
import shutil
import subprocess
from pathlib import Path

def get_chrome_native_messaging_dir():
    """Get the Chrome native messaging directory for the current OS"""
    if sys.platform == "win32":
        import winreg
        try:
            # Try to get from registry first
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"SOFTWARE\Google\Chrome\NativeMessagingHosts")
            return winreg.QueryValueEx(key, "")[0]
        except:
            # Fallback to default location
            return os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\NativeMessagingHosts")
    elif sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/Google/Chrome/NativeMessagingHosts")
    else:  # Linux
        return os.path.expanduser("~/.config/google-chrome/NativeMessagingHosts")

def create_executable_from_python():
    """Create an executable from the Python connector using PyInstaller"""
    try:
        # Check if PyInstaller is available
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
        
        print("Creating executable from Python script...")
        
        # Create the executable
        cmd = [
            "pyinstaller",
            "--onefile",
            "--name", "checkerboard_connector",
            "--hidden-import", "pyautogui",
            "--hidden-import", "psutil", 
            "--hidden-import", "pygetwindow",
            "--hidden-import", "cv2",
            "--hidden-import", "numpy",
            "--hidden-import", "PIL",
            "--hidden-import", "pytesseract",
            "--hidden-import", "pyperclip",
            "kingrow_connector.py"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            exe_path = os.path.join("dist", "checkerboard_connector.exe")
            if os.path.exists(exe_path):
                print(f"Executable created successfully: {exe_path}")
                return os.path.abspath(exe_path)
        
        print("PyInstaller failed, using Python script directly")
        return None
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("PyInstaller not found, using Python script directly")
        return None

def setup_native_messaging_host(extension_id):
    """Set up the native messaging host"""
    
    # Get the native messaging directory
    native_dir = get_chrome_native_messaging_dir()
    os.makedirs(native_dir, exist_ok=True)
    
    # Try to create executable, fallback to Python script
    exe_path = create_executable_from_python()
    
    if exe_path:
        host_path = exe_path
    else:
        # Use Python script directly
        python_exe = sys.executable
        script_path = os.path.abspath("kingrow_connector.py")
        host_path = f'"{python_exe}" "{script_path}"'
    
    # Create the host manifest
    manifest = {
        "name": "com.playok.kingrow",
        "description": "Checkerboard engine host for PlayOK auto-player",
        "path": host_path,
        "type": "stdio",
        "allowed_origins": [
            f"chrome-extension://{extension_id}/"
        ]
    }
    
    # Write the manifest file
    manifest_path = os.path.join(native_dir, "com.playok.kingrow.json")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Native messaging host configured at: {manifest_path}")
    return manifest_path

def create_install_instructions():
    """Create installation instructions"""
    instructions = """
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
set CHECKERBOARD_PATH=C:\\path\\to\\your\\checkerboard.exe
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
"""
    
    with open("INSTALLATION_GUIDE.md", 'w') as f:
        f.write(instructions)
    
    print("Installation guide created: INSTALLATION_GUIDE.md")

def main():
    if len(sys.argv) != 2:
        print("Usage: python setup_extension.py <EXTENSION_ID>")
        print("Get the Extension ID from chrome://extensions/ after loading the extension")
        sys.exit(1)
    
    extension_id = sys.argv[1]
    
    print("Setting up PlayOK Checkerboard Extension...")
    
    # Set up native messaging
    manifest_path = setup_native_messaging_host(extension_id)
    
    # Create installation guide
    create_install_instructions()
    
    print("\nSetup complete!")
    print(f"Native messaging host: {manifest_path}")
    print("Installation guide: INSTALLATION_GUIDE.md")
    print("\nNext steps:")
    print("1. Set CHECKERBOARD_PATH environment variable")
    print("2. Test the extension on PlayOK.com")
    print("3. Check checkerboard_connector.log for any issues")

if __name__ == "__main__":
    main()