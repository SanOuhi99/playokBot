#!/usr/bin/env python3
import sys
import json
import struct

def read_message():
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length:
        return None
    message_length = struct.unpack('=I', raw_length)[0]
    message = sys.stdin.buffer.read(message_length)
    return json.loads(message.decode('utf-8'))

def send_message(message):
    encoded_message = json.dumps(message).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('=I', len(encoded_message)))
    sys.stdout.buffer.write(encoded_message)
    sys.stdout.buffer.flush()

def main():
    while True:
        try:
            message = read_message()
            if not message:
                break
            
            # Simple response - just return a basic move
            if message.get('command') == 'getMove':
                response = {'move': '11-15'}  # Basic opening move
                send_message(response)
                
        except Exception:
            break

if __name__ == "__main__":
    main()
