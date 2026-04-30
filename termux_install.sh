#!/data/data/com.termux/files/usr/bin/bash

# Termux Trading Bot Installation Script
# Run with: bash termux_install.sh

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          🤖 Trading Bot - Termux Installation                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if running in Termux
if [ ! -d "/data/data/com.termux" ]; then
    print_error "This script must be run in Termux!"
    exit 1
fi

print_info "Starting installation..."
echo ""

# Step 1: Update packages
print_info "Step 1/7: Updating Termux packages..."
pkg update -y && pkg upgrade -y
if [ $? -eq 0 ]; then
    print_success "Packages updated"
else
    print_error "Failed to update packages"
    exit 1
fi
echo ""

# Step 2: Install Python
print_info "Step 2/7: Installing Python..."
pkg install -y python python-pip
if [ $? -eq 0 ]; then
    print_success "Python installed"
    python --version
else
    print_error "Failed to install Python"
    exit 1
fi
echo ""

# Step 3: Install Git (optional, for cloning repo)
print_info "Step 3/7: Installing Git..."
pkg install -y git
if [ $? -eq 0 ]; then
    print_success "Git installed"
else
    print_error "Failed to install Git"
fi
echo ""

# Step 4: Install Termux:Boot (for auto-start)
print_info "Step 4/7: Setting up Termux:Boot..."
pkg install -y termux-services
if [ $? -eq 0 ]; then
    print_success "Termux services installed"
    print_info "Install 'Termux:Boot' app from F-Droid or Play Store for auto-start"
else
    print_error "Failed to install termux-services"
fi
echo ""

# Step 5: Install required system packages
print_info "Step 5/7: Installing system dependencies..."
pkg install -y clang openssl libffi rust
if [ $? -eq 0 ]; then
    print_success "System dependencies installed"
else
    print_error "Failed to install system dependencies"
fi
echo ""

# Step 6: Upgrade pip and install Python packages
print_info "Step 6/7: Installing Python dependencies..."
pip install --upgrade pip setuptools wheel

if [ -f "requirements.txt" ]; then
    print_info "Found requirements.txt, installing packages..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        print_success "Python packages installed"
    else
        print_error "Some packages failed to install"
        print_info "Trying to install packages individually..."
        
        # Install packages one by one
        pip install pybit==5.8.0
        pip install google-generativeai==0.8.3
        pip install requests==2.31.0
        pip install python-dotenv==1.0.0
        pip install flask==3.0.0
        pip install numpy
        pip install pandas
        pip install python-telegram-bot
    fi
else
    print_error "requirements.txt not found!"
    print_info "Installing packages manually..."
    pip install pybit==5.8.0 google-generativeai==0.8.3 requests==2.31.0 python-dotenv==1.0.0 flask==3.0.0 numpy pandas python-telegram-bot
fi
echo ""

# Step 7: Setup environment file
print_info "Step 7/7: Setting up environment variables..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Created .env file from .env.example"
        print_info "⚠️  IMPORTANT: Edit .env file with your API keys!"
        print_info "Run: nano .env"
    else
        print_error ".env.example not found"
        print_info "Creating basic .env template..."
        cat > .env << 'EOF'
# Bybit API Keys
BYBIT_API_KEY_DEMO=your_demo_api_key_here
BYBIT_API_SECRET_DEMO=your_demo_api_secret_here
BYBIT_API_KEY_REAL=your_real_api_key_here
BYBIT_API_SECRET_REAL=your_real_api_secret_here

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# Server
PORT=8080
EOF
        print_success "Created .env template"
        print_info "⚠️  IMPORTANT: Edit .env file with your API keys!"
        print_info "Run: nano .env"
    fi
else
    print_success ".env file already exists"
fi
echo ""

# Create strategies folder if it doesn't exist
if [ ! -d "strategies" ]; then
    mkdir -p strategies
    print_success "Created strategies folder"
fi

# Setup Termux:Boot script
print_info "Setting up auto-start script..."
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/start_trading_bot.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

# Wait for network
sleep 30

# Change to bot directory (UPDATE THIS PATH!)
cd ~/trading-bot

# Activate wake lock to prevent sleep
termux-wake-lock

# Start the bot
python main.py > bot.log 2>&1 &

# Save PID for later
echo $! > bot.pid
EOF

chmod +x ~/.termux/boot/start_trading_bot.sh
print_success "Auto-start script created at ~/.termux/boot/start_trading_bot.sh"
print_info "⚠️  Update the path in the script to match your bot location!"
echo ""

# Create helper scripts
print_info "Creating helper scripts..."

# Start script
cat > start_bot.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock
python main.py
EOF
chmod +x start_bot.sh
print_success "Created start_bot.sh"

# Background start script
cat > start_bot_background.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock
nohup python main.py > bot.log 2>&1 &
echo $! > bot.pid
echo "Bot started in background. PID: $(cat bot.pid)"
echo "View logs: tail -f bot.log"
echo "Stop bot: ./stop_bot.sh"
EOF
chmod +x start_bot_background.sh
print_success "Created start_bot_background.sh"

# Stop script
cat > stop_bot.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    kill $PID 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "Bot stopped (PID: $PID)"
        rm bot.pid
    else
        echo "Bot not running or already stopped"
        rm bot.pid
    fi
else
    echo "No PID file found. Bot may not be running."
    pkill -f "python main.py"
fi
termux-wake-unlock
EOF
chmod +x stop_bot.sh
print_success "Created stop_bot.sh"

# Status script
cat > status_bot.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Bot is running (PID: $PID)"
        echo ""
        echo "Recent logs:"
        tail -n 20 bot.log
    else
        echo "❌ Bot is not running (stale PID file)"
        rm bot.pid
    fi
else
    echo "❌ Bot is not running"
fi
EOF
chmod +x status_bot.sh
print_success "Created status_bot.sh"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  ✅ Installation Complete!                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
print_info "Next steps:"
echo ""
echo "1. Edit your .env file with API keys:"
echo "   nano .env"
echo ""
echo "2. Start the bot:"
echo "   ./start_bot.sh              (foreground)"
echo "   ./start_bot_background.sh   (background)"
echo ""
echo "3. Check bot status:"
echo "   ./status_bot.sh"
echo ""
echo "4. Stop the bot:"
echo "   ./stop_bot.sh"
echo ""
echo "5. View logs:"
echo "   tail -f bot.log"
echo ""
print_info "For auto-start on boot:"
echo "   - Install 'Termux:Boot' app from F-Droid"
echo "   - Edit ~/.termux/boot/start_trading_bot.sh"
echo "   - Update the bot directory path"
echo "   - Reboot your device"
echo ""
print_success "Happy trading! 🚀"
