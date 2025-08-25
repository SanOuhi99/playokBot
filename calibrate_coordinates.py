#!/usr/bin/env python3
"""
Coordinate Calibration Tool for Checkerboard Application
This tool helps you calibrate the click coordinates for your specific checkerboard app
"""

import pyautogui
import pygetwindow as gw
import time
import json
import os

def find_checkerboard_window():
    """Find the checkerboard application window"""
    print("Looking for checkerboard window...")
    
    # Common window titles for checkerboard applications
    titles_to_try = [
        "checkerboard", "Checkerboard", "CheckerBoard", "Draughts", "Damka",
        "Checkers", "checkers", "Dame", "Dama", "International Draughts"
    ]
    
    for title in titles_to_try:
        windows = gw.getWindowsWithTitle(title)
        if windows:
            print(f"Found window: {windows[0].title}")
            return windows[0]
    
    # If not found, list all windows
    print("Checkerboard window not found automatically.")
    print("Available windows:")
    all_windows = gw.getAllWindows()
    
    for i, window in enumerate(all_windows):
        if window.title.strip():  # Only show windows with titles
            print(f"{i}: {window.title}")
    
    try:
        choice = int(input("Enter the number of your checkerboard window: "))
        return all_windows[choice]
    except (ValueError, IndexError):
        print("Invalid selection")
        return None

def calibrate_board_squares(window):
    """Interactive calibration of board squares"""
    print("\nBoard Square Calibration")
    print("=" * 50)
    print("You'll now click on each square of the checkerboard.")
    print("Start with square 1 (bottom-left dark square) and continue to square 32.")
    print("Press SPACE when ready to start, or ESC to cancel.")
    
    # Wait for user to be ready
    while True:
        if pyautogui.getKeyState('space'):
            break
        elif pyautogui.getKeyState('esc'):
            return None
        time.sleep(0.1)
    
    print("Starting calibration in 3 seconds...")
    time.sleep(3)
    
    square_positions = {}
    
    # Focus the checkerboard window
    try:
        window.activate()
        time.sleep(0.5)
    except:
        print("Could not activate window, continue anyway...")
    
    for square_num in range(1, 33):
        print(f"\nClick on square {square_num}")
        print("(Click anywhere to capture position, press ESC to cancel)")
        
        # Wait for mouse click
        while True:
            if pyautogui.getKeyState('esc'):
                print("Calibration cancelled")
                return None
            
            # Check for mouse click
            try:
                # Simple click detection by monitoring mouse position changes
                old_pos = pyautogui.position()
                time.sleep(0.1)
                
                # Check if mouse was clicked (this is a simplified approach)
                if pyautogui.mouseDown():
                    x, y = pyautogui.position()
                    # Convert to relative coordinates within the window
                    rel_x = x - window.left
                    rel_y = y - window.top
                    square_positions[square_num] = (rel_x, rel_y)
                    print(f"Square {square_num}: ({rel_x}, {rel_y})")
                    time.sleep(0.5)  # Debounce
                    break
                    
            except:
                pass
            
            time.sleep(0.05)
    
    return square_positions

def manual_coordinate_entry():
    """Allow manual entry of coordinates if auto-calibration fails"""
    print("\nManual Coordinate Entry")
    print("=" * 30)
    print("Enter coordinates for key squares (relative to window):")
    
    square_positions = {}
    
    # Get coordinates for a few key squares
    key_squares = [1, 5, 28, 32]  # Corners of the board
    
    for square in key_squares:
        while True:
            try:
                x = int(input(f"Square {square} X coordinate: "))
                y = int(input(f"Square {square} Y coordinate: "))
                square_positions[square] = (x, y)
                break
            except ValueError:
                print("Please enter valid numbers")
    
    # Interpolate other squares based on the key squares
    # This is a simplified grid interpolation
    if len(square_positions) >= 4:
        # Calculate grid spacing
        x_spacing = (square_positions[32][0] - square_positions[1][0]) / 7
        y_spacing = (square_positions[28][1] - square_positions[1][1]) / 7
        
        # Fill in all squares
        for row in range(8):
            for col in range(4):
                if row % 2 == 0:  # Even rows
                    square_num = row * 4 + col + 1
                    x = square_positions[1][0] + col * x_spacing * 2
                    y = square_positions[1][1] + row * y_spacing
                else:  # Odd rows
                    square_num = row * 4 + col + 1
                    x = square_positions[1][0] + col * x_spacing * 2 + x_spacing
                    y = square_positions[1][1] + row * y_spacing
                
                if 1 <= square_num <= 32:
                    if square_num not in square_positions:
                        square_positions[square_num] = (int(x), int(y))
    
    return square_positions

def save_calibration(window_title, square_positions):
    """Save the calibration data"""
    calibration_data = {
        "window_title": window_title,
        "square_positions": square_positions,
        "calibration_date": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open("checkerboard_calibration.json", "w") as f:
        json.dump(calibration_data, f, indent=2)
    
    print(f"\nCalibration saved to checkerboard_calibration.json")
    print(f"Window: {window_title}")
    print(f"Squares calibrated: {len(square_positions)}")

def test_calibration(window, square_positions):
    """Test the calibration by clicking on a few squares"""
    print("\nTesting calibration...")
    print("The cursor will move to a few squares to test accuracy.")
    print("Press ENTER to continue or ESC to skip testing.")
    
    response = input()
    if response == '\x1b':  # ESC key
        return
    
    test_squares = [1, 8, 25, 32]  # Test corners
    
    try:
        window.activate()
        time.sleep(1)
    except:
        pass
    
    for square in test_squares:
        if square in square_positions:
            x, y = square_positions[square]
            abs_x = window.left + x
            abs_y = window.top + y
            
            print(f"Moving to square {square}...")
            pyautogui.moveTo(abs_x, abs_y, duration=0.5)
            time.sleep(1)

def main():
    print("Checkerboard Coordinate Calibration Tool")
    print("=" * 40)
    
    # Disable pyautogui failsafe for this tool
    pyautogui.FAILSAFE = False
    
    # Find checkerboard window
    window = find_checkerboard_window()
    if not window:
        print("Could not find checkerboard window. Exiting.")
        return
    
    print(f"Using window: {window.title}")
    print(f"Window position: {window.left}, {window.top}")
    print(f"Window size: {window.width} x {window.height}")
    
    # Choose calibration method
    print("\nCalibration Methods:")
    print("1. Interactive clicking (click on each square)")
    print("2. Manual coordinate entry")
    
    choice = input("Choose method (1 or 2): ").strip()
    
    square_positions = None
    
    if choice == "1":
        square_positions = calibrate_board_squares(window)
    elif choice == "2":
        square_positions = manual_coordinate_entry()
    else:
        print("Invalid choice")
        return
    
    if not square_positions:
        print("Calibration failed or cancelled")
        return
    
    # Save calibration
    save_calibration(window.title, square_positions)
    
    # Test calibration
    test_calibration(window, square_positions)
    
    print("\nCalibration complete!")
    print("The coordinates will be used by the Chrome extension.")
    print("You can re-run this tool anytime to recalibrate.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCalibration cancelled by user")
    except Exception as e:
        print(f"Error: {e}")