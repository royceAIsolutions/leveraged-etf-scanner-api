import json
import os
from http.server import BaseHTTPRequestHandler
import urllib.request

SCAN_FILE = "/tmp/alpha_vantage_scan.json"

def get_latest_signals():
    """Read cached scan results or return empty"""
    if os.path.exists(SCAN_FILE):
        with open(SCAN_FILE) as f:
            return json.load(f)
    return {"buy_signals": [], "error": "No scan data available"}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == "/health":
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            data = get_latest_signals()
            self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        pass  # Suppress logs
