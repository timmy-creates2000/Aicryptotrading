# 🚀 Start Your Trading Bot NOW

## The bot is deployed but waiting for your command!

Your bot is running on Render but in **standby mode**. It's waiting for you to send the `/start` command via Telegram.

---

## ✅ Quick Start (3 Steps)

### Step 1: Open Telegram
Open your Telegram app and find your bot

### Step 2: Send `/start` Command
Type and send:
```
/start
```

### Step 3: Bot Will Start Trading
You'll see:
```
✅ Bot started! Scanning will begin in a moment...
```

---

## 📱 Telegram Commands

Once started, you can control the bot with these commands:

| Command | What It Does |
|---------|--------------|
| `/start` | Start the trading bot |
| `/status` | Check if bot is running and see last scan time |
| `/balance` | View your Bybit USDT balance |
| `/pause` | Pause trading (stops new trades) |
| `/resume` | Resume trading after pause |
| `/stats` | See win/loss statistics |
| `/help` | Show all available commands |

---

## 🔍 How to Know It's Working

After sending `/start`, check `/status`:

**Good Status (Working):**
```
📊 BOT STATUS

Running: ✅ YES
Current Trade: None
Last Scan: 14:23:45
Total Trades: 0
Wins: 0 ✅
Losses: 0 ❌
```

**Bad Status (Not Working):**
```
📊 BOT STATUS

Running: ❌ NO
Last Scan: Never
```

If you see "Running: ❌ NO", send `/start` again.

---

## ⚙️ Alternative: Auto-Start on Deploy

If you want the bot to start automatically when Render deploys (no need for `/start` command):

1. Go to Render Dashboard → Your Service → Environment
2. Add this variable:
   ```
   AUTO_START_TRADING=true
   ```
3. Save and redeploy

**Note:** With auto-start, you lose manual control. The bot will trade immediately on every deployment.

---

## 🐛 Troubleshooting

### Bot doesn't respond to `/start`
1. Check Render logs for errors
2. Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set correctly
3. Make sure webhook is configured (should auto-setup on deploy)

### Bot starts but "Last Scan: Never"
1. Check Render logs for Python errors
2. Verify `GEMINI_API_KEY` is set
3. Verify `BYBIT_API_KEY` and `BYBIT_API_SECRET` are set

### Balance shows $0.00
1. Check Bybit API permissions (Read + Wallet + Trade)
2. Verify you're using **mainnet** API keys (not testnet)
3. Make sure you have USDT in your Bybit Unified Trading Account

---

## 📊 Expected Behavior

1. **First scan:** Takes 60-90 seconds (analyzing 14 pairs across 2 timeframes)
2. **Scan frequency:** Every 60 seconds
3. **Signal requirements:** Both 15min and 1hour timeframes must agree
4. **Minimum confidence:** 75% to place trade
5. **Trade size:** $20 USDT × 5 leverage = $100 position

---

## 🎯 Next Steps

1. Send `/start` to your Telegram bot
2. Wait 60-90 seconds for first scan
3. Check `/status` to confirm "Last Scan" updates
4. Monitor for first trade signal
5. Use `/balance` to verify funds

**The bot is ready - just send `/start`!** 🚀
