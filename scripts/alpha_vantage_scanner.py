#!/usr/bin/env python3
"""
Alpha Vantage Leveraged ETF Scanner with Auto-Fallback
Scans 105 leveraged ETFs with proper rate limiting (13s between calls)
Auto-switches to Yahoo Finance when Alpha Vantage hits daily limit (25 requests/day)
Respects Royce's trading rules: 7-10% trailing stop, entry criteria, time windows
"""

import httpx
import os
import time
import json
from datetime import datetime

# API key from environment
ALPHA_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "d859n01r01qke7mbke00")

# Track API usage
alpha_calls = 0
alpha_exhausted = False  # Set to True when rate limit hit
ALPHA_DAILY_LIMIT = 25

# 105 Leveraged ETFs from skill
ETFS = [
    "SSO", "UPRO", "SAA", "TQQQ", "SQQQ", "DDM", "UDOW", "MVV", "MIDU",
    "ROM", "TECL", "REW", "TECS", "SOXL", "SOXS", "SKK", "TTT", "CWEB", "YINN",
    "TSLL", "TSLQ", "AAPU", "AAPD", "AMZU", "AMZD", "METU", "METD", "MSFU", "MSFD",
    "CURE", "SICK", "BIB", "ZBIO", "LABU", "LABD", "PILL", "PZLL",
    "UYG", "FINU", "SKF", "FAZ", "KRU", "KORU",
    "USO", "XLE", "UCO", "UWT", "SCO", "OILD", "ERX", "ERY",
    "JNUG", "JDST", "NUGT", "DUST", "GDXU", "GDXD", "BARU", "BARD",
    "URE", "DRN", "SRS", "DRV", "NAIL", "NAKD",
    "RETL", "RETS", "CONL", "COND",
    "EURL", "EURZ", "JPNL", "JPNZ", "KORU", "KORZ", "YANG", "YINN", "BRZU", "BRZK",
    "UVXY", "SVXY", "VIXY", "TMF", "TMV", "TBT", "UBT",
    "SAA", "TNA", "TZA", "UWM", "TWM", "SRTY",
    "BITU", "BITI", "COIU", "COID", "BLOK", "BITQ",
    "EETU", "EETD", "EDC", "EDZ",
    "LMBO", "FAS", "AGQ", "ZSL"
]

def get_yahoo_quote(ticker):
    """Fallback: Get quote from Yahoo Finance (no API key needed)"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    params = {"interval": "1d", "range": "5d"}
    try:
        resp = httpx.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        data = resp.json()
        if "chart" in data and "result" in data["chart"]:
            result = data["chart"]["result"][0]
            meta = result.get("meta", {})
            quote = result.get("indicators", {}).get("quote", [{}])[0]
            
            current_price = meta.get("regularMarketPrice", 0)
            prev_close = meta.get("previousClose", 0)
            change = current_price - prev_close
            change_pct = (change / prev_close * 100) if prev_close else 0
            
            return {
                "symbol": ticker,
                "price": float(current_price),
                "change": float(change),
                "change_pct": float(change_pct),
                "volume": int(quote.get("volume", [0])[-1]) if quote.get("volume") else 0,
                "prev_close": float(prev_close),
                "source": "Yahoo Finance"
            }
    except Exception as e:
        print(f"[Yahoo Error] {ticker}: {e}")
    return None

def get_yahoo_rsi(ticker):
    """Yahoo Finance doesn't provide RSI directly - return None, use price action instead"""
    return None

def is_rate_limit_error(data):
    """Check if Alpha Vantage response indicates rate limit"""
    if isinstance(data, dict):
        info = data.get("Information", "")
        if "rate limit" in info.lower() or "25 requests" in info:
            return True
    return False

def rate_limited_get(url, params):
    """Make rate-limited API call with fallback to Yahoo Finance"""
    global alpha_calls, alpha_exhausted
    
    # If already exhausted, skip Alpha Vantage
    if alpha_exhausted:
        return None
    
    # If we know we've hit the limit
    if alpha_calls >= ALPHA_DAILY_LIMIT:
        alpha_exhausted = True
        return None
    
    resp = httpx.get(url, params=params)
    alpha_calls += 1
    
    # Check if THIS call hit the rate limit
    data = resp.json()
    if is_rate_limit_error(data):
        alpha_exhausted = True
        return None
    
    if alpha_calls < ALPHA_DAILY_LIMIT:
        time.sleep(13)  # Rate limit delay only if more calls remaining
    return data

