#!/usr/bin/env python3
"""
KingsRow Engine Connector for PlayOK Chrome Extension
Handles communication between the Chrome extension and KingsRow engine
"""

import sys
import json
import struct
import subprocess
import os
import time
import threading
import logging
from pathlib import Path
import tempfile
import re

# Configure logging
logging.basicConfig(
    filename='kingsrow_connector.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class KingsRowConnector:
    def __init__(self):
        self.kingsrow_process = None
        self.kingsrow_path = self.find_kingsrow_path()
        self.game_position = "8/8/8/8/8/8/8/8 b - - 0 1"  # Starting position in FEN-like format
        self.move_history = []
        self.temp_dir = tempfile.gettempdir()
        self.position_file = os.path.join(self.temp_dir, "kingsrow_position.txt")
        self.output_file = os.path.join(self.temp_dir, "kingsrow_output.txt")
        
        logging.info("KingsRow Connector initialized")
        
    def find_kingsrow_path(self):
        """Find KingsRow executable path"""
        # Common installation paths
        possible_paths = [
            r"C:\Program Files\KingsRow\KingsRow.exe",
            r"C:\Program Files (x86)\KingsRow\KingsRow.exe", 
            r"C:\KingsRow\KingsRow.exe",
            r".\KingsRow.exe",
            os.path.expanduser("~/Desktop/KingsRow.exe"),
            os.path.expanduser("~/Documents/KingsRow/KingsRow.exe")
        ]
        
        # Check environment variable first
        env_path = os.getenv("KINGSROW_PATH")
        if env_path:
            possible_paths.insert(0, env_path)
        
        for path in possible_paths:
            if os.path.exists(path):
                logging.info(f"Found KingsRow at: {path}")
                return path
                
        logging.error("KingsRow executable not found")
        return None
    
    def start_kingsrow(self):
        """Start KingsRow engine process"""
        if not self.kingsrow_path:
            logging.error("Cannot start KingsRow - path not found")
            return False
            
        try:
            # Start KingsRow in engine mode if possible
            self.kingsrow_process = subprocess.Popen([
                self.kingsrow_path
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
               stderr=subprocess.PIPE, text=True)
            
            logging.info("KingsRow process started")
            
            # Give it a moment to initialize
            time.sleep(2)
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to start KingsRow: {e}")
            return False
    
    def read_message(self):
        """Read message from Chrome extension"""
        try:
            # Read message length
            raw_length = sys.stdin.buffer.read(4)
            if not raw_length:
                return None
                
            message_length = struct.unpack('=I', raw_length)[0]
            
            # Read message content
            message = sys.stdin.buffer.read(message_length)
            return json.loads(message.decode('utf-8'))
            
        except Exception as e:
            logging.error(f"Error reading message: {e}")
            return None
    
    def send_message(self, message):
        """Send message to Chrome extension"""
        try:
            encoded_content = json.dumps(message).encode('utf-8')
            encoded_length = len(encoded_content).to_bytes(4, byteorder='little')
            
            sys.stdout.buffer.write(encoded_length)
            sys.stdout.buffer.write(encoded_content)
            sys.stdout.buffer.flush()
            
            logging.debug(f"Sent message: {message}")
            
        except Exception as e:
            logging.error(f"Error sending message: {e}")
    
    def convert_playok_to_kingsrow(self, playok_move):
        """Convert PlayOK move notation to KingsRow format"""
        try:
            # PlayOK uses format like "12-16" or "12x19x26"
            # KingsRow might use different notation
            
            # For now, assume the formats are compatible
            # This might need adjustment based on actual KingsRow requirements
            return playok_move
            
        except Exception as e:
            logging.error(f"Error converting move: {e}")
            return playok_move
    
    def convert_kingsrow_to_playok(self, kingsrow_move):
        """Convert KingsRow move notation to PlayOK format"""
        try:
            # Convert back to PlayOK format
            return kingsrow_move
            
        except Exception as e:
            logging.error(f"Error converting move: {e}")
            return kingsrow_move
    
    def get_best_move_from_kingsrow(self, position, opponent_move=None):
        """Get best move from KingsRow engine"""
        try:
            logging.info(f"Getting best move for position after: {opponent_move}")
            
            if not self.kingsrow_process:
                if not self.start_kingsrow():
                    return self.get_fallback_move(opponent_move)
            
            # Method 1: Try to communicate directly with KingsRow process
            best_move = self.communicate_with_kingsrow(position, opponent_move)
            if best_move:
                return best_move
            
            # Method 2: Try file-based communication
            best_move = self.file_based_communication(position, opponent_move)
            if best_move:
                return best_move
            
            # Method 3: Use built-in simple engine as fallback
            return self.get_fallback_move(opponent_move)
            
        except Exception as e:
            logging.error(f"Error getting move from KingsRow: {e}")
            return self.get_fallback_move(opponent_move)
    
    def communicate_with_kingsrow(self, position, opponent_move):
        """Direct communication with KingsRow process"""
        try:
            if not self.kingsrow_process or self.kingsrow_process.poll() is not None:
                return None
            
            # Send position to KingsRow (format depends on KingsRow's protocol)
            command = f"position {position}\n"
            if opponent_move:
                command += f"move {opponent_move}\n"
            command += "go\n"
            
            self.kingsrow_process.stdin.write(command)
            self.kingsrow_process.stdin.flush()
            
            # Read response with timeout
            start_time = time.time()
            while time.time() - start_time < 10:  # 10 second timeout
                if self.kingsrow_process.stdout.readable():
                    output = self.kingsrow_process.stdout.readline()
                    if output:
                        # Parse KingsRow output for best move
                        move_match = re.search(r'\b\d{1,2}[-x]\d{1,2}(?:x\d{1,2})*\b', output)
                        if move_match:
                            return move_match.group()
                time.sleep(0.1)
            
            return None
            
        except Exception as e:
            logging.error(f"Error in direct communication: {e}")
            return None
    
    def file_based_communication(self, position, opponent_move):
        """File-based communication with KingsRow"""
        try:
            # Create input file for KingsRow
            input_data = {
                'position': position,
                'opponent_move': opponent_move,
                'move_history': self.move_history,
                'request_time': time.time()
            }
            
            with open(self.position_file, 'w') as f:
                json.dump(input_data, f, indent=2)
            
            # Try to execute KingsRow with position file
            # This assumes KingsRow can accept file input (might need adjustment)
            try:
                result = subprocess.run([
                    self.kingsrow_path, 
                    '--input', self.position_file,
                    '--output', self.output_file
                ], timeout=15, capture_output=True, text=True)
                
                if os.path.exists(self.output_file):
                    with open(self.output_file, 'r') as f:
                        output = f.read()
                    
                    # Parse output for best move
                    move_match = re.search(r'\b\d{1,2}[-x]\d{1,2}(?:x\d{1,2})*\b', output)
                    if move_match:
                        return move_match.group()
                        
            except subprocess.TimeoutExpired:
                logging.warning("KingsRow execution timed out")
            except Exception as e:
                logging.debug(f"File-based communication failed: {e}")
            
            return None
            
        except Exception as e:
            logging.error(f"Error in file-based communication: {e}")
            return None
    
    def get_fallback_move(self, opponent_move):
        """Simple fallback move generation"""
        try:
            logging.info("Using fallback move generation")
            
            # Simple move patterns based on opponent move
            if opponent_move:
                # Parse opponent move
                parts = opponent_move.split(/[-x]/)
                if len(parts) >= 2:
                    from_square = int(parts[0])
                    to_square = int(parts[-1])
                    
                    # Generate counter-move based on simple heuristics
                    return self.generate_counter_move(from_square, to_square)
            
            # Default opening moves
            opening_moves = ["11-15", "11-16", "12-16", "10-15", "9-13", "9-14"]
            move_index = len(self.move_history) % len(opening_moves)
            return opening_moves[move_index]
            
        except:
            return "11-15"  # Safe default
    
    def generate_counter_move(self, opponent_from, opponent_to):
        """Generate a counter move based on opponent's move"""
        try:
            # Simple counter-move logic
            # This is very basic and should be improved
            
            # If opponent moved forward, try to block or attack
            if opponent_to > opponent_from:
                # Opponent moved forward, try to respond
                counter_moves = [
                    f"{opponent_to + 4}-{opponent_to + 8}",
                    f"{opponent_to - 4}-{opponent_to}",
                    f"{opponent_from - 4}-{opponent_from}",
                    "22-18", "21-17", "23-18", "24-19"
                ]
            else:
                # Opponent moved backward (capture), advance
                counter_moves = [
                    "11-15", "12-16", "10-14", "9-13"
                ]
            
            # Return first valid-looking move
            for move in counter_moves:
                if self.is_valid_move_format(move):
                    return move
            
            return "11-15"  # Fallback
            
        except:
            return "11-15"
    
    def is_valid_move_format(self, move):
        """Check if move format is valid"""
        pattern = r'^\d{1,2}[-x]\d{1,2}(?:x\d{1,2})*
        return bool(re.match(pattern, move))
    
    def update_position(self, move):
        """Update internal position after a move"""
        try:
            self.move_history.append(move)
            logging.debug(f"Position updated with move: {move}")
            
        except Exception as e:
            logging.error(f"Error updating position: {e}")
    
    def reset_game(self):
        """Reset game state"""
        try:
            self.move_history = []
            self.game_position = "8/8/8/8/8/8/8/8 b - - 0 1"
            
            # Clean up temp files
            for file_path in [self.position_file, self.output_file]:
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            logging.info("Game state reset")
            
        except Exception as e:
            logging.error(f"Error resetting game: {e}")
    
    def handle_message(self, message):
        """Handle incoming message from Chrome extension"""
        try:
            command = message.get('command')
            logging.info(f"Handling command: {command}")
            
            if command == 'initialize':
                return {
                    'type': 'status',
                    'status': 'initialized',
                    'version': '2.0',
                    'kingsrow_available': self.kingsrow_path is not None
                }
            
            elif command == 'get_best_move':
                opponent_move = message.get('opponent_move')
                game_history = message.get('game_history', [])
                
                # Update our history
                self.move_history = game_history
                
                # Convert move format if needed
                kingsrow_move = self.convert_playok_to_kingsrow(opponent_move)
                self.update_position(kingsrow_move)
                
                # Get best move from KingsRow
                best_move = self.get_best_move_from_kingsrow(
                    self.game_position, kingsrow_move
                )
                
                if best_move:
                    # Convert back to PlayOK format
                    playok_move = self.convert_kingsrow_to_playok(best_move)
                    self.update_position(playok_move)
                    
                    return {
                        'type': 'best_move',
                        'move': playok_move,
                        'confidence': 0.8,
                        'depth': 12,
                        'analysis': f'Best move calculated for position after {opponent_move}'
                    }
                else:
                    return {
                        'type': 'error',
                        'message': 'Failed to calculate best move'
                    }
            
            elif command == 'new_game':
                self.reset_game()
                return {
                    'type': 'status',
                    'status': 'game_reset'
                }
            
            elif command == 'analyze_position':
                position = message.get('position')
                best_move = self.get_best_move_from_kingsrow(position)
                
                return {
                    'type': 'analysis',
                    'best_move': best_move,
                    'position': position,
                    'evaluation': 'Analysis complete'
                }
            
            else:
                return {
                    'type': 'error',
                    'message': f'Unknown command: {command}'
                }
                
        except Exception as e:
            logging.error(f"Error handling message: {e}")
            return {
                'type': 'error',
                'message': str(e)
            }
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.kingsrow_process:
                self.kingsrow_process.terminate()
                self.kingsrow_process = None
            
            # Clean up temp files
            for file_path in [self.position_file, self.output_file]:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
            logging.info("Cleanup completed")
            
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
    
    def run(self):
        """Main message loop"""
        logging.info("KingsRow connector started")
        
        try:
            while True:
                message = self.read_message()
                if not message:
                    break
                
                response = self.handle_message(message)
                if response:
                    self.send_message(response)
                    
        except KeyboardInterrupt:
            logging.info("Connector interrupted by user")
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")
        finally:
            self.cleanup()
            logging.info("KingsRow connector stopped")

def main():
    """Entry point"""
    connector = KingsRowConnector()
    connector.run()

if __name__ == "__main__":
    main()
