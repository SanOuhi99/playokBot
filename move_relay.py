import json, time, threading, logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import pygetwindow as gw
import pyautogui

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    handlers=[logging.FileHandler('relay.log'), logging.StreamHandler()]
)

class MoveHandler(BaseHTTPRequestHandler):
    def _send(self, code=200, obj=None):
        self.send_response(code)
        self.send_header('Content-Type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','POST,OPTIONS')
        self.end_headers()
        if obj is not None:
            self.wfile.write(json.dumps(obj).encode())

    def do_OPTIONS(self):
        self._send(200)

def do_POST(self):
    logging.info(f"📥 Incoming POST request on path: {self.path}")

    try:
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            logging.warning("! Empty POST request received.")
            return self._send(400, {'error': 'Empty request'})

        data = json.loads(self.rfile.read(length))
        logging.info(f" Parsed JSON data: {data}")

        move = data.get('move')
        if not move:
            logging.warning("! 'move' key not found in JSON.")
            return self._send(400, {'error': 'No move in request'})

        logging.info(f"-> Move received: {move}")

        threading.Thread(target=run_move_sequence, args=(move,)).start()
        return self._send(200, {'status': 'ok'})

    except json.JSONDecodeError:
        logging.exception("[X] JSON parsing failed.")
        return self._send(400, {'error': 'Invalid JSON'})

    except Exception as e:
        logging.exception("[X] Exception during POST handling")
        return self._send(500, {'error': str(e)})


def run_move_sequence(move):
    logging.info(f"-> Got move: {move}")
    checker = None
    for _ in range(3):
        wins = gw.getWindowsWithTitle('CheckerBoard')
        if wins:
            checker = wins[0]
            checker.activate()
            time.sleep(0.5)
            break
        time.sleep(1)
    if not checker:
        logging.error("CheckerBoard window not found")
        return

    # Simulate click to focus position (adjust coords as needed)
    x, y = checker.left + 200, checker.top + 200
    pyautogui.click(x, y)

    # Type move via keyboard
    logging.info(f"Typing move: {move}")
    pyautogui.write(move)
    pyautogui.press('enter')
def run_server():
    server_address = ('localhost', 8123)
    httpd = HTTPServer(server_address, MoveHandler)
    logging.info('Starting Checkerboard move relay on http://localhost:8123')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info(" Server stopped manually")
    finally:
        httpd.server_close()

if __name__ == '__main__':
    run_server()

