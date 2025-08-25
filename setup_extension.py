#!/usr/bin/env python3
"""
Automated Setup Script for PlayOK KingsRow Extension
This script automatically configures the Chrome extension and native messaging host
"""

import os
import sys
import json
import shutil
import subprocess
import platform
import winreg if sys.platform == "win32" else None
from pathlib import Path

class ExtensionSetup:
    def __init__(self):
        self.system = platform.system()
        self.extension_id = None
        self.current_dir = Path(__file__).parent.absolute()
        self.chrome_data_dir = self.get_chrome_data_dir()
        self.native_messaging_dir = self.get_native_messaging_dir()
        
    def get_chrome_data_dir(self):
        """Get Chrome user data directory"""
        if self.system == "Windows":
            return Path(os.environ.get("LOCALAPPDATA")) / "Google" / "Chrome" / "User Data"
        elif self.system == "Darwin":
            return Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
        else:  # Linux
            return Path.home() / ".config" / "google-chrome"
    
    def get_native_messaging_dir(self):
        """Get native messaging directory"""
        if self.system == "Windows":
            return Path(os.environ.get("LOCALAPPDATA")) / "Google" / "Chrome" / "User Data" / "NativeMessagingHosts"
        elif self.system == "Darwin":
            return Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "NativeMessagingHosts"
        else:  # Linux
            return Path.home() / ".config" / "google-chrome" / "NativeMessagingHosts"
    
    def find_extension_id(self):
        """Try to find the extension ID automatically"""
        print("🔍 Searching for Chrome extension...")
        
        extensions_dir = self.chrome_data_dir / "Default" / "Extensions"
        
        if not extensions_dir.exists():
            print("❌ Chrome extensions directory not found")
            return None
        
        try:
            for ext_dir in extensions_dir.iterdir():
                if ext_dir.is_dir() and len(ext_dir.name) == 32:
                    # Check if this is our extension
                    for version_dir in ext_dir.iterdir():
                        manifest_path = version_dir / "manifest.json"
                        if manifest_path.exists():
                            try:
                                with open(manifest_path, 'r', encoding='utf-8') as f:
                                    manifest = json.load(f)
                                
                                if manifest.get('name') == 'PlayOK KingsRow Bot':
                                    print(f"✅ Found extension ID: {ext_dir.name}")
                                    return ext_dir.name
                                    
                            except json.JSONDecodeError:
                                continue
                            except Exception as e:
                                print(f"⚠️  Error reading manifest: {e}")
                                continue
            
            print("❌ Extension not found. Please load the extension in Chrome first.")
            return None
            
        except Exception as e:
            print(f"❌ Error searching for extension: {e}")
            return None
    
    def get_extension_id_input(self):
        """Get extension ID from user input"""
        print("\n📋 Manual Extension ID Entry")
        print("1. Open Chrome and go to chrome://extensions/")
        print("2. Enable 'Developer mode' (top right toggle)")
        print("3. Find 'PlayOK KingsRow Bot' extension")
        print("4. Copy the Extension ID (long string below the extension name)")
        
        while True:
            extension_id = input("\nEnter Extension ID: ").strip()
            
            if len(extension_id) == 32 and extension_id.isalnum():
                return extension_id
            else:
                print("❌ Invalid Extension ID. Should be 32 alphanumeric characters.")
    
    def check_dependencies(self):
        """Check if all Python dependencies are installed"""
        print("🔍 Checking Python dependencies...")
        
        required_packages = [
            'pyautogui', 'psutil', 'pygetwindow', 'requests'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"  ✅ {package}")
            except ImportError:
                print(f"  ❌ {package} - MISSING")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
            print("Install with: pip install " + " ".join(missing_packages))
            
            install = input("\nInstall missing packages now? (y/n): ").strip().lower()
            if install == 'y':
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install"
                    ] + missing_packages)
                    print("✅ Packages installed successfully")
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to install packages: {e}")
                    return False
            else:
                return False
        
        print("✅ All dependencies are installed")
        return True
    
    def find_kingsrow(self):
        """Find KingsRow installation"""
        print("🔍 Searching for KingsRow...")
        
        possible_paths = []
        
        if self.system == "Windows":
            possible_paths = [
                "C:\\Program Files\\KingsRow\\KingsRow.exe",
                "C:\\Program Files (x86)\\KingsRow\\KingsRow.exe",
                "C:\\KingsRow\\KingsRow.exe"
            ]
        elif self.system == "Darwin":
            possible_paths = [
                "/Applications/KingsRow.app",
                str(Path.home() / "Applications" / "KingsRow.app")
            ]
        else:  # Linux
            possible_paths = [
                "/usr/local/bin/kingsrow",
                "/usr/bin/kingsrow",
                str(Path.home() / "bin" / "kingsrow")
            ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ Found KingsRow at: {path}")
                return path
        
        print("❌ KingsRow not found automatically")
        manual_path = input("Enter KingsRow path manually (or press Enter to skip): ").strip()
        
        if manual_path and os.path.exists(manual_path):
            print(f"✅ KingsRow path set: {manual_path}")
            return manual_path
        
        print("⚠️  KingsRow path not set - you'll need to configure this later")
        return None
    
    def create_native_messaging_host(self):
        """Create native messaging host configuration"""
        print("🔧 Setting up native messaging host...")
        
        # Ensure directory exists
        self.native_messaging_dir.mkdir(parents=True, exist_ok=True)
        
        # Create the host manifest
        if self.system == "Windows":
            # Create batch file to run Python script
            batch_file = self.current_dir / "run_kingsrow_connector.bat"
            with open(batch_file, 'w') as f:
                f.write(f'@echo off\n')
                f.write(f'cd /d "{self.current_dir}"\n')
                f.write(f'"{sys.executable}" kingsrow_connector.py\n')
            
            host_path = str(batch_file)
            
        else:
            # Create shell script for Unix-like systems
            shell_script = self.current_dir / "run_kingsrow_connector.sh"
            with open(shell_script, 'w') as f:
                f.write(f'#!/bin/bash\n')
                f.write(f'cd "{self.current_dir}"\n')
                f.write(f'"{sys.executable}" kingsrow_connector.py\n')
            
            shell_script.chmod(0o755)
            host_path = str(shell_script)
        
        # Create manifest
        manifest = {
            "name": "com.playok.kingsrow",
            "description": "KingsRow engine connector for PlayOK extension",
            "path": host_path,
            "type": "stdio",
            "allowed_origins": [
                f"chrome-extension://{self.extension_id}/"
            ]
        }
        
        manifest_path = self.native_messaging_dir / "com.playok.kingsrow.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Native messaging host created: {manifest_path}")
        return True
    
    def create_config_file(self, kingsrow_path):
        """Create configuration file"""
        print("⚙️ Creating configuration file...")
        
        config = {
            "kingsrow_path": kingsrow_path,
            "extension_id": self.extension_id,
            "auto_play_delay": 1000,
            "detection_interval": 500,
            "debug_mode": False,
            "log_level": "INFO",
            "setup_date": str(Path(__file__).stat().st_mtime)
        }
        
        config_path = self.current_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration saved: {config_path}")
        return True
    
    def create_desktop_shortcut(self):
        """Create desktop shortcut for easy access"""
        if self.system != "Windows":
            return  # Only create shortcuts on Windows for now
        
        try:
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "PlayOK KingsRow Setup.bat"
            
            with open(shortcut_path, 'w') as f:
                f.write(f'@echo off\n')
                f.write(f'title PlayOK KingsRow Extension\n')
                f.write(f'cd /d "{self.current_dir}"\n')
                f.write(f'echo Starting PlayOK KingsRow Extension Setup...\n')
                f.write(f'echo.\n')
                f.write(f'echo Extension Directory: {self.current_dir}\n')
                f.write(f'echo Extension ID: {self.extension_id}\n')
                f.write(f'echo.\n')
                f.write(f'echo Press any key to run setup again...\n')
                f.write(f'pause > nul\n')
                f.write(f'python setup_extension.py\n')
                f.write(f'pause\n')
            
            print(f"✅ Desktop shortcut created: {shortcut_path}")
            
        except Exception as e:
            print(f"⚠️  Could not create desktop shortcut: {e}")
    
    def test_installation(self):
        """Test if the installation is working"""
        print("🧪 Testing installation...")
        
        try:
            # Test Python connector
            result = subprocess.run([
                sys.executable, "-c", 
                "import kingsrow_connector; print('Connector import successful')"
            ], cwd=self.current_dir, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("✅ Python connector test passed")
            else:
                print(f"❌ Python connector test failed: {result.stderr}")
                return False
            
            # Check if native messaging manifest exists
            manifest_path = self.native_messaging_dir / "com.playok.kingsrow.json"
            if manifest_path.exists():
                print("✅ Native messaging manifest exists")
            else:
                print("❌ Native messaging manifest not found")
                return False
            
            print("✅ All tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
    
    def print_instructions(self):
        """Print final setup instructions"""
        print("\n" + "="*60)
        print("🎉 SETUP COMPLETE!")
        print("="*60)
        
        print(f"""
📁 Extension Directory: {self.current_dir}
🆔 Extension ID: {self.extension_id}
📄 Config File: {self.current_dir / 'config.json'}
🔗 Native Host: {self.native_messaging_dir / 'com.playok.kingsrow.json'}

🚀 NEXT STEPS:
1. Restart Google Chrome completely
2. Go to PlayOK.com and start a checkers game
3. The extension icon should show "active" status
4. When opponent makes a move, KingsRow will calculate response

🔧 TESTING:
- Click the extension icon to see status
- Check logs in: kingsrow_connector.log
- Enable debug mode in extension popup if needed

⚠️  TROUBLESHOOTING:
- If moves aren't detected: Check if PlayOK's interface has changed
- If KingsRow doesn't respond: Verify KingsRow path in config.json
- If extension shows errors: Check Chrome extension console

📚 For detailed help, see: INSTALLATION_GUIDE.md
        """)
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🚀 PlayOK KingsRow Extension Setup")
        print("="*50)
        
        # Check dependencies
        if not self.check_dependencies():
            print("❌ Setup failed - missing dependencies")
            return False
        
        # Find extension ID
        self.extension_id = self.find_extension_id()
        if not self.extension_id:
            self.extension_id = self.get_extension_id_input()
        
        if not self.extension_id:
            print("❌ Setup failed - no extension ID")
            return False
        
        # Find KingsRow
        kingsrow_path = self.find_kingsrow()
        
        # Create native messaging host
        if not self.create_native_messaging_host():
            print("❌ Setup failed - could not create native messaging host")
            return False
        
        # Create config file
        if not self.create_config_file(kingsrow_path):
            print("❌ Setup failed - could not create config file")
            return False
        
        # Create desktop shortcut
        self.create_desktop_shortcut()
        
        # Test installation
        if not self.test_installation():
            print("⚠️  Setup completed but tests failed")
        
        # Print final instructions
        self.print_instructions()
        
        return True

def main():
    """Main entry point"""
    try:
        setup = ExtensionSetup()
        success = setup.run_setup()
        
        if success:
            input("\nPress Enter to close...")
        else:
            input("\nSetup failed. Press Enter to close...")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        input("Press Enter to close...")
        sys.exit(1)

if __name__ == "__main__":
    main()
