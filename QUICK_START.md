# 🚀 QUICK START & DEPLOYMENT GUIDE

## 🏃 Run Locally (Easy)

### **Option 1: Python Script (Fastest)**
```bash
# 1. Create virtual environment
python -m venv env

# 2. Activate it
# Windows:
env\Scripts\activate
# Mac/Linux:
source env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup .env file
cp .env.example .env
# Edit .env and add your API keys

# 5. Run bot
python main.py
```

### **Option 2: One-Line Setup (Copy-Paste)**

**Windows (PowerShell):**
```powershell
python -m venv env; .\env\Scripts\activate; pip install -r requirements.txt; Copy-Item .env.example .env; python main.py
```

**Mac/Linux:**
```bash
python -m venv env && source env/bin/activate && pip install -r requirements.txt && cp .env.example .env && python main.py
```

### **Option 3: Docker (If you use Docker)**
```bash
docker build -t crypto-trader .
docker run -e BYBIT_API_KEY=xxx -e BYBIT_API_SECRET=xxx crypto-trader
```

---

## 📋 Setup Checklist

- [ ] Clone/download code to local folder
- [ ] Create `env/` virtual environment
- [ ] Activate virtual environment
- [ ] Run `pip install -r requirements.txt`
- [ ] Copy `.env.example` to `.env`
- [ ] Add your API keys to `.env`
  - [ ] BYBIT_API_KEY (demo or real)
  - [ ] BYBIT_API_SECRET
  - [ ] GEMINI_API_KEY
  - [ ] TELEGRAM_BOT_TOKEN
  - [ ] TELEGRAM_CHAT_ID
- [ ] Run `python main.py`

---

## 🌍 Deploy on Render.com (Free Tier)

### **Step 1: Prepare GitHub Repo**

1. Create GitHub account (free)
2. Create new repository:
   - Name: `crypto-trader`
   - Public or Private
3. Clone to your computer:
   ```bash
   git clone https://github.com/YOUR_USERNAME/crypto-trader.git
   cd crypto-trader
   ```

4. Add your code:
   ```bash
   # Copy all your .py files here
   # The .env file is ALREADY in .gitignore so it won't be pushed
   ```

5. Push to GitHub:
   ```bash
   git add .
   git commit -m "Initial commit: crypto trading bot"
   git push -u origin main
   ```

### **Step 2: Connect to Render**

