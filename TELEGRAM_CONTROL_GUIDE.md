# 📱 Telegram Control Guide

Complete guide to controlling your trading bot via Telegram.

## 🚀 Quick Start

1. **Find your bot** on Telegram (search for your bot username)
2. **Start conversation** by typing `/start`
3. **Use commands** or click buttons to control the bot

## 📋 Available Commands

### 🎮 Main Control

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Show main menu with buttons | `/start` |
| `/status` | View bot status & current trade | `/status` |
| `/stats` | View win/loss statistics | `/stats` |
| `/help` | Show all available commands | `/help` |

### ⏯️ Bot Control

| Command | Description | When to Use |
|---------|-------------|-------------|
| `/resume` | Resume trading (start scanning) | After pausing or starting bot |
| `/pause` | Pause trading (no new trades) | When you want to stop opening new positions |
| `/stop` | Stop the bot completely | Emergency stop |

**Note:** Pausing keeps existing trades running with trailing stops, but won't open new ones.

### 💰 Balance & Accounts

| Command | Description | What You See |
|---------|-------------|--------------|
| `/balance` | View current account balance | Total equity, available balance, P&L |
| `/accounts` | Compare demo vs real accounts | Side-by-side comparison with switch button |

**Features:**
- ✅ Auto-refresh every 30 seconds
- ✅ Color-coded status (🟢 Good, 🟡 Warning, 🔴 Low)
- ✅ One-click mode switching
- ✅ Real-time P&L tracking

### 📚 Strategy Management

| Command | Description | What It Does |
|---------|-------------|--------------|
| `/strategies` | List all strategy files | Shows uploaded strategies with preview/delete buttons |
| `/reload_strategies` | Reload RAG system | Reloads all strategy documents into AI |

**Upload Strategy Files:**
1. Create a `.txt`, `.md`, or `.pdf` file with your strategy
2. Send it as a document/file to the bot
3. Bot automatically validates, saves, and loads it into RAG

**Example Strategy File:**
```
supply_demand_zones.txt

STRATEGY: Supply & Demand Zones

ENTRY RULES:
- Find 3+ touch zones on higher timeframe
- Wait for price to return to zone
- Enter on break with volume confirmation

STOP LOSS:
- 2% below demand zone
- 2% above supply zone

TAKE PROFIT:
- 2:1 risk/reward minimum
- Trail after 1:1 is reached

FILTERS:
- Only trade during London/NY session
- Avoid news events
- RSI must confirm direction
```

### ⚙️ Configuration

| Command | Description | Options |
|---------|-------------|---------|
| `/config` | View current settings | Shows all trading parameters |
| `/mode` | Switch DEMO/REAL mode | Toggle between testnet and live |
| `/amount` | Set trade amount | $0.1, $0.2, $0.5, $1, $2, $5 |
| `/leverage` | Set leverage | 1x, 2x, 3x, 5x, 10x |
| `/keys` | Manage API keys | Add demo or real API keys |

### 📊 Monitoring

| Command | Description | Info Shown |
|---------|-------------|------------|
| `/logs` | View recent Telegram logs | Last 10 messages sent by bot |
| `/force_close` | Force close current trade | Emergency exit (in development) |

## 🎯 Common Use Cases

### Starting the Bot

```
1. /start          → Shows main menu
2. /balance        → Check your balance
3. /resume         → Start trading
4. Bot scans automatically every 60 seconds
```

### Checking Status

```
/status            → Quick status check
/stats             → Detailed statistics
/balance           → Current balance
```

### Uploading a Strategy

```
1. Create strategy.txt file
2. Send as document to bot
3. Bot validates and saves
4. /strategies     → Verify upload
5. /reload_strategies → Reload RAG
```

### Switching Modes

```
1. /accounts       → Compare demo/real
2. Click "Switch to REAL" button
3. Confirm switch
4. Bot uses new API keys
```

### Pausing Trading

```
/pause             → Stops opening new trades
                     (existing trades continue)
/resume            → Resume trading
```

## 🔔 Automatic Notifications

The bot sends you notifications for:

### 🔍 Scan Events
- **Scan Start** - When bot starts scanning pairs
- **Best Signal** - When a high-confidence signal is found
- **No Signal** - When no good opportunities exist

### ⚡ Trade Events
- **Trade Opened** - Full details: entry, SL, TP, R:R ratio
- **Trail Update** - When stop loss is moved (profit locked)
- **Trade Closed** - Final P&L, ROI, duration, stats

### 🤖 Bot Events
- **Bot Started** - When bot begins running
- **Bot Stopped** - When bot is stopped
- **Errors** - Critical errors or issues

### 📊 Example Notifications

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

## 🎮 Interactive Buttons

Most commands show interactive buttons for quick actions:

