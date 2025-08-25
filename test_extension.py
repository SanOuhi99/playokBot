#!/usr/bin/env python3
"""
Test script for PlayOK Checkerboard Extension
Verifies all components are working correctly
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

def test_python_dependencies():
    """Test if all required Python packages are installed"""
    print("Testing Python dependencies...")
    
    required_packages = [
        'pyautogui', 'psutil', 'pygetwindow', 'cv2', 'numpy', 
        'PIL', 'pytesseract', 'pyperclip'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            else:
                __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install pyautogui psutil pygetwindow opencv-python pillow pytesseract pyperclip")
        return False
    
    print("All Python dependencies are installed!")
    return True

def test_checkerboard_detection():
    """Test if checkerboard application can be detected"""
    print("\nTesting checkerboard application detection...")
    
    try:
        import pygetwindow as gw
        
        # Common checkerboard window titles
        titles_to_check = [
            "checkerboard", "Checkerboard", "CheckerBoard", "Draughts", 
            "Damka", "Checkers", "checkers", "Dame", "Dama"
        ]
        
        found_windows = []
        
        for title in titles_to_check:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                found_windows.extend([(w.title, title) for w in windows])
        
        if found_windows:
            print("  ✓ Checkerboard windows found:")
            for window_title, search_term in found_windows:
                print(f"    - {window_title} (matched: {search_term})")
            return True
        else:
            print("  ✗ No checkerboard windows found")
            print("    Make sure your checkerboard application is running")
            print("    Window title should contain one of:", titles_to_check)
            return False
            
    except Exception as e:
        print(f"  ✗ Error during detection: {e}")
        return False

def test_native_messaging_setup():
    """Test if native messaging host is properly configured"""
    print("\nTesting native messaging setup...")
    
    # Check if host manifest exists
    if sys.platform == "win32":
        native_dir = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\NativeMessagingHosts")
    elif sys.platform == "darwin":
        native_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome/NativeMessagingHosts")
    else:
        native_dir = os.path.expanduser("~/.config/google-chrome/NativeMessagingHosts")
    
    manifest_path = os.path.join(native_dir, "com.playok.kingrow.json")
    
    if os.path.exists(manifest_path):
        print(f"  ✓ Native messaging manifest found: {manifest_path}")
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Check manifest structure
            required_fields = ['name', 'description', 'path', 'type', 'allowed_origins']
            missing_fields = [field for field in required_fields if field not in manifest]
            
            if missing_fields:
                print(f"  ✗ Manifest missing fields: {missing_fields}")
                return False
            
            # Check if the executable/script path exists
            path = manifest['path']
            if os.path.exists(path.split('"')[1] if '"' in path else path.split()[0]):
                print(f"  ✓ Connector executable/script found: {path}")
            else:
                print(f"  ✗ Connector path not found: {path}")
                return False
            
            print(f"  ✓ Native messaging configuration is valid")
            return True
            
        except Exception as e:
            print(f"  ✗ Error reading manifest: {e}")
            return False
    else:
        print(f"  ✗ Native messaging manifest not found: {manifest_path}")
        print("    Run setup_extension.py with your Chrome extension ID")
        return False

def test_calibration_data():
    """Test if coordinate calibration data exists and is valid"""
    print("\nTesting coordinate calibration...")
    
    calibration_file = "checkerboard_calibration.json"
    
    if os.path.exists(calibration_file):
        try:
            with open(calibration_file, 'r') as f:
                data = json.load(f)
            
            square_positions = data.get('square_positions', {})
            
            if len(square_positions) >= 32:
                print(f"  ✓ Calibration data found with {len(square_positions)} squares")
                print(f"  ✓ Window: {data.get('window_title', 'Unknown')}")
                print(f"  ✓ Date: {data.get('calibration_date', 'Unknown')}")
                return True
            else:
                print(f"  ✗ Incomplete calibration data ({len(square_positions)}/32 squares)")
                return False
                
        except Exception as e:
            print(f"  ✗ Error reading calibration file: {e}")
            return False
    else:
        print(f"  ✗ Calibration file not found: {calibration_file}")
        print("    Run calibrate_coordinates.py to create calibration data")
        return False

def test_connector_script():
    """Test if the connector script can run without errors"""
    print("\nTesting connector script...")
    
    try:
        # Test basic import and initialization
        result = subprocess.run([
            sys.executable, "-c", 
            "import kingrow_connector; print('Connector script imports successfully')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("  ✓ Connector script imports successfully")
            return True
        else:
            print(f"  ✗ Connector script error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ✗ Connector script test timed out")
        return False
    except Exception as e:
        print(f"  ✗ Error testing connector script: {e}")
        return False

def test_chrome_extension_files():
    """Test if Chrome extension files are present and valid"""
    print("\nTesting Chrome extension files...")
    
    required_files = [
        'manifest.json', 'background.js', 'content.js', 'popup.html'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
            
            # Validate manifest.json
            if file == 'manifest.json':
                try:
                    with open(file, 'r') as f:
                        manifest = json.load(f)
                    
                    required_permissions = ['scripting', 'tabs', 'nativeMessaging']
                    missing_perms = [p for p in required_permissions if p not in manifest.get('permissions', [])]
                    
                    if missing_perms:
                        print(f"    ✗ Missing permissions: {missing_perms}")
                        return False
                    else:
                        print(f"    ✓ All required permissions present")
                        
                except Exception as e:
                    print(f"    ✗ Error reading manifest: {e}")
                    return False
        else:
            print(f"  ✗ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\nMissing extension files: {', '.join(missing_files)}")
        return False
    
    print("All Chrome extension files are present!")
    return True

def run_comprehensive_test():
    """Run all tests and provide a summary"""
    print("=" * 60)
    print("PlayOK Checkerboard Extension - Comprehensive Test")
    print("=" * 60)
    
    tests = [
        ("Python Dependencies", test_python_dependencies),
        ("Chrome Extension Files", test_chrome_extension_files),
        ("Native Messaging Setup", test_native_messaging_setup),
        ("Coordinate Calibration", test_calibration_data),
        ("Checkerboard Detection", test_checkerboard_detection),
        ("Connector Script", test_connector_script)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"  ✗ Unexpected error in {test_name}: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:<25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your extension is ready to use.")
        print("\nNext steps:")
        print("1. Load the extension in Chrome (chrome://extensions/)")
        print("2. Start your checkerboard application")
        print("3. Go to PlayOK.com and start a checkers game")
        print("4. The extension will automatically handle opponent moves")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Address the issues above before using the extension.")
        
        if not results.get("Native Messaging Setup", True):
            print("\nTo fix native messaging:")
            print("1. Run: python setup_extension.py YOUR_EXTENSION_ID")
            print("2. Get extension ID from chrome://extensions/")
        
        if not results.get("Coordinate Calibration", True):
            print("\nTo fix calibration:")
            print("1. Start your checkerboard application")
            print("2. Run: python calibrate_coordinates.py")
        
        if not results.get("Python Dependencies", True):
            print("\nTo fix dependencies:")
            print("pip install pyautogui psutil pygetwindow opencv-python pillow pytesseract pyperclip")

if __name__ == "__main__":
    try:
        run_comprehensive_test()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Unexpected error during testing: {e}")