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

@app.get("/")
def root():
    return {"service": "Leveraged ETF Scanner API", "docs": "/docs", "endpoints": {"/scan": "Get BUY/SELL signals", "/health": "Health check"}}

@app.get("/scan")
def scan_etfs():
    scan_file = os.path.expanduser("~/.hermes/skills/finance/free-finance-apis/alpha_vantage_scan.json")
    if os.path.exists(scan_file):
        with open(scan_file) as f:
            return json.load(f)
    return {"buy_signals": [], "error": "No scan data available. Cron job runs daily at 9:30 AM ET."}

@app.get("/health")
def health():
    return {"status": "ok", "scanner": "ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
