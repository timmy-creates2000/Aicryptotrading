# Telegram Bot Commands Setup Guide

## **What You Can Now Do** 🎮

Control your trading bot directly from Telegram with interactive commands:

### **Available Commands**

```
/start       → Show main menu with buttons
/status      → Check bot running status
/stats       → View win/loss statistics  
/resume      → Start trading (resume from pause)
/pause       → Pause trading (don't open new trades)
/stop        → Stop the bot completely
/help        → Show all commands
/logs        → View recent Telegram message logs
/force_close → Force close current trade (coming soon)
```

---

## **Setup Instructions**

### **Step 1: Get Telegram Bot Token**
1. Open Telegram, search for `@BotFather`
2. Send `/newbot`
3. Follow prompts (name your bot)
4. Copy the token you receive (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### **Step 2: Get Your Chat ID**
1. Search for `@userinfobot` on Telegram
2. Send `/start`
3. Note the number shown (your chat ID)

### **Step 3: Update `.env` File**
```bash
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=987654321
TELEGRAM_LOG_FILE=telegram_messages.log
```

### **Step 4: Setup Webhook (if using Render/hosting)**

If hosting on Render.com:

1. Find your public URL: `https://your-app.onrender.com`
2. Run this Python script once:

```python
from telegram_commands import setup_telegram_webhook
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = "https://your-app.onrender.com/telegram/webhook"

setup_telegram_webhook(BOT_TOKEN, WEBHOOK_URL)
print("Webhook registered!")
```

**For Local Testing (Polling Mode):**
Skip webhook setup, bot will poll Telegram for messages.

---

## **Command Examples**

### **Check Status**
```
User: /status
Bot: 🟢 BOT STATUS
     Running: ✅ YES
     Current Trade: BTCUSDT
     Last Scan: 14:32:15
     Total Trades: 45
     Wins: 28 ✅
     Losses: 17 ❌
     Win Rate: 62.2%
```

### **View Statistics**
```
User: /stats
Bot: 📈 TRADE STATISTICS
     Total Trades: 45
     Wins: 28 (62.2%)
     Losses: 17 (37.8%)
     Win/Loss Ratio: 1:0.61
```

### **Pause Trading**
```
User: /pause
Bot: ⏸️ TRADING PAUSED
     No new trades will be opened.
     Existing trades will continue with trailing stops.
```

### **Resume Trading**
```
User: /resume
Bot: ▶️ TRADING RESUMED
     Bot is now actively scanning for signals.
     New trades will be placed automatically.
```

---

## **Interactive Buttons**

When you send `/start`, you get quick-action buttons:

```
┌─────────────────────┐
│ 📊 Status  📈 Stats │
├─────────────────────┤
│ ▶️ Resume ⏸️ Pause  │
└─────────────────────┘
```

Click any button for instant updates (no need to type!)

---

## **Monitoring Features**

### **Real-Time Status**
- See if bot is running (🟢 green or 🔴 red)
- Current trade symbol
- Last scan time
- Win/loss count

### **Statistics Dashboard**
- Total trades placed
- Win rate percentage
- Win/loss ratio
- Streak tracking (coming soon)

### **Message Logs**
```
User: /logs
Bot: Shows last 10 telegram messages with:
     - Message type (SCAN_START, TRADE_OPENED, etc)
     - Status (SUCCESS, FAILED, RATE_LIMITED)
     - Exact timestamp
```

---

## **Pause vs Stop**

| Feature | Pause | Stop |
|---------|-------|------|
| **Stops new trades** | ✅ Yes | ✅ Yes |
| **Keeps open trades** | ✅ Yes | ✅ Yes |
| **Can resume** | ✅ Yes | ❌ No |
| **Need to restart** | ❌ No | ✅ Yes |

**Use `/pause` to**:
- Take a break without restarting
- Test manually
- Market conditions are bad

**Use `/stop` to**:
- Completely shut down bot
- Need to restart with fresh state

---

## **Advanced Features (Coming Soon)**

- `/force_close` - Manually close current position
- `/config` - View/edit bot settings
- `/alerts` - Customize notification types
- `/pnl` - View detailed P&L breakdown
- `/recent` - Show last 5 trades

---

## **Troubleshooting**

### **Bot doesn't respond to commands**
1. Check `.env` has correct `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
2. If using webhook, verify URL is accessible
3. Try polling mode (local testing)
4. Check logs: `cat telegram_messages.log`

### **Commands work but take 10+ seconds**
- Bot might be running a trade
- Trailing stop blocks other operations
- This is normal, consider /pause during long operations

### **"Telegram not configured" error**
- Missing `TELEGRAM_BOT_TOKEN` in `.env`
- Missing `TELEGRAM_CHAT_ID` in `.env`
- Restart bot after updating `.env`

---

## **How It Works Behind the Scenes**

1. **Telegram sends message** to your bot
2. **Webhook receives it** at `/telegram/webhook` endpoint
3. **Command handler processes** the request
4. **Bot state updates** (`bot_status` dict)
5. **Main trading loop** checks state and adjusts behavior
6. **Response sent back** to Telegram with results

**Key Integration Points:**
- `telegram_commands.py` - Command handlers
- `server.py` - Flask webhook endpoint
- `main.py` - Trading loop checks `bot_status`
- `telegram_bot.py` - Send notifications back

---

## **Example Workflow**

```
9:00 AM   → Bot starts, sends 🚀 TRADING BOT STARTED
9:15 AM   → Signal found, sends 🏆 BEST SIGNAL FOUND
9:16 AM   → Trade opened, sends ⚡ TRADE OPENED
9:17 AM   → You send /status via Telegram
9:17 AM   → Bot responds with current position
9:20 AM   → You send /pause (bad market conditions)
9:20 AM   → Bot stops scanning, keeps current trade
9:30 AM   → Market improves, you send /resume
9:30 AM   → Bot resumes scanning
2:00 PM   → Trade closes, sends ✅ TRADE CLOSED
```

---

## **Security Notes**

⚠️ **Important:**
- Keep `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` secret
- Don't share `.env` file
- Telegram is direct control, be careful with commands
- All commands are logged to `telegram_messages.log`
- Consider setting webhook with authentication for production

---

**Ready to try it?** Send `/help` to your bot to get started!
