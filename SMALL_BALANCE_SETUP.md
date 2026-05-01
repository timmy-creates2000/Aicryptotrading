# 💰 Trading with $3.20 Balance

## Your Situation

- **Balance:** $3.20 USDT
- **Trade Size:** $2.00 per trade
- **Leverage:** 5x
- **Position Size:** $10.00 per trade
- **Coins:** Cheap altcoins (DOGE, XRP, ADA, TRX, SHIB)

## Why These Settings?

### 1. Small Trade Size ($2.00)
- Leaves you with $1.20 buffer
- Can make 1 trade at a time
- Won't drain your account on first trade

### 2. Cheap Coins Only
```
DOGEUSDT  - Dogecoin (~$0.08)
XRPUSDT   - Ripple (~$2.50)
ADAUSDT   - Cardano (~$0.90)
TRXUSDT   - Tron (~$0.25)
SHIBUSDT  - Shiba Inu (~$0.000025)
```

These meet Bybit's minimum order sizes even with $2 trades.

### 3. 5x Leverage
- $2 × 5 = $10 position
- Manageable risk
- Meets minimum trade requirements

## Expected Behavior

### First Trade
```
🔍 Scanning 5 pairs...
  DOGEUSDT: BUY (78%)
  XRPUSDT: WAIT (65%)
  ADAUSDT: WAIT (55%)
  TRXUSDT: SELL (72%)
  SHIBUSDT: WAIT (60%)

🏆 Best: DOGEUSDT BUY (78%)

📊 Executing BUY on DOGEUSDT
   Price: $0.08
   Quantity: 125 DOGE
   Value: $2 × 5x = $10

✅ Order placed
```

### After Trade
- Balance: $1.20 remaining
- Position: $10 worth of DOGE
- Bot waits 5 minutes
- Then scans again

## Profit/Loss Examples

### Win Scenario (+2%)
- Entry: $10 position
- Exit: $10.20
- Profit: $0.20
- New Balance: $3.40

### Loss Scenario (-2%)
- Entry: $10 position
- Exit: $9.80
- Loss: $0.20
- New Balance: $3.00

## Growing Your Account

### Strategy
1. Start with $3.20
2. Make small profits ($0.20-$0.50 per trade)
3. After reaching $5.00, increase trade size to $3.00
4. After reaching $10.00, increase to $5.00
5. Keep growing gradually

### Realistic Timeline
- Week 1: $3.20 → $5.00 (if 50% win rate)
- Week 2: $5.00 → $8.00
- Month 1: $8.00 → $15.00
- Month 2: $15.00 → $30.00

**This assumes:**
- 2-3 trades per day
- 50% win rate
- 2% profit per winning trade

## Risks with Small Balance

### ⚠️ One Bad Trade Can Hurt
- A -20% loss = $2.00 gone
- You'd be down to $1.20
- Might not be enough to trade

### ⚠️ Fees Add Up
- Bybit charges 0.055% per trade
- On $10 position = $0.0055 fee
- Need to profit >0.11% to break even

### ⚠️ Limited Opportunities
- Can only trade 1 position at a time
- Miss other signals while in trade
- Need to be patient

## Safety Tips

1. **Don't increase leverage** - Stay at 5x max
2. **Don't chase losses** - If you lose, wait for next signal
3. **Don't trade all at once** - Keep $1.20 buffer
4. **Watch for fees** - Make sure profit > fees
5. **Be patient** - Growing $3 takes time

## Adjusting Trade Size

Edit `simple_bot.py` line 29:

```python
TRADE_AMOUNT_USDT = 2.0  # Start here with $3.20

# When you reach $5:
TRADE_AMOUNT_USDT = 3.0

# When you reach $10:
TRADE_AMOUNT_USDT = 5.0

# When you reach $25:
TRADE_AMOUNT_USDT = 10.0
```

## What If Balance Drops Below $2?

The bot will show:
```
⚠️ Warning: Balance $1.50 is low
```

But it will keep trying to trade. If balance is too low, Bybit will reject orders with "Insufficient balance" error.

## Recommendation

**Add more funds if possible:**
- $10 minimum is more comfortable
- $20 gives you room to breathe
- $50+ lets you trade multiple pairs

But if $3.20 is all you have, the bot is configured to work with it. Just be patient and let it grow slowly.

## Deploy Now

1. The bot is already configured for $3.20
2. Follow `DEPLOY_SIMPLE_BOT.md`
3. Watch it trade with $2 per trade
4. Monitor your balance growth

**Good luck! 🚀**
