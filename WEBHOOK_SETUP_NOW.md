# 🚨 URGENT: Setup Telegram Webhook

Your `/start` command isn't working because the webhook isn't configured yet!

## 🔧 Quick Fix (Choose One Method)

### Method 1: Using Browser (EASIEST) ⭐

1. **Get your info:**
   - Bot Token: Check your `.env` file for `TELEGRAM_BOT_TOKEN`
   - Render URL: Your app URL (e.g., `https://your-app.onrender.com`)

2. **Open this URL in your browser:**
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=<YOUR_RENDER_URL>/telegram/webhook
   ```

   **Example:**
   ```
   https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/setWebhook?url=https://my-trading-bot.onrender.com/telegram/webhook
   ```

3. **You should see:**
   ```json
   {
     "ok": true,
     "result": true,
     "description": "Webhook was set"
   }
   ```

4. **Test in Telegram:**
   - Type `/start` in your bot chat
   - Should see menu with buttons!

---

### Method 2: Using cURL (Command Line)

**Windows (PowerShell):**
```powershell
$BOT_TOKEN = "your_bot_token_here"
$RENDER_URL = "https://your-app.onrender.com"
$WEBHOOK_URL = "$RENDER_URL/telegram/webhook"

Invoke-WebRequest -Uri "https://api.telegram.org/bot$BOT_TOKEN/setWebhook" -Method Post -Body (@{url=$WEBHOOK_URL} | ConvertTo-Json) -ContentType "application/json"
```

**Linux/Mac/Termux:**
```bash
BOT_TOKEN="your_bot_token_here"
RENDER_URL="https://your-app.onrender.com"
WEBHOOK_URL="$RENDER_URL/telegram/webhook"

curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"$WEBHOOK_URL\"}"
```

---

### Method 3: Using Python Script

```bash
python setup_webhook.py setup
```

Or if that doesn't work:

```python
# Run this in Python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RENDER_URL = "https://your-app.onrender.com"  # Change this!
WEBHOOK_URL = f"{RENDER_URL}/telegram/webhook"

response = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
    json={"url": WEBHOOK_URL}
)

print(response.json())
```

---

## 🔍 Check If Webhook Is Set

**Browser:**
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

**cURL:**
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

**Should show:**
```json
{
  "ok": true,
  "result": {
    "url": "https://your-app.onrender.com/telegram/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

---

## 📋 What You Need

1. **TELEGRAM_BOT_TOKEN** - From BotFather
   - Format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
   - Find in your `.env` file

2. **RENDER_EXTERNAL_URL** - Your Render app URL
   - Format: `https://your-app-name.onrender.com`
   - Find in Render dashboard

3. **Webhook Endpoint** - Automatically created
   - Format: `https://your-app-name.onrender.com/telegram/webhook`
   - This is where Telegram sends messages

---

## 🚨 Common Issues

### Issue 1: "Webhook setup failed"

**Cause:** Wrong bot token or URL

**Fix:**
1. Check `TELEGRAM_BOT_TOKEN` in `.env`
2. Verify Render URL is correct
3. Make sure bot is deployed and running

### Issue 2: "Bad Request: bad webhook"

**Cause:** Invalid webhook URL

**Fix:**
1. URL must start with `https://` (not `http://`)
2. URL must be accessible from internet
3. Check Render app is deployed

### Issue 3: Commands still not working

**Cause:** Webhook not receiving messages

**Fix:**
1. Check Render logs for incoming requests
2. Verify webhook URL is correct
3. Try deleting and re-setting webhook:
   ```
   https://api.telegram.org/bot<TOKEN>/deleteWebhook
   ```
   Then set it again

### Issue 4: "Connection refused"

**Cause:** Render app not running

**Fix:**
1. Check Render dashboard - is app deployed?
2. Check logs for errors
3. Verify environment variables are set

---

## ✅ Success Checklist

After setup, verify:

- [ ] Webhook URL is set (check with getWebhookInfo)
- [ ] Render app is deployed and running
- [ ] Environment variables are set in Render
- [ ] `/start` command responds in Telegram
- [ ] Menu with buttons appears
- [ ] Other commands work (`/status`, `/balance`)

---

## 🎯 Step-by-Step Example

Let's say:
- Bot Token: `123456:ABC-DEF1234ghIkl`
- Render URL: `https://crypto-bot-xyz.onrender.com`

**1. Set webhook (browser):**
```
https://api.telegram.org/bot123456:ABC-DEF1234ghIkl/setWebhook?url=https://crypto-bot-xyz.onrender.com/telegram/webhook
```

**2. Check webhook:**
```
https://api.telegram.org/bot123456:ABC-DEF1234ghIkl/getWebhookInfo
```

**3. Test in Telegram:**
```
/start
```

**4. Should see:**
```
🚀 TRADING BOT CONTROLLER

✅ Bot started and scanning for signals!

Available commands:
• /balance - View account balance
• /accounts - Compare demo/real
...

[💰 Balance] [📊 Status]
[📚 Strategies] [📈 Stats]
[▶️ Resume] [⏸️ Pause]
```

---

## 🆘 Still Not Working?

### Debug Steps:

1. **Check Render logs:**
   - Go to Render dashboard
   - Click on your service
   - Go to "Logs" tab
   - Look for errors

2. **Test webhook manually:**
   ```bash
   curl -X POST https://your-app.onrender.com/telegram/webhook \
     -H "Content-Type: application/json" \
     -d '{"message":{"chat":{"id":"YOUR_CHAT_ID"},"text":"/start"}}'
   ```

3. **Verify environment variables:**
   - Render dashboard → Environment
   - Check all variables are set
   - Especially `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`

4. **Check Flask server:**
   - Logs should show: `[server] ✅ Web server started on port 8080`
   - Should show: `[telegram] Telegram commands registered`

5. **Test bot token:**
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getMe
   ```
   Should return bot info

---

## 💡 Pro Tip

Add this to your `.env` file:
```env
RENDER_EXTERNAL_URL=https://your-app-name.onrender.com
```

Then run:
```bash
python setup_webhook.py setup
```

This automatically sets up the webhook for you!

---

## 🚀 After Webhook Is Set

You can use all commands:

```
/start          - Show menu and start bot
/status         - Check bot status
/balance        - View balance
/accounts       - Compare demo/real
/strategies     - Manage strategies
/stats          - View statistics
/resume         - Resume trading
/pause          - Pause trading
/help           - Show all commands
```

---

## 📞 Need Help?

1. Check Render logs for errors
2. Verify webhook is set with `getWebhookInfo`
3. Test bot token with `getMe`
4. Make sure app is deployed and running
5. Check all environment variables are set

**The most common issue is forgetting to set the webhook!** Do it now and your bot will work! 🚀
