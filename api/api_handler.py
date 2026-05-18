from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request

def handler(request, response):
    """Vercel Python serverless handler"""
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    
    if request.path == "/health":
        response.status = 200
        response.json = {"status": "ok"}
        return response
    
    # Return cached scan data
    scan_file = "/tmp/alpha_vantage_scan.json"
    if os.path.exists(scan_file):
        with open(scan_file) as f:
            data = json.load(f)
        response.status = 200
        response.json = data
    else:
        response.status = 200
        response.json = {"buy_signals": [], "error": "No scan data. Run cron job first."}
    
    return response
