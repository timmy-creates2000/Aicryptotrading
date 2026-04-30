#!/usr/bin/env python3
# setup_webhook.py — Setup Telegram webhook for Render deployment

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")  # e.g., https://your-app.onrender.com

def setup_webhook():
    """Setup Telegram webhook for command handling."""
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env")
        return False
    
    if not RENDER_URL:
        print("❌ RENDER_EXTERNAL_URL not found in .env")
        print("   Add it to .env: RENDER_EXTERNAL_URL=https://your-app.onrender.com")
        return False
    
    webhook_url = f"{RENDER_URL.rstrip('/')}/telegram/webhook"
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    
    print(f"🔧 Setting up Telegram webhook...")
    print(f"   Webhook URL: {webhook_url}")
    
    try:
        response = requests.post(api_url, json={"url": webhook_url}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print("✅ Webhook setup successful!")
                print(f"   Description: {result.get('description', 'N/A')}")
                return True
            else:
                print(f"❌ Webhook setup failed: {result.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def check_webhook():
    """Check current webhook status."""
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        return
    
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"
    
    try:
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                info = result.get("result", {})
                print("\n📊 Current Webhook Status:")
                print(f"   URL: {info.get('url', 'Not set')}")
                print(f"   Pending updates: {info.get('pending_update_count', 0)}")
                print(f"   Last error: {info.get('last_error_message', 'None')}")
                print(f"   Max connections: {info.get('max_connections', 'N/A')}")
            else:
                print(f"❌ Failed to get webhook info: {result.get('description')}")
        else:
            print(f"❌ HTTP Error {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def delete_webhook():
    """Delete webhook (use for local testing)."""
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        return False
    
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
    
    try:
        response = requests.post(api_url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print("✅ Webhook deleted successfully!")
                return True
            else:
                print(f"❌ Failed: {result.get('description')}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "═" * 60)
    print("  TELEGRAM WEBHOOK SETUP")
    print("═" * 60 + "\n")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            setup_webhook()
        elif command == "check":
            check_webhook()
        elif command == "delete":
            delete_webhook()
        else:
            print("❌ Unknown command")
            print("\nUsage:")
            print("  python setup_webhook.py setup   - Setup webhook")
            print("  python setup_webhook.py check   - Check webhook status")
            print("  python setup_webhook.py delete  - Delete webhook")
    else:
        # Default: setup webhook
        setup_webhook()
        print("\n")
        check_webhook()
