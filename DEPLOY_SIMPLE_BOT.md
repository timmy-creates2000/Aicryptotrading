# 🚀 Deploy Simple Bot to Render (5 Minutes)

## What You Have Now

✅ **simple_bot.py** - One file, 250 lines, does everything  
✅ **No complexity** - No demo mode, no multi-timeframe, no 20 config files  
✅ **Just works** - Scans → AI decides → Trades → Notifies  

---

## Step 1: Update Render Configuration

In your Render dashboard:

1. Go to your service settings
2. Change **Build Command** to:
   ```
   pip install -r requirements.simple.txt
   ```

3. Change **Start Command** to:
   ```
   python simple_bot.py
   ```

---

## Step 2: Set Environment Variables

In Render → Environment, set these 5 variables:

```
BYBIT_API_KEY=uxrWndHSeRFvRf4Erc
BYBIT_API_SECRET=yQyOLSOn1AH2p5d256tnNNxcUpl6kWCET6sQ
GEMINI_API_KEY=your_gemini_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

**Get Gemini API Key:**
- Go to: https://aistudio.google.com/app/apikey
- Click "Create API Key"
- Copy and paste into Render

---

## Step 3: Deploy

Click **"Manual Deploy" → "Deploy latest commit"**

---

## Step 4: Watch Logs

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
  SOLUSDT: WAIT (60%)
  BNBUSDT: SELL (78%)
  XRPUSDT: WAIT (55%)

🏆 Best: ETHUSDT BUY (82%)

📊 Executing BUY on ETHUSDT
   Price: $3,245.50
   Quantity: 0.031
   Value: $20 × 5x = $100

✅ Order placed: 1234567890
```

---

## Step 5: Get Telegram Notifications

You'll receive:
```
🤖 Bot started!
Balance: $XXX.XX
Watching: BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT

✅ TRADE EXECUTED

Symbol: ETHUSDT
Side: BUY
Price: $3,245.50
Quantity: 0.031
Confidence: 82%
Reason: Strong upward momentum with high volume

Order ID: 1234567890
```

---

## What Happens Next

1. **Every 60 seconds:** Bot scans 5 pairs
2. **AI analyzes:** Gemini decides BUY/SELL/WAIT
3. **If confident (75%+):** Places trade automatically
4. **After trade:** Waits 5 minutes before next scan
5. **Telegram:** Notifies you of every action

---

## Customize (Optional)

Edit `simple_bot.py` lines 28-32:

```python
WATCHLIST = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]  # Add more pairs
TRADE_AMOUNT_USDT = 20.0  # Increase trade size
LEVERAGE = 5              # Change leverage
SCAN_INTERVAL = 60        # Scan more/less frequently
MIN_CONFIDENCE = 75       # Require higher confidence
```

Then push to GitHub and Render will auto-deploy.

---

## Troubleshooting

### Bot doesn't start
- Check Render logs for Python errors
- Verify all 5 environment variables are set
- Make sure GEMINI_API_KEY is valid

### "Error getting balance"
- Verify Bybit API permissions: Read + Wallet + Trade
- Check you're using Mainnet keys (not testnet)
- Confirm USDT is in Unified Trading Account

### No trades executing
- Check AI confidence is reaching 75%+
- Verify balance is at least $20 USDT
- Look for "Order failed" messages in logs

### Telegram not working
- Verify TELEGRAM_BOT_TOKEN is correct
- Check TELEGRAM_CHAT_ID matches your chat
- Test by sending `/start` to your bot

---

## That's It!

**No Telegram commands needed. No /start button. Just deploys and trades.**

The bot is now:
- ✅ Scanning markets every 60 seconds
- ✅ Using AI to make decisions
- ✅ Trading with real money
- ✅ Sending you notifications

Monitor the Render logs and your Telegram for activity.

🚀 **Simple. Clean. Working.**
