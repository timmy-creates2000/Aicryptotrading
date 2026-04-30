# PythonAnywhere Deployment Guide

## ⚠️ Important Limitations

PythonAnywhere has some restrictions that affect this trading bot:

### ❌ What WON'T Work on Free Tier:
1. **No external API access** - Free accounts can't connect to Bybit API or Gemini AI
2. **Whitelist required** - Only paid accounts can access external APIs
3. **No always-on tasks** - Free tier has limited always-on processes

### ✅ What You Need:
- **Paid Account Required** ($5/month minimum) for:
  - External API access (Bybit, Gemini)
  - Always-on web apps
  - Scheduled tasks

## 🚀 Deployment Steps (Paid Account)

### Step 1: Upload Your Code

1. **Login to PythonAnywhere**
   - Go to https://www.pythonanywhere.com
   - Login to your account

2. **Open Bash Console**
   - Click "Consoles" tab
   - Start a new Bash console

3. **Clone Your Repository**
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

   Or upload files manually:
   - Use "Files" tab
   - Upload your project folder

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
mkvirtualenv --python=/usr/bin/python3.10 trading-bot

# Activate it
workon trading-bot

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Set Environment Variables

Create a `.env` file in your project directory:

```bash
nano .env
```

Add your credentials:
```
BYBIT_API_KEY_DEMO=your_demo_key
BYBIT_API_SECRET_DEMO=your_demo_secret
BYBIT_API_KEY_REAL=your_real_key
BYBIT_API_SECRET_REAL=your_real_secret
GEMINI_API_KEY=your_gemini_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
PORT=8080
```

Save with `Ctrl+O`, exit with `Ctrl+X`

### Step 4: Configure Web App

1. **Go to Web Tab**
   - Click "Add a new web app"
   - Choose "Manual configuration"
   - Select Python 3.10

2. **Configure WSGI File**
   - Click on WSGI configuration file link
   - Replace content with:

```python
import sys
import os

# Add your project directory to path
project_home = '/home/yourusername/your-repo'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

# Import Flask app
from server import app as application
```

3. **Set Virtual Environment**
   - In Web tab, find "Virtualenv" section
   - Enter: `/home/yourusername/.virtualenvs/trading-bot`

4. **Set Working Directory**
   - In Web tab, set working directory to: `/home/yourusername/your-repo`

### Step 5: Start Trading Bot as Always-On Task

Since the bot needs to run continuously, you need to set it up as an always-on task:

1. **Go to Tasks Tab**
   - Click "Create a new scheduled task" or "Always-on task" (paid only)

2. **For Always-On Task:**
   ```bash
   cd /home/yourusername/your-repo && /home/yourusername/.virtualenvs/trading-bot/bin/python main.py
   ```

3. **Alternative: Use Scheduled Task (runs hourly)**
   ```bash
   cd /home/yourusername/your-repo && /home/yourusername/.virtualenvs/trading-bot/bin/python -c "from trader import scan_all_pairs; scan_all_pairs()"
   ```

### Step 6: Reload Web App

- Go back to Web tab
- Click green "Reload" button
- Your Flask server should now be running

## 🔧 PythonAnywhere vs Render Comparison

| Feature | PythonAnywhere (Paid) | Render (Free) |
|---------|----------------------|---------------|
| **Price** | $5/month minimum | Free tier available |
| **External APIs** | ✅ Allowed (paid) | ✅ Allowed |
| **Always-On** | ✅ Yes | ✅ Yes (with ping) |
| **File Storage** | ✅ Persistent | ❌ Ephemeral (free) |
| **Memory** | 512MB-3GB | 512MB (free) |
| **Setup** | More manual | Auto-deploy from Git |
| **Best For** | Python-specific apps | Any language, CI/CD |

## 💡 Recommendation

### Use Render if:
- You want free tier with external APIs
- You prefer Git-based auto-deployment
- You're okay with ephemeral storage
- You can set up UptimeRobot for pinging

### Use PythonAnywhere if:
- You need persistent file storage
- You prefer Python-focused environment
- You want simpler console access
- You're willing to pay $5/month

## 🎯 Best Option for Your Bot

**Render is better for your use case** because:
1. Free tier supports external APIs (Bybit, Gemini)
2. Auto-deploys from Git (easier updates)
3. Your bot already has `render.yaml` configured
4. Flask server keeps it alive (no sleep)

**PythonAnywhere advantages:**
1. Persistent storage for strategy files
2. Better for manual file management
3. Direct console access

## 🚀 Quick Start Commands

### For PythonAnywhere:
```bash
# In Bash console
git clone your-repo
cd your-repo
mkvirtualenv --python=/usr/bin/python3.10 trading-bot
pip install -r requirements.txt
python main.py
```

### For Render:
```bash
# Just push to Git
git add .
git commit -m "Ready for deployment"
git push origin main
# Render auto-deploys!
```

## 📝 Notes

- **API Whitelist**: PythonAnywhere requires whitelisting external APIs (Bybit, Gemini) on paid plans
- **Always-On Tasks**: Limited to paid accounts only
- **File Uploads**: Strategy files uploaded via Telegram will persist on PythonAnywhere but not on Render free tier
- **Monitoring**: Both platforms need monitoring (UptimeRobot for Render, built-in for PythonAnywhere)

Choose based on your priority: **ease of deployment (Render)** vs **persistent storage (PythonAnywhere)**.
