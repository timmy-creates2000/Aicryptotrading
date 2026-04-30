# 🤖 Crypto Trading Bot — AI-Powered with Telegram Control

AI-powered trading bot using Gemini Flash + Bybit API + Multi-timeframe analysis.
Scans multiple pairs, picks best signal, trails profit automatically, fully controllable via Telegram.

## 🚀 Quick Start

**👉 See [QUICK_START.md](QUICK_START.md) for:**
- Local setup (copy-paste commands)
- Render.com deployment
- Telegram configuration
- Environment variables
- Troubleshooting

**TL;DR for Windows:**
```bash
.\start.bat
```

**TL;DR for Mac/Linux:**
```bash
./start.sh
```

---

## 📁 File Structure

```
trading-bot/
├── main.py          ← START HERE — press Enter to run
├── config.py        ← Edit your watchlist and settings
├── scanner.py       ← Scans all pairs for signals
├── ai_analyst.py    ← Gemini AI analysis
├── history.py       ← Fetches candles + trade history from Bybit
├── trader.py        ← Places and closes trades
├── trailing.py      ← Trailing stop loss manager
├── telegram_bot.py  ← Telegram alerts
└── .env             ← Your API keys (never share this!)
```

---

## ⚙️ Setup Steps

### 1. Install Python libraries
```bash
pip install pybit google-generativeai python-telegram-bot requests python-dotenv
```

### 2. Get Bybit Testnet API Keys
- Go to https://testnet.bybit.com
- Sign up → Avatar → API Management → Create Key
- Permissions: Read + Trade
- Copy API Key and Secret into `.env`

### 3. Get Gemini API Key
- Go to https://aistudio.google.com
- Click "Get API Key" → Create key
- Copy into `.env`

### 4. Setup Telegram Bot (Optional but recommended)
- Open Telegram → search @BotFather
- Type /newbot → follow instructions
- Copy the token into `.env`
- Then message @userinfobot to get your Chat ID
- Copy Chat ID into `.env`

### 5. Fill in your .env file
```
BYBIT_API_KEY=xxxxxxxxxxxx
BYBIT_API_SECRET=xxxxxxxxxxxx
BYBIT_TESTNET=True
GEMINI_API_KEY=xxxxxxxxxxxx
TELEGRAM_BOT_TOKEN=xxxxxxxxxxxx
TELEGRAM_CHAT_ID=xxxxxxxxxxxx
```

### 6. Run the bot
```bash
python main.py
```

Press ENTER to start. Press CTRL+C to stop.

---

## ⚙️ Customize Settings (config.py)

| Setting | Default | What it does |
|---|---|---|
| SCAN_INTERVAL_SECONDS | 60 | How often to scan all pairs |
| MIN_CONFIDENCE_TO_TRADE | 75 | Minimum AI confidence to trade |
| TRAILING_STEP_PERCENT | 0.3 | How tight the trailing SL follows |
| INITIAL_STOP_LOSS_PERCENT | 1.0 | Initial SL distance from entry |
| TRADE_QUANTITY_USDT | 5.0 | Size of each trade in USDT |
| LEVERAGE | 5 | Leverage multiplier |

---

## ⚠️ Important

- Always test on TESTNET first (BYBIT_TESTNET=True)
- Only go live after 2-4 weeks of profitable testnet results
- Never risk more than you can afford to lose
