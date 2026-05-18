---
name: free-finance-apis
description: Integrate free tier Alpha Vantage API and Yahoo Finance fallback for market data, technicals, and fundamentals to generate trading signals aligned with Royce's risk rules and Alpaca live execution.
---

# Free Finance APIs Integration

## Prerequisites
- Alpha Vantage API key (free tier: 25 calls/day TOTAL, 5 calls/minute) -> env var: ALPHA_VANTAGE_API_KEY
  Key confirmed working: d859n01r01qke7mbke00 (set in ~/.zshrc)
  **CRITICAL**: Free tier = 25 calls/day (not 800/day as commonly misstated)
  - Full 105 ETF scan needs 210 calls = impossible on free tier
  - Solution: Auto-fallback to Yahoo Finance when limit reached

## When to Use
- Generate trading signals for leveraged ETFs (2x/3x) from 100-leveraged-etf-list
- Scan crypto pairs (tier 1 active) for Alpaca crypto trading
- Apply technical indicators (RSI, MACD) for entry/exit
- Respect Royce's risk rules automatically
- **Note**: If user says "forget X" or "drop X", remove that approach immediately (e.g., "Forget unusual whales" = delete skill)

## API Capabilities
## Best Websites for Technical Analysis (Researched)

### Tier 1: Accessible (No API Key, Scrapeable)
1. **Yahoo Finance** (already integrated)
   - URL: https://finance.yahoo.com
   - Data: Real-time quotes, historical prices, basic fundamentals
   - Access: API-like endpoint at `query1.finance.yahoo.com/v8/finance/chart/`
   - Limitation: No RSI/MACD (price action only)

