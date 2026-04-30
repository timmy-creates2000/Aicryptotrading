# Termux Deployment Guide - Run Trading Bot on Android

## 📱 What is Termux?

Termux is a Linux terminal emulator for Android that lets you run your trading bot directly on your phone - **completely free** with no cloud hosting needed!

## ✅ Advantages

- ✅ **100% Free** - No hosting costs
- ✅ **Persistent Storage** - Files never get deleted
- ✅ **Always Connected** - Your phone stays online
- ✅ **Full Control** - Complete access to bot
- ✅ **Low Power** - Minimal battery usage
- ✅ **No External APIs Restrictions** - Direct connection to Bybit, Gemini, Telegram

## ⚠️ Requirements

### 1. Android Device
- Android 7.0 or higher
- At least 2GB RAM
- Stable internet connection (WiFi recommended)
- Battery optimization disabled for Termux

### 2. Apps Needed
- **Termux** - Main terminal app ([F-Droid](https://f-droid.org/packages/com.termux/) or [GitHub](https://github.com/termux/termux-app/releases))
- **Termux:Boot** (Optional) - Auto-start on device boot ([F-Droid](https://f-droid.org/packages/com.termux/termux-boot/))
- **Termux:API** (Optional) - Access Android features ([F-Droid](https://f-droid.org/packages/com.termux/termux-api/))

**⚠️ IMPORTANT:** Download from F-Droid or GitHub, NOT Google Play Store (outdated version)

## 🚀 Quick Installation

### Step 1: Install Termux

1. Download Termux from [F-Droid](https://f-droid.org/packages/com.termux/)
2. Install and open Termux
3. Grant storage permission:
   ```bash
   termux-setup-storage
   ```

### Step 2: Download Your Bot

Option A: Clone from Git
```bash
pkg install git -y
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

Option B: Copy files manually
```bash
# Copy your bot folder to:
# /storage/emulated/0/Download/trading-bot
# Then in Termux:
cp -r ~/storage/downloads/trading-bot ~/
cd ~/trading-bot
```

### Step 3: Run Installation Script

```bash
# Make script executable
chmod +x termux_install.sh

# Run installation
bash termux_install.sh
```

The script will automatically:
- ✅ Update Termux packages
- ✅ Install Python 3
- ✅ Install all dependencies
- ✅ Create .env file
- ✅ Setup helper scripts
- ✅ Configure auto-start

### Step 4: Configure API Keys

```bash
# Edit .env file
nano .env
```

Add your API keys:
```env
BYBIT_API_KEY_DEMO=your_demo_key
BYBIT_API_SECRET_DEMO=your_demo_secret
GEMINI_API_KEY=your_gemini_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

Save: `Ctrl+O`, then `Enter`
Exit: `Ctrl+X`

### Step 5: Start the Bot

```bash
# Start in foreground (see output)
./start_bot.sh

# OR start in background (keeps running)
./start_bot_background.sh
```

## 🎮 Bot Control Commands

### Start Bot
```bash
./start_bot.sh              # Foreground (see live output)
./start_bot_background.sh   # Background (keeps running when you close Termux)
```

### Stop Bot
```bash
./stop_bot.sh
```

### Check Status
```bash
./status_bot.sh
```

### View Logs
```bash
tail -f bot.log             # Live logs
tail -n 100 bot.log         # Last 100 lines
cat bot.log                 # Full log
```

### Restart Bot
```bash
./stop_bot.sh && ./start_bot_background.sh
```

## 🔄 Keep Bot Running When Termux is Closed

### Method 1: Wake Lock (Recommended)

The installation script already includes wake lock in the start scripts. This prevents Android from killing the process.

```bash
# Wake lock is automatically enabled when you run:
./start_bot_background.sh
```

### Method 2: Termux:Boot (Auto-start on device boot)

1. **Install Termux:Boot** from F-Droid

2. **Grant boot permission:**
   - Open Android Settings
   - Apps → Termux:Boot → Permissions
   - Enable "Autostart" or "Run in background"

3. **Edit boot script:**
   ```bash
   nano ~/.termux/boot/start_trading_bot.sh
   ```

4. **Update the path to your bot:**
   ```bash
   #!/data/data/com.termux/files/usr/bin/bash
   
   # Wait for network
   sleep 30
   
   # Change to your bot directory
   cd ~/trading-bot  # ← Update this path!
   
   # Start bot
   termux-wake-lock
   python main.py > bot.log 2>&1 &
   echo $! > bot.pid
   ```

5. **Make it executable:**
   ```bash
   chmod +x ~/.termux/boot/start_trading_bot.sh
   ```

6. **Reboot your device** - Bot will auto-start!

### Method 3: Termux:Widget (Quick Start Button)

1. **Install Termux:Widget** from F-Droid

2. **Create widget script:**
   ```bash
   mkdir -p ~/.shortcuts
   cp start_bot_background.sh ~/.shortcuts/
   ```

3. **Add widget to home screen:**
   - Long press home screen
   - Add widget → Termux:Widget
   - Tap widget to start bot

## 🔋 Battery Optimization

To prevent Android from killing Termux:

### Disable Battery Optimization

1. **Android Settings** → Battery → Battery Optimization
2. Find **Termux** and **Termux:Boot**
3. Select **"Don't optimize"** or **"Unrestricted"**

### Keep Screen On (Optional)

```bash
# In Termux, run:
termux-wake-lock
```

This keeps CPU awake but screen can turn off.

## 📊 Monitoring Your Bot

### Check if Bot is Running
```bash
./status_bot.sh
```

### View Live Logs
```bash
tail -f bot.log
```

### Check Process
```bash
ps aux | grep python
```

### Check Network Connection
```bash
ping -c 4 api.bybit.com
```

### Check Disk Space
```bash
df -h
```

## 🛠️ Troubleshooting

### Bot Stops When Termux Closes

**Solution:**
```bash
# Use background start with wake lock
./start_bot_background.sh

# Verify wake lock is active
termux-wake-status
```

### "Permission Denied" Errors

**Solution:**
```bash
# Make scripts executable
chmod +x *.sh

# Grant storage permission
termux-setup-storage
```

### Python Package Installation Fails

**Solution:**
```bash
# Update packages
pkg update && pkg upgrade

# Install build tools
pkg install clang python libffi openssl

# Reinstall packages
pip install --upgrade pip
pip install -r requirements.txt
```

### Bot Crashes or Stops

**Solution:**
```bash
# Check logs
tail -n 50 bot.log

# Check if process is running
ps aux | grep python

# Restart bot
./stop_bot.sh
./start_bot_background.sh
```

### High Battery Drain

**Solution:**
- Increase `SCAN_INTERVAL_SECONDS` in `config.py` (e.g., 300 = 5 minutes)
- Use WiFi instead of mobile data
- Close other apps
- Enable battery saver mode (but keep Termux unrestricted)

### Network Connection Issues

**Solution:**
```bash
# Test connection
ping -c 4 8.8.8.8

# Restart network
termux-wifi-connectioninfo

# Check if API is accessible
curl -I https://api.bybit.com
```

## 📱 Best Practices

### 1. Keep Phone Plugged In
- Trading bot runs 24/7
- Keep phone charging or use power bank
- Monitor battery health

### 2. Use Stable WiFi
- More reliable than mobile data
- Lower latency
- No data usage concerns

### 3. Regular Backups
```bash
# Backup your bot folder
tar -czf trading-bot-backup.tar.gz ~/trading-bot

# Copy to external storage
cp trading-bot-backup.tar.gz ~/storage/downloads/
```

### 4. Monitor Logs Daily
```bash
# Check for errors
tail -n 100 bot.log | grep -i error

# Check bot status
./status_bot.sh
```

### 5. Update Regularly
```bash
# Update Termux packages
pkg update && pkg upgrade

# Update Python packages
pip install --upgrade -r requirements.txt

# Update bot code (if using Git)
git pull origin main
```

## 🔐 Security Tips

1. **Never share your .env file**
2. **Use demo account first** (testnet)
3. **Set strong device lock** (PIN/password)
4. **Enable encryption** if available
5. **Don't root your device** (security risk)
6. **Keep Termux updated**

## 📊 Performance Tips

### Reduce Resource Usage

Edit `config.py`:
```python
SCAN_INTERVAL_SECONDS = 300  # Scan every 5 minutes instead of 1
CANDLE_LIMIT = 30            # Use fewer candles
HISTORY_LIMIT = 30           # Use less history
```

### Monitor Resource Usage
```bash
# Check CPU usage
top

# Check memory usage
free -h

# Check bot memory usage
ps aux | grep python
```

## 🎯 Comparison: Termux vs Cloud Hosting

| Feature | Termux (Android) | Render/Railway |
|---------|------------------|----------------|
| **Cost** | ✅ Free | ✅ Free (limited) |
| **Setup** | ⭐⭐ Medium | ⭐ Easy |
| **Persistent Storage** | ✅ Yes | ❌ No (free tier) |
| **Always On** | ✅ Yes | ⚠️ Needs ping |
| **Control** | ✅ Full | ⚠️ Limited |
| **Reliability** | ⚠️ Depends on phone | ✅ High |
| **Scalability** | ❌ Limited | ✅ Good |
| **Power Usage** | ⚠️ Battery drain | ✅ None |

## 🚀 Quick Reference

```bash
# Start bot in background
./start_bot_background.sh

# Check status
./status_bot.sh

# View logs
tail -f bot.log

# Stop bot
./stop_bot.sh

# Edit config
nano config.py

# Edit API keys
nano .env

# Update code
git pull

# Restart bot
./stop_bot.sh && ./start_bot_background.sh
```

## 📝 Summary

Termux is perfect for running your trading bot if you:
- ✅ Want zero hosting costs
- ✅ Have an Android device that can stay on
- ✅ Want full control over your bot
- ✅ Need persistent file storage
- ✅ Don't mind some battery usage

**Recommended for:** Personal use, testing, small-scale trading

**Not recommended for:** Production trading with large capital (use cloud hosting for better reliability)

---

## 🎉 You're Ready!

Your trading bot is now running on your Android device. Monitor it regularly and happy trading! 🚀

For issues or questions, check the logs first:
```bash
tail -f bot.log
```
