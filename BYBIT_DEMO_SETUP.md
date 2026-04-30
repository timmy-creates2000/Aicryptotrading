# Bybit Demo (Testnet) Setup Guide

## What is Bybit Demo Trading?

Bybit Demo Trading (Testnet) lets you:
- Trade with **fake money** but **real market prices**
- Test your bot safely before using real funds
- Practice strategies without risk
- Get free testnet USDT to trade with

## Step 1: Access Bybit Testnet

1. Go to **https://testnet.bybit.com**
2. Click "Sign Up" or "Log In"
3. Use your regular Bybit account credentials (same as mainnet)

## Step 2: Get Free Testnet USDT

1. After logging in to testnet, look for "Faucet" or "Get Testnet Funds"
2. Click to receive free testnet USDT (usually 10,000 USDT)
3. This is fake money for testing only

## Step 3: Create Demo API Keys

1. On testnet.bybit.com, go to **Account → API Management**
2. Click "Create New Key"
3. Set permissions:
   - ✅ Read-Write (for trading)
   - ✅ Contract Trading
   - ✅ Spot Trading
4. **IMPORTANT**: Save your API Key and Secret immediately (you can't see the secret again)
5. Copy both values

## Step 4: Create Real API Keys (Optional)

1. Go to **https://www.bybit.com** (mainnet)
2. Log in to your real account
3. Go to **Account → API Management**
4. Click "Create New Key"
5. Set the same permissions as demo
6. Save your API Key and Secret

## Step 5: Update Your .env File

Open your `.env` file and add:

```bash
# DEMO Keys (from testnet.bybit.com)
BYBIT_API_KEY_DEMO=your_testnet_api_key_here
BYBIT_API_SECRET_DEMO=your_testnet_api_secret_here

# REAL Keys (from www.bybit.com)
BYBIT_API_KEY_REAL=your_mainnet_api_key_here
BYBIT_API_SECRET_REAL=your_mainnet_api_secret_here

# Telegram (same as before)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Gemini AI (same as before)
GEMINI_API_KEY=your_gemini_api_key
```

## Step 6: Test Your Setup

1. Start your bot
2. Open Telegram and send `/accounts`
3. You should see:
   - **DEMO**: Your testnet balance (10,000 USDT)
   - **REAL**: Your real balance

4. Use `/mode` to switch between DEMO and REAL

## Important Notes

### Demo Mode (Testnet)
- URL: testnet.bybit.com
- Fake money, real prices
- Perfect for testing
- No risk

### Real Mode (Mainnet)
- URL: www.bybit.com
- Real money, real trades
- Use after testing in demo
- Real risk

## Security Tips

1. **Never share your API secrets** with anyone
2. **Don't commit .env to Git** (it's in .gitignore)
3. **Use IP restrictions** on your API keys (optional but recommended)
4. **Start with demo mode** to test everything first
5. **Use small amounts** when switching to real mode

## Troubleshooting

### "Could not fetch balance" Error
- Check that your API keys are correct
- Verify you're using the right keys for the mode (demo keys for DEMO, real keys for REAL)
- Make sure API keys hav