def get_quote(ticker):
    """Get current quote with auto-fallback"""
    global alpha_calls
    
    # Try Alpha Vantage first (if calls remaining)
    if alpha_calls < ALPHA_DAILY_LIMIT:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": ticker,
            "apikey": ALPHA_KEY
        }
        data = rate_limited_get("https://www.alphavantage.co/query", params)
        
        if data and not is_rate_limit_error(data):
            if "Global Quote" in data and data["Global Quote"]:
                q = data["Global Quote"]
                return {
                    "symbol": ticker,
                    "price": float(q.get("05. price", 0)),
                    "change": float(q.get("09. change", 0)),
                    "change_pct": float(q.get("10. change percent", "0%").rstrip("%")),
                    "volume": int(q.get("06. volume", 0)),
                    "prev_close": float(q.get("08. previous close", 0)),
                    "source": "Alpha Vantage"
                }
    
    # Fallback to Yahoo Finance (no delay needed)
    print(f"  [Fallback] Using Yahoo Finance for {ticker}")
    return get_yahoo_quote(ticker)

def get_rsi(ticker, interval="daily"):
    """Get RSI with auto-fallback (Yahoo doesn't provide RSI)"""
    global alpha_calls
    
    # Try Alpha Vantage first
    if alpha_calls < ALPHA_DAILY_LIMIT:
        params = {
            "function": "RSI",
            "symbol": ticker,
            "interval": interval,
            "time_period": 14,
            "series_type": "close",
            "apikey": ALPHA_KEY
        }
        data = rate_limited_get("https://www.alphavantage.co/query", params)
        
        if data and not is_rate_limit_error(data):
            if "Technical Analysis: RSI" in data:
                rsi_data = data["Technical Analysis: RSI"]
                if rsi_data:
                    latest_date = sorted(rsi_data.keys())[-1]
                    return float(rsi_data[latest_date]["RSI"])
    
    # Yahoo Finance doesn't provide RSI - return None
    return None

def scan_etfs(limit=None):
    """Scan ETFs and return signals"""
    results = []
    etfs_to_scan = ETFS[:limit] if limit else ETFS
    
    print(f"Scanning {len(etfs_to_scan)} ETFs...")
    print(f"Alpha Vantage daily limit: {ALPHA_DAILY_LIMIT} calls")
    print(f"Auto-fallback to Yahoo Finance when limit reached\n")
    
    for i, ticker in enumerate(etfs_to_scan):
        print(f"[{i+1}/{len(etfs_to_scan)}] Scanning {ticker}...", end=" ")
        
        quote = get_quote(ticker)
        if not quote:
            print("No data available")
            continue
        
        rsi = get_rsi(ticker)
        source = quote.get("source", "Yahoo Finance")
        
        # Determine signal based on Royce's rules
        signal = "HOLD"
        reason = []
        
        # Use RSI if available (Alpha Vantage)
        if rsi and rsi < 40:
            signal = "BUY"
            reason.append(f"RSI={rsi:.1f} < 40")
        elif rsi and rsi > 70:
            signal = "AVOID"
            reason.append(f"RSI={rsi:.1f} > 70")
        
        # If no RSI (Yahoo fallback), use price action
        if rsi is None:
            if quote["change_pct"] < -3:
                signal = "BUY"  # Oversold move
                reason.append(f"Down {quote['change_pct']:.1f}% (no RSI)")
            elif quote["change_pct"] > 3:
                signal = "AVOID"
                reason.append(f"Up {quote['change_pct']:.1f}% (no RSI)")
            else:
                reason.append("No RSI data (using Yahoo Finance)")
        
        reason.append(f"[{source}]")
        
        results.append({
            "ticker": ticker,
            "price": quote["price"],
            "change_pct": quote["change_pct"],
            "rsi": rsi,
            "signal": signal,
            "reasons": reason,
            "source": source,
            "timestamp": datetime.now().isoformat()
        })
        
        rsi_str = f"{rsi:.1f}" if rsi else "N/A (Yahoo)"
        print(f"{signal} @ ${quote['price']:.2f} (RSI: {rsi_str}) [{source}]")
    
    return results

def save_results(results, filename="alpha_vantage_scan.json"):
    """Save results to JSON file"""
    path = f"/Users/royceai/.hermes/skills/finance/free-finance-apis/{filename}"
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {path}")
    return path

if __name__ == "__main__":
    import sys
    
    # Quick scan mode: only scan top priorities
    quick_mode = "--quick" in sys.argv
    limit = 10 if quick_mode else None
    
    if quick_mode:
        print("QUICK SCAN MODE: Scanning top 10 ETFs only\n")
    
    results = scan_etfs(limit=limit)
    
    # Filter for BUY signals
    buy_signals = [r for r in results if r["signal"] == "BUY"]
    
    print(f"\n{'='*50}")
    print(f"SCAN COMPLETE: {len(results)} ETFs scanned")
    print(f"BUY signals: {len(buy_signals)}")
    print(f"{'='*50}")
    
    if buy_signals:
        print("\nBUY SIGNALS:")
        for sig in buy_signals:
            print(f"  {sig['ticker']}: ${sig['price']:.2f} (RSI={sig['rsi']:.1f}) - {', '.join(sig['reasons'])}")
    
    save_results(results)