1. Go to [render.com](https://render.com)
2. Sign up (free with GitHub account)
3. Click "New +" → "Web Service"
4. Select your GitHub repo: `crypto-trader`
5. Configure:
   - **Name:** `crypto-trader`
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Region:** Closest to you (or us-east-1)
   - **Plan:** Free Tier

### **Step 3: Add Environment Variables**

After creating service, go to **Settings** → **Environment Variables**

Add each variable from `.env.example`:

| Key | Value | Required |
|-----|-------|----------|
| `BYBIT_API_KEY` | Your API key | ✅ Yes |
| `BYBIT_API_SECRET` | Your API secret | ✅ Yes |
| `BYBIT_TESTNET` | `False` | ✅ Yes |
| `GEMINI_API_KEY` | Your Gemini key | ✅ Yes |
| `TELEGRAM_BOT_TOKEN` | Your bot token | ✅ Yes |
| `TELEGRAM_CHAT_ID` | Your chat ID | ✅ Yes |
| `PORT` | `8080` | ✅ Yes |

**⚠️ IMPORTANT:** .env file is in .gitignore so variables MUST be added in Render dashboard!

### **Step 4: Configure Webhook (For Telegram)**

After Render deploys:

1. Get your Render URL from dashboard
   - It looks like: `https://crypto-trader-xxxx.onrender.com`

2. Register Telegram webhook (run once):
   ```bash
   curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://crypto-trader-xxxx.onrender.com/telegram/webhook"
   ```

3. Verify it works:
   ```bash
   /start → Should get response in Telegram
   ```

### **Step 5: Monitor on Render**

- **Logs:** View in Render dashboard → Logs
- **Metrics:** CPU, Memory, Network usage
- **Restart:** Click "Restart" if needed
- **Rebuild:** Push new code to GitHub (auto-redeploys)

---

## 📱 Get Your Telegram Credentials

### **Get Bot Token**
1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Follow prompts (name, username)
5. Copy the token: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`

### **Get Chat ID**
1. Start your bot: `@YourBotName /start`
2. Send any message
3. Go to: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Find `"chat":{"id":123456789}` - that's your Chat ID

---

## 🔑 Get Your API Keys

### **Bybit Demo/Real Keys**
1. Go to [bybit.com](https://bybit.com)
2. Log in
3. Settings → API → Create API Key
4. For DEMO: Select "Testnet" → Copy key and secret
5. For REAL: Select "Main Account" → Copy key and secret

### **Google Gemini API Key**
1. Go to [ai.google.dev](https://ai.google.dev)
2. Click "Get API Key"
3. Create new API key
4. Copy it

---

## 📝 .env File Example

After copying `.env.example` to `.env`:

```
BYBIT_API_KEY=Your_API_Key_Here_123456
BYBIT_API_SECRET=Your_API_Secret_Here_abcdef
BYBIT_TESTNET=False

GEMINI_API_KEY=Your_Gemini_Key_Here
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=987654321

PORT=8080
```

**⚠️ NEVER commit .env to GitHub** - It's in .gitignore!

---

## ✅ Verify Setup Works

### **Local Test**
```bash
# Run once to verify everything works
python main.py

# Should see:
# [trading] Started scanning WATCHLIST
# [telegram] Message sent: "🤖 Bot started"
# [server] Flask running on 0.0.0.0:8080
```

### **Telegram Test**
- Send: `/start`
- Bot should respond: `🤖 Crypto Trading Bot Started!`
- Send: `/status`
- Bot should show current status

### **Render Test**
- Deploy code to Render
- Wait 5 minutes for build
- Send Telegram message: `/status`
- Bot should respond (from Render server)

---

## 🐛 Troubleshooting

### **Bot doesn't respond to Telegram**
```
1. Check TELEGRAM_BOT_TOKEN is correct
2. Check TELEGRAM_CHAT_ID is correct
3. Restart bot
4. Send /start
```

### **Bot doesn't trade**
```
1. Check BYBIT_API_KEY and BYBIT_API_SECRET
2. Check BYBIT_TESTNET=False for demo mode
3. Check if bot is PAUSED: /status
4. Check logs: /logs
```

### **Render service keeps crashing**
```
1. Check logs in Render dashboard
2. Verify all environment variables are set
3. Check Python version (should be 3.10+)
4. Restart service
```

### **.env file not found**
```
1. Make sure .env exists in project root
2. Run: cp .env.example .env
3. Fill in your API keys
4. Restart bot
```

### **ModuleNotFoundError when running**
```
1. Make sure venv is activated
   - Windows: .\env\Scripts\activate
   - Mac/Linux: source env/bin/activate
2. Run: pip install -r requirements.txt
3. Try again
```

---

## 📂 Project Structure

```
crypto-trader/
├── main.py                 # Main bot loop
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── .env.example          # Environment template (commit this)
├── .env                  # Your keys (DON'T commit - in .gitignore)
├── .gitignore            # Files to ignore (includes .env)
│
├── Trading Core:
├── trader.py             # Place trades
├── trailing.py           # Trailing stop losses
├── scanner.py            # Find trade signals
│
├── Analysis:
├── ai_analyst.py         # AI analysis
├── technical_indicators.py # RSI, MACD, etc
├── multi_timeframe.py    # Multi-timeframe analysis
├── strategy_rag.py       # Load strategy docs
│
├── Telegram Control:
├── telegram_bot.py       # Message delivery
├── telegram_commands.py  # Bot commands
├── telegram_control_panel.py # Config management
│
├── Infrastructure:
├── server.py             # Flask web server
├── render.yaml          # Render.com config
├── history.py           # Trade history
├── risk_management.py   # Risk limits
│
└── Documentation:
    ├── README.md        # Overview
    ├── TELEGRAM_*.md    # Telegram guides
    └── QUICK_START.md   # This file
```

---

## 🚀 Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] .env file NOT in git (check .gitignore)
- [ ] .env.example file IS in git
- [ ] Render service created
- [ ] All environment variables added to Render
- [ ] Bot responds to `/start` on Telegram
- [ ] Bot trades in DEMO mode first
- [ ] Tested for 1-2 weeks in DEMO
- [ ] Real API keys added (when ready)
- [ ] Mode switched to REAL via `/mode` command
- [ ] Monitoring logs in Render dashboard

---

## 💡 Pro Tips

1. **Keep .env safe** - Never share it, it's in .gitignore
2. **Start with DEMO** - Test for 2 weeks before REAL
3. **Monitor logs** - Check `/logs` daily
4. **Scale gradually** - Start with $0.1 trades
5. **Backup config** - Download trading_config.json periodically
6. **Update strategies** - Use `/strategies` to manage RAG docs

---

## 🎓 Next Steps

1. **Local Setup:** Follow "Run Locally" above
2. **Test Bot:** Send Telegram commands
3. **Test Trading:** Let it run in DEMO for 1 week
4. **Deploy:** Follow "Deploy on Render" above
5. **Go Live:** Switch to REAL mode when confident

**Everything is ready!** Start with local testing first. 🎉