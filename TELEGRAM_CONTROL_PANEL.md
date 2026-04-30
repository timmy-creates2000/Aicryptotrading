# TELEGRAM CONTROL PANEL — Easy Configuration

You can now control everything from Telegram! No terminal needed.

---

## **Available Commands** 🎮

### **Trading Control**
```
/start       → Main menu
/status      → Current bot status
/stats       → Win/loss statistics
/resume      → Start trading
/pause       → Pause trading
/stop        → Stop bot
/help        → All commands
```

### **Configuration** ⚙️
```
/config      → Show all settings
/mode        → Switch DEMO ↔ REAL
/amount      → Set trade amount ($0.1 to $5)
/leverage    → Set leverage (1x to 10x)
/keys        → Manage API keys
```

### **Monitoring**
```
/logs        → View message delivery logs
```

---

## **How to Use Each Command** 

### **1. /config** (View All Settings)
Shows your current configuration:
```
⚙️ TRADING CONFIG

Mode: DEMO
Trade Amount: $0.5
Leverage: 5x
Stop Loss: 1%
Take Profit: 2%
Max Losses: 3 in a row
Daily Loss Limit: 5%
```

Click buttons to change any setting!

### **2. /mode** (Switch Demo/Real)
```
Step 1: Type /mode
Step 2: Click "Switch to REAL" or "Switch to DEMO"
Step 3: Bot updates API keys automatically
Step 4: Ready to trade!
```

**Important:** Before switching to REAL, add real API keys with `/keys`

### **3. /amount** (Set Trade Size)
Choose how much to trade per trade:
```
$0.1  → Conservative (best for testing)
$0.2  → 
$0.5  → Safe (good for most)
$1.0  → 
$2.0  →
$5.0  → Aggressive (risky)
```

**Your Balance** | **Recommended**
---|---
$3.50 | $0.5
$10 | $1.0
$50 | $5.0
$100 | $10.0

### **4. /leverage** (Risk Level)
```
1x   → 🟢 No leverage (lowest risk)
2x   → 🟢 Low risk
3x   → 🟡 Medium risk
5x   → 🟡 Medium-high risk (default)
10x  → 🔴 HIGH RISK (use carefully!)
```

**Example:**
- $0.5 × 5x leverage = $2.50 buying power
- If price goes up 10% = +$0.25 profit
- If price down 10% = -$0.25 loss

### **5. /keys** (Add API Keys)

**For DEMO Mode:**
```
Step 1: Click "Demo Keys"
Step 2: Get keys from Bybit → Settings → API → Demo Trading
Step 3: Send:
demo_key=abc123xyz
demo_secret=xyz789abc

Step 4: Done! Ready for demo trading
```

**For REAL Mode (⚠️ Careful!):**
```
Step 1: Click "Real Keys"
Step 2: Get keys from Bybit → Settings → API → Real Trading
Step 3: Send:
real_key=abc123xyz
real_secret=xyz789abc

Step 4: Switch mode to REAL when ready
```

---

## **Example Workflow** 📋

### **Day 1: Testing**
```
1. Send /config → See defaults
2. Send /amount → Choose $0.5
3. Send /mode → See current mode
4. Send /keys → Add demo keys
5. Send /resume → Start trading
6. Send /stats → Check results
```

### **Day 2: Adjust Settings**
```
1. Send /leverage → Change to 3x (safer)
2. Send /amount → Change to $0.3 (smaller)
3. Send /pause → Pause to test
4. Send /resume → Resume
```

### **Ready for Real Trading**
```
1. Send /keys → Add real API keys
2. Send /mode → Switch to REAL
3. Send /amount → Set to $0.5 (small)
4. Send /resume → Start with small size
5. Send /stats → Monitor closely
```

---

## **Safety Features** 🛡️

✅ **Buttons instead of typing** - Click, don't type wrong commands  
✅ **Confirmation** - No accidental switches  
✅ **Auto limits** - Max 10x leverage  
✅ **State saved** - Config persists after restart  
✅ **Easy undo** - Change settings anytime  

---

## **Files It Uses** 📁

- `telegram_control_panel.py` - Manages config
- `trading_config.json` - Persisted settings
- `config.py` - Python config (auto-updated)
- `.env` - API keys (auto-updated)

---

## **Pro Tips** 💡

1. **Start conservative** 
   - $0.1-0.5 trades
   - 3-5x leverage
   - Test for 1-2 weeks

2. **Monitor daily**
   - Send /stats every morning
   - Check /logs for issues
   - Adjust if needed

3. **Scale gradually**
   - Week 1: $0.5/trade
   - Week 2: $1.0/trade (if profitable)
   - Week 3: $2.0/trade (if still profitable)

4. **Keep backups**
   - Save your API keys somewhere safe
   - Screenshot important configs
   - Note your strategy settings

---

## **Quick Reference** ⚡

| Want to... | Command | Then |
|-----------|---------|------|
| See config | `/config` | Click buttons to change |
| Switch to REAL | `/mode` | Click "Switch to REAL" |
| Change trade amount | `/amount` | Click desired amount |
| Lower risk | `/leverage` | Click "1x" or "2x" |
| Add API keys | `/keys` | Follow prompts |
| Start trading | `/resume` | Bot begins scanning |
| Pause trading | `/pause` | No new trades |
| Check stats | `/stats` | See win/loss data |

---

**Everything can now be controlled from Telegram!** 📱✅