2. **Finviz** (https://finviz.com)
   - Data: RSI, MACD, SMA, EMA, Bollinger Bands
   - Tools: Stock screener, heatmaps, charts
   - Access: Partial (returns JS-heavy pages, may need browser tool)
   - Note: Free tier has delays, but data visible

3. **StockCharts.com** (https://stockcharts.com)
   - Data: SharpCharts, RSI, MACD, Point & Figure
   - Tools: Symbol summary, technical analysis
   - Access: Free tools available, may have rate limits

### Tier 2: Advanced (May Need Browser Tool)
1. **TradingView** (https://tradingview.com)
   - Best charts + 100+ indicators (RSI, MACD, BBANDS)
   - Free tier: Limited but usable
   - Access: Heavy anti-bot (use browser tool, not curl)

2. **Barchart** (https://barchart.com)
   - Technical opinions, RSI, MACD, moving averages
   - Access: Moderate (some endpoints scrapeable)

### Recommendation for Royce's Setup
- **Primary**: Yahoo Finance (fast, reliable, no limits, use for 105 ETF quotes)
- **Secondary**: TradingView browser automation (for RSI/MACD verification, once per day for top picks)
- **Tertiary**: Alpha Vantage (25/day, use for batch RSI when available)

### Usage Pattern
1. Run daily scan with Yahoo Finance (fast, ~2 mins for 105 ETFs)
2. Get BUY/AVOID signals based on price action (no RSI)
3. For top 3-5 signals, use TradingView browser tool to verify RSI/MACD
4. Only enter trades when RSI < 40 (verified) AND price above 20-day MA AND positive MACD

### Yahoo Finance (Fallback, No API Key)
- Real-time quotes, price, change %
- Volume data
- **Limitation**: No technical indicators (RSI, MACD not available)
- **Advantage**: No rate limits, no API key needed

## Auto-Fallback Logic (User Mandated)
When user says "make sure you rotate" or "don't max it out":
1. Try Alpha Vantage first for each ticker
2. Detect rate limit error in response JSON ("Information" field contains "rate limit" or "25 requests")
3. Set `alpha_exhausted = True` to skip all future Alpha Vantage calls
4. Switch to Yahoo Finance (no delays needed)
5. Adjust signal logic: use price action (±3% thresholds) instead of RSI when using Yahoo

## Integration with Royce's Trading Rules
1. **Time Windows**:
   - ETF alerts only 9:30 AM - 4 PM ET weekdays
   - Crypto bots every 3 hours
   - No alerts/cron 9 PM - 7 AM (sleep schedule)
2. **Risk Filters**:
   - Check CPI/PPI/Fed/NFP days (exit ETFs before release)
   - Apply 7-10% trailing stop
   - Macro risk = manual exit on sudden moves
3. **Alpaca Execution**:
   - Use alpaca-trading skill for live order placement
   - Crypto: ACTIVE (tier 1)
   - Live only, no paper trading

## Scanner API (Autonomous Income)
**Generate passive income by deploying the scanner as a paid API.**

### Files
- `api/app.py` - FastAPI app with `/scan` and `/health` endpoints
- `api/vercel.json` - Vercel serverless config
- `api/requirements.txt` - FastAPI/uvicorn dependencies
- GitHub repo: https://github.com/royceAIsolutions/leveraged-etf-scanner-api

### Deploy to Vercel
Follow `vercel-deployment` skill for full steps. Quick reference:
1. Save Vercel token with `echo -n "YOUR_TOKEN" > ~/.vercel/token` (no trailing newline)
2. Link repo via Vercel dashboard (Settings → Git → Connect Repo) if API linking fails
3. Auto-deploys on git push to main branch
4. Test: `https://<your-project>.vercel.app/health` → `{"status": "ok"}`

**Pitfalls:**
- Vercel API project linking (PUT /projects/{id}/link) may fail even with valid tokens → use manual dashboard
- Token file must have no trailing newlines (use `echo -n` to save)

### Deploy to Render (Alternative)
1. Push `api/` to GitHub repo
2. Connect repo to render.com
3. Auto-deploys on git push

### Monetize
- List on RapidAPI: $0.50 per call
- 80% revenue to you (RapidAPI takes 20%)
- Fully passive after setup

## Common Pitfalls

### API Key Format Confusion
- **Alpha Vantage keys**: Longer format (e.g., `d859n01r01qke7mbke00`) - 20+ chars
- **Finnhub API keys**: Shorter format (e.g., `c4ah8m9r01qke7mbke00`) - 18-20 chars
- **Finnhub Webhook Secrets**: NOT for REST API calls (X-Finnhub-Secret header only)
- Finnhub API keys provided by user are all invalid, do not use Finnhub.
- Alpha Vantage rate limit: 25/day, auto-fallback to Yahoo Finance when exhausted.
- Yahoo Finance query1 may return 429/403, use query2 endpoint instead.
- Tavily web search returns 432 error, use `web_search_plus` with provider='brave' or 'exa' for economic calendar checks.
- Vercel CLI requires interactive browser login (`vercel login`) for deployment, cannot be automated. Manual step required once.

## Monetization: ETF Scanner API
Turn the `alpha_vantage_scanner.py` into a paid public API for passive income:
1. **Files Created** (in `api/` subdirectory):
   - `app.py`: FastAPI wrapper with `/scan` (returns BUY/SELL signals) and `/health` endpoints
   - `requirements.txt`: FastAPI, uvicorn dependencies
   - `vercel.json`: Vercel deployment config
2. **Deploy Workflow**:
   - Automatable steps: Create API files, commit to git (already done)
   - Manual step: User runs `vercel login` (one-time browser auth)
   - After auth: Run `vercel --prod` from `api/` to deploy, get public URL
3. **Monetize**: List on RapidAPI with $0.50/call pricing, 80% revenue share. Daily cron job (ID: c70b1a6ae155) updates cached scan results automatically.

## Full Execution Rule
When user approves task execution (e.g., responds "Y"), complete all automatable steps immediately. Do not wait or ask for mid-task permission. Clearly list remaining manual steps upfront after completing automatable work.
- **Never reuse keys across services** - keys fail across different providers

### Finding Finnhub API Key (If Needed Later)
1. Log in at https://finnhub.io/login
2. Go to Dashboard -> **"API Key" section** (NOT "Webhook" section)
3. Click "Generate API Key" if none visible
4. Copy key from Dashboard display (not URL bar or webhook config)

### Rate Limit Handling
- Alpha Vantage: 25/day TOTAL, 5/min -> 13s sleep between calls
- Yahoo Finance: No limits, no delays
- **Rotation Strategy**: When scanning large ticker lists, design for auto-fallback (not manual switching)

## Scanner Script
- **Location**: `scripts/alpha_vantage_scanner.py`
- **Key Feature**: Auto-fallback to Yahoo Finance (user mandated: "Once Alpha Vantage maxes, automatically go to next best option")
- **Features**:
  - Scans 105 leveraged ETFs from `100-leveraged-etf-list`
  - Auto-detects Alpha Vantage rate limits and switches to Yahoo
  - Signal generation: BUY (RSI<40 or down >3%), AVOID (RSI>70 or up >3%), HOLD
  - Respects Royce's trading rules (7-10% trailing stop, entry criteria)
- **Usage**:
  - Quick scan (10 ETFs): `python3 scripts/alpha_vantage_scanner.py --quick`
  - Full scan (105 ETFs): `python3 scripts/alpha_vantage_scanner.py`
  - Note: Full scan auto-switches to Yahoo after 25 Alpha Vantage calls

## Related Skills
- alpaca-trading
- autonomous-trading-system
- leveraged-etf-research-process
- economic-events-trading
- 100-leveraged-etf-list
- 100-stock-trading-list
