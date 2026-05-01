# 🤖 Simple Crypto Trading Bot

**Minimal, working trading bot with just the essentials.**

## What It Does

1. Scans 5 crypto pairs every 60 seconds
2. Asks Gemini AI for trading signals
3. Places trades when AI is 75%+ confident
4. Sends Telegram notifications
5. Uses REAL money on Bybit Mainnet

## Files You Need

- `simple_bot.py` - The entire bot (one file!)
- `.env.simple` - Your API keys
- `requirements.simple.txt` - Python packages

## Setup (5 Minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.simple.txt
```

### 2. Configure API Keys

Copy `.env.simple` to `.env` and fill in:

```bash
cp .env.simple .env
nano .env
```

Required:
- `BYBIT_API_KEY` - Your Bybit API key (already filled)
- `BYBIT_API_SECRET` - Your Bybit secret (already filled)
- `GEMINI_API_KEY` - Get from https://aistudio.google.com/app/apikey
- `TELEGRAM_BOT_TOKEN` - Get from @BotFather on Telegram
- `TELEGRAM_CHAT_ID` - Your Telegram chat ID

### 3. Run Locally

```bash
python simple_bot.py
```

You'll see:
```
🤖 SIMPLE CRYPTO TRADING BOT
Mode: REAL TRADING (Bybit Mainnet)
Pairs: BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT
Trade Size: $20 × 5x leverage
💰 Balance: $XXX.XX USDT

🔍 Scanning 5 pairs...
  BTCUSDT: WAIT (45%)
  ETHUSDT: BUY (82%)
  ...
```

## Deploy to Render

### 1. Update `render.yaml`

```yaml
services:
  - type: web
    name: simple-crypto-bot
    runtime: python
    buildCommand: pip install -r requirements.simple.txt
    startCommand: python simple_bot.py
    envVars:
      - key: BYBIT_API_KEY
        sync: false
      - key: BYBIT_API_SECRET
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: TELEGRAM_CHAT_ID
        sync: false
```

### 2. Push to GitHub

```bash
git add simple_bot.py .env.simple requirements.simple.txt SIMPLE_BOT_README.md
git commit -m "Add simplified trading bot"
git push origin main
```

### 3. Deploy on Render

1. Go to Render Dashboard
2. Update environment variables with your API keys
3. Redeploy

Bot starts automatically!

## How It Works

### Scanning
- Every 60 seconds, checks 5 crypto pairs
- Gets current price from Bybit
- Asks Gemini AI: "Should I buy, sell, or wait?"

### Trading
- Only trades if AI is 75%+ confident
- Uses $20 USDT per trade with 5x leverage ($100 position)
- Places market orders (instant execution)

### Safety
- Only trades with real money (no testnet confusion)
- Waits 5 minutes after each trade
- Sends Telegram alerts for every action

## Configuration

Edit these values in `simple_bot.py`:

```python
WATCHLIST = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
TRADE_AMOUNT_USDT = 20.0  # Trade size
LEVERAGE = 5              # Leverage multiplier
SCAN_INTERVAL = 60        # Seconds between scans
MIN_CONFIDENCE = 75       # AI confidence threshold
```

## Telegram Notifications

You'll receive messages for:
- ✅ Bot started
- 📊 Trade executed (with details)
- ❌ Trade failed
- 🛑 Bot stopped

## Troubleshooting

### "Error getting balance"
- Check Bybit API permissions: Read + Wallet + Trade
- Verify you're using Mainnet keys (not testnet)

### "AI error"
- Check GEMINI_API_KEY is correct
- Verify you have API quota remaining

### "Order failed"
- Check you have enough USDT balance
- Verify trade size meets Bybit minimums
- Check symbol is valid (e.g., BTCUSDT not BTC)

## What's Different from Complex Bot?

**Removed:**
- ❌ Demo/testnet mode switching
- ❌ Multi-timeframe analysis
- ❌ Technical indicators (RSI, MACD, EMA)
- ❌ Trailing stop loss
- ❌ Strategy RAG system
- ❌ Balance caching
- ❌ Risk management limits
- ❌ Flask web server
- ❌ Telegram command panel
- ❌ 20+ configuration files

**Kept:**
- ✅ Bybit real trading
- ✅ Gemini AI signals
- ✅ Telegram notifications
- ✅ Market scanning
- ✅ Auto-trading

## Next Steps

1. Test with small amounts first ($20)
2. Monitor for 24 hours
3. Adjust `WATCHLIST` and `TRADE_AMOUNT_USDT` as needed
4. Add more pairs if working well

**This is a minimal, working bot. No complexity, just trading.** 🚀