### Main Menu (`/start`)
```
[💰 Balance] [📊 Status]
[📚 Strategies] [📈 Stats]
[▶️ Resume] [⏸️ Pause]
```

### Balance View (`/balance`)
```
[🔄 Refresh]
[💰 Compare Accounts]
```

### Accounts View (`/accounts`)
```
[🔄 Switch to REAL]
[🔄 Refresh]
```

### Strategies (`/strategies`)
```
[👁️ strategy1.txt] [🗑️]
[👁️ strategy2.txt] [🗑️]
[🔄 Reload All]
```

### Config (`/config`)
```
[🔄 Switch Mode] [💵 Set Amount]
[📈 Set Leverage]
```

## 🔐 Security Tips

1. **Never share your bot token** - Keep `TELEGRAM_BOT_TOKEN` secret
2. **Use demo mode first** - Test with testnet before going live
3. **Set chat ID correctly** - Only you should receive notifications
4. **Don't share API keys** - Never send keys in Telegram messages
5. **Monitor regularly** - Check `/status` and `/balance` daily

## 🛠️ Troubleshooting

### Bot Not Responding

**Check:**
1. Is `TELEGRAM_BOT_TOKEN` set correctly in `.env`?
2. Is `TELEGRAM_CHAT_ID` set correctly?
3. Is the bot running? (Check Render/Termux logs)
4. Try `/start` command

**Fix:**
```bash
# Check environment variables
cat .env | grep TELEGRAM

# Restart bot (Termux)
./stop_bot.sh
./start_bot_background.sh

# Check logs
tail -f bot.log
```

### Balance Not Showing

**Check:**
1. Are API keys set correctly?
2. Is the mode (DEMO/REAL) correct?
3. Do API keys have "Read" permission?

**Fix:**
```
/config          → Check current mode
/keys            → Add/update API keys
/balance         → Try again
```

### Strategy Upload Fails

**Common Issues:**
- File too large (max 5MB)
- Wrong file type (use .txt, .md, .pdf)
- File content too short (min 50 characters)

**Fix:**
1. Check file size and type
2. Ensure file has meaningful content
3. Try uploading again
4. Use `/strategies` to verify

### Commands Not Working

**Try:**
1. `/start` - Restart bot conversation
2. Check spelling - Commands are case-sensitive
3. Use buttons instead of typing
4. Check `/help` for correct command format

## 📱 Mobile Tips

### Quick Access
- **Pin the chat** - Keep bot conversation at top
- **Use buttons** - Faster than typing commands
- **Enable notifications** - Don't miss trade alerts
- **Use shortcuts** - Save common commands

### Battery Saving
- **Mute non-critical alerts** - Keep only trade notifications
- **Use WiFi** - More reliable than mobile data
- **Check periodically** - Don't need to monitor 24/7

## 🎯 Best Practices

### Daily Routine
```
Morning:
1. /status         → Check overnight activity
2. /balance        → Verify account balance
3. /stats          → Review performance

During Day:
- Monitor notifications
- Check /status occasionally
- Adjust settings if needed

Evening:
1. /stats          → Review day's trades
2. /balance        → Check P&L
3. /pause          → Pause if needed
```

### Strategy Management
```
Weekly:
1. Review strategy performance
2. Upload new strategies if needed
3. Delete underperforming strategies
4. /reload_strategies → Refresh RAG

Monthly:
1. Analyze win rate
2. Adjust risk parameters
3. Update strategy documents
4. Review /logs for issues
```

## 📊 Command Reference Card

**Quick Commands:**
```
/start    - Main menu
/status   - Bot status
/balance  - Account balance
/resume   - Start trading
/pause    - Stop trading
/help     - All commands
```

**Management:**
```
/strategies - Manage strategies
/config     - Settings
/accounts   - Compare accounts
/stats      - Statistics
```

**Emergency:**
```
/pause        - Stop new trades
/stop         - Stop bot
/force_close  - Close current trade
```

## 🚀 Pro Tips

1. **Use buttons** - Faster and less error-prone than typing
2. **Upload strategies** - Let AI learn your trading style
3. **Monitor balance** - Check `/balance` before and after trades
4. **Compare accounts** - Use `/accounts` to track demo vs real
5. **Review stats** - Use `/stats` to improve win rate
6. **Check logs** - Use `/logs` to debug issues
7. **Pause during news** - Use `/pause` during high-impact events
8. **Test in demo** - Always test new strategies in demo mode first

## 📝 Summary

Your bot is fully controllable via Telegram with:
- ✅ Real-time status updates
- ✅ Balance monitoring
- ✅ Strategy management
- ✅ Configuration changes
- ✅ Trade notifications
- ✅ Interactive buttons
- ✅ Emergency controls

Start with `/start` and explore the buttons!

---

**Need Help?**
- Type `/help` in Telegram
- Check bot logs: `tail -f bot.log`
- Review this guide
- Test commands in demo mode first
