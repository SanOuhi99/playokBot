#!/usr/bin/env python3
import sys
import json
import subprocess
import os
import logging
import time
import pyautogui
import psutil
import pygetwindow as gw
from threading import Thread
import cv2
import numpy as np
from PIL import Image
import re

# Set up logging for debugging
logging.basicConfig(
    filename='checkerboard_connector.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configure pyautogui
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

def read_message():
    """Read a message from Chrome extension via stdin"""
    try:
        raw_length = sys.stdin.buffer.read(4)
        if not raw_length:
            return None
        message_length = int.from_bytes(raw_length, byteorder='little')
        message_bytes = sys.stdin.buffer.read(message_length)
        return json.loads(message_bytes.decode('utf-8'))
    except Exception as e:
        logging.error(f"Error reading message: {e}")
        return None

def send_message(message):
    """Send a message to Chrome extension via stdout"""
    try:
        encoded_content = json.dumps(message).encode('utf-8')
        encoded_length = len(encoded_content).to_bytes(4, byteorder='little')
        sys.stdout.buffer.write(encoded_length)
        sys.stdout.buffer.write(encoded_content)
        sys.stdout.buffer.flush()
        logging.debug(f"Sent message: {message}")
    except Exception as e:
        logging.error(f"Error sending message: {e}")

def find_checkerboard_exe():
    """Find checkerboard.exe process or launch it"""
    try:
        # Check if checkerboard.exe is already running
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            if proc.info['name'] and 'checkerboard.exe' in proc.info['name'].lower():
                logging.info(f"Found running checkerboard.exe: PID {proc.info['pid']}")
                return True
        
        # Try to launch checkerboard.exe
        checkerboard_path = os.getenv("CHECKERBOARD_PATH", "checkerboard.exe")
        
        # Try common paths
        common_paths = [
            checkerboard_path,
            "C:\\Program Files\\Checkerboard\\checkerboard.exe",
            "C:\\Program Files (x86)\\Checkerboard\\checkerboard.exe",
            "./checkerboard.exe",
            "checkerboard.exe"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                logging.info(f"Launching checkerboard.exe from: {path}")
                subprocess.Popen([path])
                time.sleep(3)  # Wait for the application to start
                return True
        
        logging.error("checkerboard.exe not found in common locations")
        return False
        
    except Exception as e:
        logging.error(f"Error finding/launching checkerboard.exe: {e}")
        return False

def load_calibration_data():
    """Load coordinate calibration data"""
    try:
        if os.path.exists("checkerboard_calibration.json"):
            with open("checkerboard_calibration.json", 'r') as f:
                data = json.load(f)
                return data.get("square_positions", {})
    except Exception as e:
        logging.debug(f"Could not load calibration data: {e}")
    
    # Default coordinates if no calibration file exists
    return {
        1: (50, 50), 2: (150, 50), 3: (250, 50), 4: (350, 50),
        5: (100, 100), 6: (200, 100), 7: (300, 100), 8: (400, 100),
        9: (50, 150), 10: (150, 150), 11: (250, 150), 12: (350, 150),
        13: (100, 200), 14: (200, 200), 15: (300, 200), 16: (400, 200),
        17: (50, 250), 18: (150, 250), 19: (250, 250), 20: (350, 250),
        21: (100, 300), 22: (200, 300), 23: (300, 300), 24: (400, 300),
        25: (50, 350), 26: (150, 350), 27: (250, 350), 28: (350, 350),
        29: (100, 400), 30: (200, 400), 31: (300, 400), 32: (400, 400)
    }

def convert_move_to_coordinates(move):
    """Convert move notation (like '12-16') to board coordinates"""
    try:
        # Load calibrated coordinates
        square_positions = load_calibration_data()
        
        # Convert string keys to integers for lookup
        if isinstance(list(square_positions.keys())[0], str):
            square_positions = {int(k): v for k, v in square_positions.items()}
        
        if 'x' in move:
            parts = move.split('x')
        else:
            parts = move.split('-')
        
        from_square = int(parts[0])
        to_square = int(parts[-1])
        
        from_coords = square_positions.get(from_square)
        to_coords = square_positions.get(to_square)
        
        return from_coords, to_coords, parts[1:] if len(parts) > 2 else []
        
    except Exception as e:
        logging.error(f"Error converting move to coordinates: {e}")
        return None, None, []

def execute_move_in_checkerboard(move):
    """Execute a move in the checkerboard application"""
    try:
        logging.info(f"Executing move in checkerboard: {move}")
        
        # Focus on checkerboard window using pygetwindow
        checkerboard_windows = gw.getWindowsWithTitle("checkerboard")
        if not checkerboard_windows:
            # Try alternative window titles
            alt_titles = ["Checkerboard", "CheckerBoard", "Draughts", "Damka"]
            for title in alt_titles:
                checkerboard_windows = gw.getWindowsWithTitle(title)
                if checkerboard_windows:
                    break
        
        window = None
        window_x, window_y = 0, 0
        
        if checkerboard_windows:
            window = checkerboard_windows[0]
            try:
                window.activate()
                time.sleep(0.5)
                window_x, window_y = window.left, window.top
            except Exception as e:
                logging.warning(f"Could not activate window: {e}")
        
        from_coords, to_coords, jumps = convert_move_to_coordinates(move)
        
        if from_coords and to_coords:
            # Apply window offset if we found the window
            final_from_coords = (window_x + from_coords[0], window_y + from_coords[1])
            final_to_coords = (window_x + to_coords[0], window_y + to_coords[1])
            
            # Click on the from square
            pyautogui.click(final_from_coords[0], final_from_coords[1])
            time.sleep(0.3)
            
            # Handle jumps if present
            if jumps:
                for jump_square in jumps:
                    jump_coords = convert_move_to_coordinates(f"1-{jump_square}")[1]
                    if jump_coords:
                        final_jump_coords = (window_x + jump_coords[0], window_y + jump_coords[1])
                        pyautogui.click(final_jump_coords[0], final_jump_coords[1])
                        time.sleep(0.3)
            else:
                # Click on the to square
                pyautogui.click(final_to_coords[0], final_to_coords[1])
                time.sleep(0.3)
                
            logging.info("Move executed successfully in checkerboard")
            return True
        else:
            logging.error("Could not convert move to coordinates")
            return False
            
    except Exception as e:
        logging.error(f"Error executing move in checkerboard: {e}")
        return False

def wait_for_engine_response():
    """Wait for the checkerboard engine to make its move"""
    try:
        logging.info("Waiting for engine response...")
        time.sleep(2)  # Initial wait for engine to think
        
        # Monitor for changes in the checkerboard window
        # This is a simplified approach - you might need to adjust based on your specific checkerboard app
        max_wait_time = 30  # Maximum wait time in seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            time.sleep(0.5)
            # Here you could implement more sophisticated detection
            # For now, we'll wait a reasonable amount of time
            if time.time() - start_time > 3:  # Minimum 3 seconds
                break
        
        logging.info("Engine response wait completed")
        return True
        
    except Exception as e:
        logging.error(f"Error waiting for engine response: {e}")
        return False

def capture_screen_region(x, y, width, height):
    """Capture a specific region of the screen"""
    try:
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    except Exception as e:
        logging.error(f"Error capturing screen region: {e}")
        return None

def detect_move_from_screen():
    """Use OCR and screen capture to detect the engine's move"""
    try:
        # Find checkerboard window
        checkerboard_windows = gw.getWindowsWithTitle("checkerboard")
        if not checkerboard_windows:
            alt_titles = ["Checkerboard", "CheckerBoard", "Draughts", "Damka"]
            for title in alt_titles:
                checkerboard_windows = gw.getWindowsWithTitle(title)
                if checkerboard_windows:
                    break
        
        if not checkerboard_windows:
            logging.error("Could not find checkerboard window for move detection")
            return None
        
        window = checkerboard_windows[0]
        
        # Capture areas where moves might be displayed
        # Common areas: title bar, status bar, move history panel
        regions_to_check = [
            # Top area (title/status)
            (window.left, window.top, window.width, 100),
            # Bottom area (status bar)
            (window.left, window.top + window.height - 100, window.width, 100),
            # Right panel (move history - common in checkers apps)
            (window.left + window.width - 200, window.top, 200, window.height),
            # Left panel
            (window.left, window.top, 200, window.height)
        ]
        
        for i, (x, y, w, h) in enumerate(regions_to_check):
            image = capture_screen_region(x, y, w, h)
            if image is None:
                continue
                
            # Use OCR to extract text
            try:
                import pytesseract
                text = pytesseract.image_to_string(image)
                logging.debug(f"OCR text from region {i}: {text}")
                
                # Look for move patterns in the text
                move_patterns = [
                    r'\b\d{1,2}[-x]\d{1,2}(?:x\d{1,2})*\b',  # Standard notation
                    r'\b[A-H][1-8][-x][A-H][1-8]\b',          # Algebraic notation
                    r'\b\d{1,2}\s*[-x]\s*\d{1,2}\b'          # Spaced notation
                ]
                
                for pattern in move_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        # Return the last/most recent move found
                        latest_move = matches[-1].replace(' ', '')
                        logging.info(f"Detected move from OCR: {latest_move}")
                        return latest_move
                        
            except Exception as e:
                logging.debug(f"OCR failed for region {i}: {e}")
                continue
        
        return None
        
    except Exception as e:
        logging.error(f"Error in screen-based move detection: {e}")
        return None

def monitor_clipboard_for_move():
    """Monitor clipboard for moves (some apps copy moves to clipboard)"""
    try:
        import pyperclip
        
        # Store initial clipboard content
        initial_content = pyperclip.paste()
        
        # Wait a bit for potential clipboard update
        time.sleep(1)
        
        current_content = pyperclip.paste()
        
        if current_content != initial_content:
            # Check if new content looks like a move
            move_match = re.search(r'\b\d{1,2}[-x]\d{1,2}(?:x\d{1,2})*\b', current_content)
            if move_match:
                move = move_match.group()
                logging.info(f"Detected move from clipboard: {move}")
                return move
        
        return None
        
    except Exception as e:
        logging.debug(f"Clipboard monitoring failed: {e}")
        return None

def get_engine_move():
    """Extract the engine's move from checkerboard application using multiple methods"""
    try:
        logging.info("Attempting to get engine move from checkerboard")
        
        # Method 1: Check for log files
        move_log_paths = [
            "checkerboard_moves.txt",
            "moves.log", 
            "game.pdn",
            "history.txt",
            "latest_move.txt",
            os.path.expanduser("~/Documents/Checkerboard/moves.txt"),
            os.path.expanduser("~/AppData/Local/Checkerboard/moves.log"),
            os.path.expanduser("~/Desktop/moves.txt")
        ]
        
        for log_path in move_log_paths:
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r') as f:
                        content = f.read().strip()
                        lines = content.split('\n')
                        
                        # Check last few lines for moves
                        for line in reversed(lines[-5:]):
                            line = line.strip()
                            move_match = re.search(r'\b\d{1,2}[-x]\d{1,2}(?:x\d{1,2})*\b', line)
                            if move_match:
                                engine_move = move_match.group()
                                logging.info(f"Engine move from log file {log_path}: {engine_move}")
                                return engine_move
                except Exception as e:
                    logging.debug(f"Could not read from {log_path}: {e}")
        
        # Method 2: Screen capture and OCR
        screen_move = detect_move_from_screen()
        if screen_move:
            return screen_move
        
        # Method 3: Clipboard monitoring
        clipboard_move = monitor_clipboard_for_move()
        if clipboard_move:
            return clipboard_move
        
        # Method 4: Look for common temp files
        temp_paths = [
            os.path.expanduser("~/temp_move.txt"),
            "./temp_move.txt",
            "C:/temp/checkerboard_move.txt"
        ]
        
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                try:
                    with open(temp_path, 'r') as f:
                        content = f.read().strip()
                        move_match = re.search(r'\b\d{1,2}[-x]\d{1,2}(?:x\d{1,2})*\b', content)
                        if move_match:
                            engine_move = move_match.group()
                            logging.info(f"Engine move from temp file: {engine_move}")
                            # Clean up temp file
                            os.remove(temp_path)
                            return engine_move
                except Exception as e:
                    logging.debug(f"Could not read temp file {temp_path}: {e}")
        
        logging.warning("Could not detect engine move using any method")
        return None
        
    except Exception as e:
        logging.error(f"Error getting engine move: {e}")
        return None

def get_checkerboard_move(opponent_move, history):
    """Get the best move using checkerboard.exe application"""
    try:
        logging.info(f"Processing opponent move: {opponent_move}")
        
        # Ensure checkerboard.exe is running
        if not find_checkerboard_exe():
            logging.error("Could not find or launch checkerboard.exe")
            return "1-5"  # Default move
        
        # Execute opponent's move in checkerboard
        if not execute_move_in_checkerboard(opponent_move):
            logging.error("Failed to execute opponent move in checkerboard")
            return "1-5"
        
        # Wait for engine to calculate response
        if not wait_for_engine_response():
            logging.error("Engine response timeout")
            return "1-5"
        
        # Get the engine's move
        engine_move = get_engine_move()
        if engine_move:
            logging.info(f"Engine suggested move: {engine_move}")
            return engine_move
        else:
            logging.error("Could not get engine move")
            return "1-5"
            
    except Exception as e:
        logging.error(f"Error in get_checkerboard_move: {e}")
        return "1-5"

def main():
    """Main message loop"""
    logging.info("Checkerboard connector started")
    
    try:
        while True:
            message = read_message()
            if not message:
                break
                
            logging.debug(f"Received message: {message}")
            
            if message.get('command') == 'getMove':
                current_move = message.get('currentMove', '')
                history = message.get('history', [])
                
                best_move = get_checkerboard_move(current_move, history)
                
                response = {'move': best_move}
                send_message(response)
                
    except KeyboardInterrupt:
        logging.info("Connector interrupted by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        logging.info("Checkerboard connector stopped")

if __name__ == "__main__":
    main()
