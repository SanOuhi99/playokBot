#!/usr/bin/env python3
"""
Quick setup script that automatically detects the Chrome extension ID
"""

import os
import json
import sys
import subprocess
import time

def find_chrome_extension_id():
    """Try to automatically find the extension ID from Chrome's extension directory"""
    try:
        if sys.platform == "win32":
            # Windows Chrome extension paths
            chrome_paths = [
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Extensions"),
                os.path.expandvars(r"%APPDATA%\Google\Chrome\User Data\Default\Extensions")
            ]
        elif sys.platform == "darwin":
            # macOS Chrome extension paths
            chrome_paths = [
                os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Extensions")
            ]
        else:
            # Linux Chrome extension paths
            chrome_paths = [
                os.path.expanduser("~/.config/google-chrome/Default/Extensions")
            ]
        
        for chrome_path in chrome_paths:
            if os.path.exists(chrome_path):
                # Look for extension directories
                for ext_id in os.listdir(chrome_path):
                    if len(ext_id) == 32 and ext_id.isalnum():  # Chrome extension ID format
                        ext_dir = os.path.join(chrome_path, ext_id)
                        if os.path.isdir(ext_dir):
                            # Check if it contains a manifest with our extension name
                            for version_dir in os.listdir(ext_dir):
                                manifest_path = os.path.join(ext_dir, version_dir, "manifest.json")
                                if os.path.exists(manifest_path):
                                    try:
                                        with open(manifest_path, 'r') as f:
                                            manifest = json.load(f)
                                        if manifest.get('name') == 'PlayOK AutoMove Bot':
                                            return ext_id
                                    except:
                                        continue
        return None
    except Exception as e:
        print(f"Error searching for extension ID: {e}")
        return None

def setup_native_messaging(extension_id):
    """Set up native messaging host"""
    print(f"Setting up native messaging for extension ID: {extension_id}")
    
    # Get the native messaging directory
    if sys.platform == "win32":
        native_dir = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\NativeMessagingHosts")
    elif sys.platform == "darwin":
        native_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome/NativeMessagingHosts")
    else:
        native_dir = os.path.expanduser("~/.config/google-chrome/NativeMessagingHosts")
    
    os.makedirs(native_dir, exist_ok=True)
    
    # Use Python script directly (no need for compilation)
    python_exe = sys.executable
    script_path = os.path.abspath("kingrow_connector.py")
    
    # Create the host manifest
    manifest = {
        "name": "com.playok.kingrow",
        "description": "Checkerboard engine host for PlayOK auto-player",
        "path": python_exe,
        "type": "stdio",
        "allowed_origins": [
            f"chrome-extension://{extension_id}/"
        ]
    }
    
    # For Windows, we need to handle the script path differently
    if sys.platform == "win32":
        # Create a batch file to run the Python script
        batch_path = os.path.abspath("run_connector.bat")
        with open(batch_path, 'w') as f:
            f.write(f'@echo off\n"{python_exe}" "{script_path}"\n')
        manifest["path"] = batch_path
    else:
        # For Unix-like systems, create a shell script
        shell_script = os.path.abspath("run_connector.sh")
        with open(shell_script, 'w') as f:
            f.write(f'#!/bin/bash\n"{python_exe}" "{script_path}"\n')
        os.chmod(shell_script, 0o755)
        manifest["path"] = shell_script
    
    # Write the manifest file
    manifest_path = os.path.join(native_dir, "com.playok.kingrow.json")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Native messaging host configured at: {manifest_path}")
    return True

def main():
    print("PlayOK Checkerboard Extension - Quick Setup")
    print("=" * 50)
    
    # Try to auto-detect extension ID
    print("Searching for Chrome extension...")
    extension_id = find_chrome_extension_id()
    
    if extension_id:
        print(f"Found extension ID: {extension_id}")
    else:
        print("Could not auto-detect extension ID.")
        print("Please manually enter your Chrome extension ID.")
        print("You can find it at chrome://extensions/ (enable Developer mode)")
        extension_id = input("Extension ID: ").strip()
    
    if not extension_id or len(extension_id) != 32:
        print("Invalid extension ID. Please ensure you've loaded the extension in Chrome.")
        return False
    
    # Set up native messaging
    if setup_native_messaging(extension_id):
        print("\n✓ Setup complete!")
        print("\nNext steps:")
        print("1. Restart Chrome to register the native messaging host")
        print("2. Start your checkerboard.exe application")
        print("3. Run 'python calibrate_coordinates.py' to calibrate board coordinates")
        print("4. Test the extension on PlayOK.com")
        return True
    else:
        print("Setup failed.")
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup cancelled by user")
    except Exception as e:
        print(f"Setup error: {e}")