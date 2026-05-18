"""
Leveraged ETF Scanner API - FastAPI wrapper for alpha_vantage_scanner.py
Deploy to Vercel/Render for autonomous income.
Usage: Returns BUY/SELL signals for 105+ leveraged ETFs.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI(title="Leveraged ETF Scanner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to cached scan results (updated by cron job)
SCAN_FILE = os.path.expanduser("~/.hermes/skills/finance/free-finance-apis/alpha_vantage_scan.json")

@app.get("/")
def root():
    return {
        "service": "Leveraged ETF Scanner API",
        "docs": "/docs",
        "endpoints": {
            "/scan": "Get latest BUY/SELL signals",
            "/health": "Health check"
        }
    }

@app.get("/scan")
def get_scan_results():
    """Return latest ETF scan results with BUY/SELL signals"""
    if os.path.exists(SCAN_FILE):
        with open(SCAN_FILE) as f:
            return json.load(f)
    return {
        "buy_signals": [],
        "error": "No scan data available. Cron job runs daily at 9:30 AM ET."
    }

@app.get("/health")
def health():
    return {"status": "ok", "scanner": "ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
