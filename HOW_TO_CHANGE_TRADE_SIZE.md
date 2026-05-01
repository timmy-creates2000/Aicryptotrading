# 📝 How to Change Trade Size

## Quick Answer

Edit `simple_bot.py` **line 29** and change this number:

```python
TRADE_AMOUNT_USDT = 0.1  # ← Change this number
```

---

## Step-by-Step Guide

### Method 1: Edit on GitHub (Easiest)

1. Go to: https://github.com/timmy-creates2000/Aicryptotrading
2. Click on `simple_bot.py`
3. Click the pencil icon (✏️ Edit)
4. Find line 29: `TRADE_AMOUNT_USDT = 0.1`
5. Change `0.1` to your desired amount
6. Scroll down and click "Commit changes"
7. Render will auto-deploy in 2-3 minutes

### Method 2: Edit Locally

1. Open `simple_bot.py` in your code editor
2. Find line 29
3. Change the number
4. Save the file
5. Push to GitHub:
   ```bash
   git add simple_bot.py
   git commit -m "Change trade size to X"
   git push origin main
   ```

---

## Trade Size Options

### For $3.20 Balance

```python
# Ultra safe (32 trades possible)
TRADE_AMOUNT_USDT = 0.1

# Safe (16 trades possible)
TRADE_AMOUNT_USDT = 0.2

# Moderate (6 trades possible)
TRADE_AMOUNT_USDT = 0.5

# Aggressive (4 trades possible)
TRADE_AMOUNT_USDT = 0.7

# Very aggressive (3 trades possible)
TRADE_AMOUNT_USDT = 1.0

# Risky (1 trade possible)
TRADE_AMOUNT_USDT = 2.0
```

### Recommended by Balance

| Your Balance | Safe Trade Size | Aggressive Trade Size |
|--------------|----------------|----------------------|
| $3.20 | 0.1 - 0.2 | 0.5 - 0.7 |
| $5.00 | 0.2 - 0.3 | 0.7 - 1.0 |
| $10.00 | 0.5 - 1.0 | 1.5 - 2.0 |
| $20.00 | 1.0 - 2.0 | 3.0 - 5.0 |
| $50.00 | 2.0 - 5.0 | 7.0 - 10.0 |
| $100.00 | 5.0 - 10.0 | 15.0 - 20.0 |

---

## What Happens When You Change It

### Example: Change from 0.1 to 0.5

**Before (0.1):**
```
Trade size: $0.10
Leverage: 10x
Position: $1.00
Profit on 2% move: $0.02
```

**After (0.5):**
```
Trade size: $0.50
Leverage: 10x
Position: $5.00
Profit on 2% move: $0.10
```

**5x bigger profits, but also 5x bigger losses!**

---

## Daily Earnings by Trade Size

### With $3.20 Balance

| Trade Size | Position Size | Profit per 2% Win | Daily Potential* |
|------------|---------------|-------------------|------------------|
| $0.10 | $1.00 | $0.02 | $0.02 - $0.05 |
| $0.20 | $2.00 | $0.04 | $0.04 - $0.10 |
| $0.50 | $5.00 | $0.10 | $0.10 - $0.25 |
| $0.70 | $7.00 | $0.14 | $0.14 - $0.35 |
| $1.00 | $10.00 | $0.20 | $0.20 - $0.50 |

*Assumes 2-4 winning trades per day

---

## Risk Warning

### The Danger of Large Trade Sizes

**With $3.20 balance:**

```python
TRADE_AMOUNT_USDT = 1.0  # $1 per trade
```

**One bad trade:**
- Position: $10.00 (with 10x leverage)
- Loss of 10%: -$1.00
- Your balance: $3.20 → $2.20
- **You lost 31% of your account in one trade!**

**Three bad trades in a row:**
- Loss 1: $3.20 → $2.20
- Loss 2: $2.20 → $1.20
- Loss 3: $1.20 → $0.20
- **You're basically wiped out!**

---

## My Recommendation

### Start Conservative, Increase Gradually

**Week 1-2: Learn the Bot**
```python
TRADE_AMOUNT_USDT = 0.1  # Ultra safe
```
- Get comfortable with how it works
- See how AI makes decisions
- Learn from wins and losses

**Week 3-4: Increase Slightly**
```python
TRADE_AMOUNT_USDT = 0.2  # Still safe
```
- If you're profitable, double your size
- If you're losing, stay at 0.1

**Month 2: Scale Up**
```python
TRADE_AMOUNT_USDT = 0.5  # Moderate risk
```
- Only if your balance grew to $5+
- Only if you have 60%+ win rate

**Month 3+: Aggressive Growth**
```python
TRADE_AMOUNT_USDT = 1.0  # Higher risk
```
- Only if balance is $10+
- Only if consistently profitable

---

## How to Monitor Performance

After changing trade size, watch these metrics:

### In Render Logs
```
✅ Order placed: 1234567890
Balance before: $3.20
Balance after: $3.22 (+$0.02)
```

### In Telegram
```
✅ TRADE EXECUTED
Profit: $0.10
New balance: $3.30
```

### Track Your Win Rate
- Count wins vs losses
- If win rate drops below 50%, reduce trade size
- If win rate is 60%+, consider increasing

---

## Quick Change Examples

### Want to be more aggressive now?

```python
# Change line 29 from:
TRADE_AMOUNT_USDT = 0.1

# To:
TRADE_AMOUNT_USDT = 0.5
```

Push to GitHub → Render auto-deploys → Bot uses new size

### Want to be safer?

```python
# Change line 29 from:
TRADE_AMOUNT_USDT = 0.5

# To:
TRADE_AMOUNT_USDT = 0.1
```

---

## Pro Tips

1. **Never risk more than 30% per trade**
   - With $3.20, max trade size = $1.00

2. **Increase gradually**
   - Don't jump from 0.1 to 1.0
   - Go: 0.1 → 0.2 → 0.5 → 0.7 → 1.0

3. **Scale with balance**
   - As balance grows, increase trade size
   - Keep trade size at 10-30% of balance

4. **Test first**
   - Run new trade size for 1 week
   - If profitable, keep it
   - If losing, reduce back

5. **Don't get greedy**
   - Slow and steady wins
   - Protect your capital first
   - Profits come second

---

## Summary

**To change trade size:**
1. Edit `simple_bot.py` line 29
2. Change `TRADE_AMOUNT_USDT = 0.1` to your desired amount
3. Save and push to GitHub
4. Render auto-deploys

**Recommended progression:**
- Start: 0.1 (learn)
- Week 2: 0.2 (if profitable)
- Month 2: 0.5 (if balance grew)
- Month 3: 1.0 (if consistently winning)

**Remember:** Bigger trades = bigger profits BUT also bigger losses! 🚀
