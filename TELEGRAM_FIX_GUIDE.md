# 🔧 Telegram Control Fix Guide

## Issues Fixed

1. ✅ Bot no longer auto-starts on deploy
2. ✅ `/start` command now works properly
3. ✅ Added webhook setup script
4. ✅ Better P&L tracking in notifications

## 🚀 Setup Steps

### Step 1: Update Environment Variables

Add to your `.env` file (or Render dashboard):

```env
# Control bot auto-start behavior
AUTO_START_TRADING=false  # false = wait for /start command, true = auto-start

# Your Render URL (for webhook)
RENDER_EXTERNAL_URL=https://your-app-name.onrender.com
```

### Step 2: Setup Telegram Webhook

After deploying to Render, run this **once**:

```bash
python setup_webhook.py setup
```

Or manually:
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://your-app.onrender.com/telegram/webhook"
```

**Check webhook status:**
```bash
python setup_webhook.py check
```

### Step 3: Test Telegram Commands

1. Open Telegram and find your bot
2. Type `/start` - Bot should respond with menu
3. Click "▶️ Resume" or type `/resume` to start trading
4. Type `/status` to check if bot is running

## 📊 How It Works Now

### Bot Startup Behavior

**With `AUTO_START_TRADING=false` (Recommended):**
```
1. Bot deploys on Render
2. Flask server starts
3. Bot waits for /start command
4. You control when trading begins
```

**With `AUTO_START_TRADING=true`:**
```
1. Bot deploys on Render
2. Flask server starts
3. Bot immediately starts trading
4. No manual intervention needed
```

### Telegram Commands Flow

```
/start          → Shows menu + starts bot if not running
/resume         → Resumes trading (if paused)
/pause          → Pauses trading (no new trades)
/status         → Shows current status
/balance        → Shows account balance with P&L
/stats          → Shows win/loss statistics
```

## 💰 P&L Tracking

The bot now tracks and shows:

### In `/balance` command:
- Total Equity
- Available Balance
- Unrealized P&L (open positions)
- Realized P&L (closed trades)

### In Trade Notifications:

**Trade Opened:**
```
⚡ TRADE OPENED

Pair: BTCUSDT
Side: LONG
Entry: 45,230.50
SL: 44,778.00
TP: 46,135.50
Qty: 0.011
R:R: 1:2.00
AI Confidence: 87%
📊 Trailing stop ACTIVE
```

**Trade Closed:**
```
✅ WIN

Pair: BTCUSDT
Entry: 45,230.50 → Exit: 46,100.00
PnL: +9.57 USDT (ROI: 1.92%)
Locked Profit: 8.20 USDT
📈 Duration: 47 min
🔄 SL Updates: 3
Final Trend: BULLISH
```

### In `/stats` command:
```
📈 TRADE STATISTICS

Total Trades: 15
Wins: 10 (66.7%)
Losses: 5 (33.3%)
Win/Loss Ratio: 1:0.50

Total P&L: +45.23 USDT
Average Win: +6.80 USDT
Average Loss: -3.15 USDT
```

## 🔍 Troubleshooting

### `/start` Command Not Working

**Check:**
1. Is webhook setup correctly?
   ```bash
   python setup_webhook.py check
   ```

2. Is `RENDER_EXTERNAL_URL` set in environment variables?

3. Is bot deployed and running on Render?

**Fix:**
```bash
# Re-setup webhook
python setup_webhook.py setup

# Check Render logs
# Go to Render dashboard → Your service → Logs
```

### Bot Not Responding to Commands

**Check:**
1. Webhook URL is correct
2. `TELEGRAM_BOT_TOKEN` is set
3. `TELEGRAM_CHAT_ID` is your chat ID

**Test webhook:**
```bash
curl -X POST https://your-app.onrender.com/telegram/webhook \
  -H "Content-Type: application/json" \
  -d '{"message":{"chat":{"id":"YOUR_CHAT_ID"},"text":"/status"}}'
```

### Bot Auto-Starts Despite Setting

**Check:**
1. Is `AUTO_START_TRADING=false` in Render environment variables?
2. Did you redeploy after changing?

**Fix:**
1. Go to Render dashboard
2. Environment → Add `AUTO_START_TRADING=false`
3. Manual Deploy → Deploy latest commit

### Not Seeing P&L

**Check:**
1. Are you using `/balance` command?
2. Have you made any trades yet?
3. Is `balance_manager.py` working?

**Test:**
```
/balance        → Should show current balance
/stats          → Should show trade statistics
/status         → Should show wins/losses
```

## 📱 Recommended Workflow

### First Time Setup:
```
1. Deploy to Render
2. Add environment variables (including AUTO_START_TRADING=false)
3. Run: python setup_webhook.py setup
4. Open Telegram → /start
5. Check /balance
6. Click "▶️ Resume" to start trading
```

### Daily Use:
```
Morning:
1. /status      → Check overnight activity
2. /balance     → Check P&L
3. /stats       → Review performance

During Day:
- Receive automatic trade notifications
- Check /status occasionally

Evening:
1. /stats       → Review day's trades
2. /balance     → Check total P&L
3. /pause       → Pause if needed
```

### Emergency:
```
/pause          → Stop new trades immediately
/stop           → Stop bot completely
/force_close    → Close current trade (in development)
```

## 🎯 Testing Checklist

After deploying, test these:

- [ ] `/start` - Shows menu and starts bot
- [ ] `/status` - Shows bot is running
- [ ] `/balance` - Shows account balance
- [ ] `/stats` - Shows statistics (after trades)
- [ ] `/pause` - Pauses trading
- [ ] `/resume` - Resumes trading
- [ ] `/strategies` - Lists strategies
- [ ] `/accounts` - Compares demo/real
- [ ] Receive trade opened notification
- [ ] Receive trade closed notification with P&L
- [ ] Receive trailing stop updates

## 📝 Environment Variables Summary

**Required:**
```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
BYBIT_API_KEY=your_api_key
BYBIT_API_SECRET=your_api_secret
GEMINI_API_KEY=your_gemini_key
```

**Optional but Recommended:**
```env
AUTO_START_TRADING=false
RENDER_EXTERNAL_URL=https://your-app.onrender.com
TELEGRAM_LOG_FILE=telegram_messages.log
PORT=8080
```

## 🚀 Quick Commands Reference

```bash
# Setup webhook (run once after deploy)
python setup_webhook.py setup

# Check webhook status
python setup_webhook.py check

# Delete webhook (for local testing)
python setup_webhook.py delete

# Test bot locally
python main.py

# View logs (Termux)
tail -f bot.log

# View logs (Render)
# Go to dashboard → Logs tab
```

## ✅ Success Indicators

You'll know everything is working when:

1. ✅ `/start` command responds with menu
2. ✅ Bot shows "running: false" initially
3. ✅ `/resume` starts the bot
4. ✅ `/status` shows "Running: YES"
5. ✅ You receive scan notifications
6. ✅ Trade notifications show P&L
7. ✅ `/balance` shows current balance
8. ✅ `/stats` shows win/loss data

## 🎉 You're All Set!

Your bot now:
- ✅ Waits for your command to start
- ✅ Responds to Telegram commands
- ✅ Shows P&L in notifications
- ✅ Tracks wins/losses
- ✅ Provides full control via Telegram

Start with `/start` and happy trading! 🚀
