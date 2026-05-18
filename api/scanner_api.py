from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json
import os

app = FastAPI(title="Leveraged ETF Scanner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SCANNER_PATH = os.path.expanduser("~/.hermes/skills/finance/free-finance-apis/scripts/alpha_vantage_scanner.py")

@app.get("/scan")
def scan_etfs(quick: bool = False):
    """Return BUY/SELL signals for 105+ leveraged ETFs"""
    try:
        cmd = ["python3", SCANNER_PATH]
        if quick:
            cmd.append("--quick")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # Read latest scan results
        scan_file = os.path.expanduser("~/.hermes/skills/finance/free-finance-apis/alpha_vantage_scan.json")
        if os.path.exists(scan_file):
            with open(scan_file) as f:
                data = json.load(f)
            return {"status": "success", "data": data}
        return {"status": "error", "output": result.stdout[-2000:]}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/health")
def health():
    return {"status": "ok", "scanner": "ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
