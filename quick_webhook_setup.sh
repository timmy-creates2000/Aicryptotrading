#!/bin/bash
# quick_webhook_setup.sh - Quick Telegram webhook setup

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          🔧 TELEGRAM WEBHOOK SETUP                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Create .env file with your credentials first"
    exit 1
fi

# Load environment variables
source .env

# Check required variables
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN not set in .env"
    exit 1
fi

if [ -z "$RENDER_EXTERNAL_URL" ]; then
    echo "⚠️  RENDER_EXTERNAL_URL not set in .env"
    echo ""
    echo "Please enter your Render URL (e.g., https://your-app.onrender.com):"
    read RENDER_URL
    
    if [ -z "$RENDER_URL" ]; then
        echo "❌ No URL provided"
        exit 1
    fi
else
    RENDER_URL=$RENDER_EXTERNAL_URL
fi

# Remove trailing slash
RENDER_URL=${RENDER_URL%/}

WEBHOOK_URL="${RENDER_URL}/telegram/webhook"
API_URL="https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook"

echo "🔧 Setting up webhook..."
echo "   Bot Token: ${TELEGRAM_BOT_TOKEN:0:10}..."
echo "   Webhook URL: $WEBHOOK_URL"
echo ""

# Set webhook
RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{\"url\":\"$WEBHOOK_URL\"}")

# Check response
if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo "✅ Webhook setup successful!"
    echo ""
    echo "📊 Webhook Info:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""
    echo "✅ You can now use Telegram commands:"
    echo "   /start - Start the bot"
    echo "   /status - Check status"
    echo "   /balance - View balance"
    echo ""
else
    echo "❌ Webhook setup failed!"
    echo ""
    echo "Response:"
    echo "$RESPONSE"
    echo ""
    echo "Common issues:"
    echo "  1. Check TELEGRAM_BOT_TOKEN is correct"
    echo "  2. Check RENDER_EXTERNAL_URL is accessible"
    echo "  3. Make sure bot is deployed on Render"
fi

echo ""
echo "🔍 Checking webhook status..."
CHECK_URL="https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"
curl -s "$CHECK_URL" | python3 -m json.tool 2>/dev/null || curl -s "$CHECK_URL"
