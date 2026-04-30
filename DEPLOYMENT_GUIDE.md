# Telegram Control Panel - Deployment Guide

## ✅ Implementation Complete

All core features have been implemented and integrated:

### 1. Balance Management
- View current account balance with `/balance`
- Compare demo and real accounts with `/accounts`
- Automatic caching (30-second TTL)
- Mode switching with balance display
- Professional formatting with emoji indicators (🟢🟡🔴)

### 2. Strategy File Upload
- Upload .txt, .md, or .pdf files directly via Telegram
- Automatic validation (file type, size < 5MB, content > 50 chars)
- Filename sanitization and duplicate handling
- Automatic RAG system reload after upload
- Preview and delete strategies with `/strategies`

### 3. Telegram Commands
- `/balance` - View current balance
- `/accounts` - Compare demo/real accounts
- `/strategies` - Manage strategy files
- `/reload_strategies` - Reload RAG system
- All existing commands still work

## 🚀 Deployment to Render.com

### Step 1: Environment Variables
In your Render dashboard, add these environment variables:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
BYBIT_API_KEY_DEMO=your_demo_key
BYBIT_API_SECRET_DEMO=your_demo_secret
BYBIT_API_KEY_REAL=your_real_key
BYBIT_API_SECRET_REAL=your_real_secret
```

**IMPORTANT:** Do NOT upload your `.env` file to Git or Render. Use the Render dashboard to set environment variables.

### Step 2: Push to Git
```bash
git add .
git commit -m "Add Telegram control panel features"
git push origin main
```

### Step 3: Deploy on Render
- Render will automatically detect the push and deploy
- Check logs for any errors
- Test the bot with `/start` command

## 📱 How to Use

### Upload Strategy Files
1. Open Telegram and find your bot
2. Send a .txt, .md, or .pdf file as a document
3. Bot will validate, save, and reload RAG system
4. Use `/strategies` to view all uploaded files

### Check Balances
1. Use `/balance` to see current mode balance
2. Use `/accounts` to compare demo and real
3. Click "Switch Mode" buttons to change between demo/real
4. Balance cache refreshes every 30 seconds

### Manage Strategies
1. Use `/strategies` to list all files
2. Click 👁️ button to preview content
3. Click 🗑️ button to delete (with confirmation)
4. Use `/reload_strategies` to manually reload RAG

## 🔒 Security Notes

- API keys are stored in environment variables (secure)
- File uploads are validated for type, size, and content
- Filenames are sanitized to prevent directory traversal
- Demo mode uses Bybit testnet (no real money)
- Real mode requires explicit confirmation

## 📊 File Types Supported

### Strategy Files (.txt, .md, .pdf)
- **Purpose:** AI reads these before making trading decisions
- **Max Size:** 5MB per file
- **Min Content:** 50 characters
- **Examples:**
  - ICT trading rules
  - Supply/demand zone strategies
  - Risk management guidelines
  - Entry/exit criteria

## ✅ Testing Checklist

Before going live, test these features:

- [ ] `/balance` shows correct balance
- [ ] `/accounts` compares demo and real
- [ ] Upload a .txt strategy file
- [ ] Preview strategy with 👁️ button
- [ ] Delete strategy with 🗑️ button
- [ ] Switch between demo and real modes
- [ ] Check that RAG system loads strategies
- [ ] Verify cache refreshes after 30 seconds

## 🐛 Troubleshooting

### "Balance features not available"
- Check that `balance_manager.py` exists
- Verify API keys are set in environment variables

### "Strategy uploader not available"
- Check that `strategy_uploader.py` exists
- Verify `strategies/` folder exists

### "Could not fetch balance"
- Verify API keys are correct
- Check Bybit API status
- Ensure mode (DEMO/REAL) matches your API keys

### File upload fails
- Check file size (must be < 5MB)
- Check file type (.txt, .md, .pdf only)
- Check content length (must be > 50 chars)

## 📝 Next Steps

Your bot is ready to deploy! The implementation includes:
- ✅ Balance management with caching
- ✅ Strategy file upload with validation
- ✅ Professional Telegram interface with buttons
- ✅ RAG system integration
- ✅ Mode switching (demo/real)
- ✅ Error handling and logging

Deploy to Render and start trading! 🚀
