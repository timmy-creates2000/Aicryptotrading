#!/usr/bin/env python3
"""
setup_telegram_features.py — Setup script for Telegram bot features

This script helps configure and test Telegram bot integration including:
- Balance fetching (demo/real accounts)
- Strategy RAG system
- File upload capabilities
- Command handlers
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def check_environment():
    """Check if required environment variables are set."""
    print("🔍 Checking environment variables...")
    
    required_vars = {
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
        "BYBIT_API_KEY": os.getenv("BYBIT_API_KEY"),
        "BYBIT_API_SECRET": os.getenv("BYBIT_API_SECRET")
    }
    
    missing = []
    for var, value in required_vars.items():
        if not value:
            missing.append(var)
            print(f"  ❌ {var}: Not set")
        else:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"  ✅ {var}: {masked}")
    
    if missing:
        print(f"\n⚠️  Missing variables: {', '.join(missing)}")
        print("Please add them to your .env file")
        return False
    
    print("✅ All environment variables configured\n")
    return True


def check_dependencies():
    """Check if required Python packages are installed."""
    print("📦 Checking dependencies...")
    
    required_packages = [
        "flask",
        "requests",
        "python-dotenv",
        "pybit"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    print("✅ All dependencies installed\n")
    return True


def check_modules():
    """Check if custom modules are available."""
    print("🔧 Checking custom modules...")
    
    modules = {
        "telegram_commands": "Telegram command handlers",
        "telegram_control_panel": "Trading config panel",
        "balance_manager": "Balance fetching",
        "strategy_rag": "Strategy RAG system",
        "strategy_uploader": "File upload handler"
    }
    
    available = {}
    for module, description in modules.items():
        try:
            __import__(module)
            print(f"  ✅ {module}: {description}")
            available[module] = True
        except ImportError as e:
            print(f"  ⚠️  {module}: Not available ({str(e)})")
            available[module] = False
    
    print()
    return available


def test_telegram_connection():
    """Test connection to Telegram API."""
    print("📡 Testing Telegram connection...")
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("  ❌ TELEGRAM_BOT_TOKEN not set")
        return False
    
    try:
        import requests
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data.get("result", {})
                print(f"  ✅ Connected to bot: @{bot_info.get('username')}")
                print(f"     Name: {bot_info.get('first_name')}")
                return True
        
        print(f"  ❌ Failed: {response.status_code}")
        return False
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False


def test_bybit_connection():
    """Test connection to Bybit API."""
    print("\n💱 Testing Bybit connection...")
    
    api_key = os.getenv("BYBIT_API_KEY")
    api_secret = os.getenv("BYBIT_API_SECRET")
    
    if not api_key or not api_secret:
        print("  ❌ Bybit credentials not set")
        return False
    
    try:
        from pybit.unified_trading import HTTP
        
        session = HTTP(
            testnet=True,
            api_key=api_key,
            api_secret=api_secret
        )
        
        # Try to get wallet balance
        result = session.get_wallet_balance(accountType="UNIFIED")
        
        if result.get("retCode") == 0:
            print("  ✅ Connected to Bybit (Demo)")
            return True
        else:
            print(f"  ❌ Failed: {result.get('retMsg')}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False


def setup_strategies_folder():
    """Create strategies folder if it doesn't exist."""
    print("\n📁 Setting up strategies folder...")
    
    folder = "strategies"
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"  ✅ Created {folder}/ directory")
    else:
        print(f"  ✅ {folder}/ directory exists")
    
    # Count existing strategy files
    files = [f for f in os.listdir(folder) if f.endswith(('.txt', '.md', '.pdf'))]
    print(f"  📚 Found {len(files)} strategy file(s)")
    
    return True


def print_summary(results):
    """Print setup summary."""
    print("\n" + "="*50)
    print("📋 SETUP SUMMARY")
    print("="*50)
    
    all_good = all(results.values())
    
    for check, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check}")
    
    print("="*50)
    
    if all_good:
        print("\n🎉 All checks passed! Telegram features are ready.")
        print("\nNext steps:")
        print("1. Start the server: python server.py")
        print("2. Test commands in Telegram: /start")
        print("3. Upload strategy files via Telegram")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
    
    print()


def main():
    """Run all setup checks."""
    print("\n🚀 TELEGRAM FEATURES SETUP")
    print("="*50 + "\n")
    
    results = {
        "Environment Variables": check_environment(),
        "Dependencies": check_dependencies(),
        "Telegram Connection": test_telegram_connection(),
        "Bybit Connection": test_bybit_connection(),
        "Strategies Folder": setup_strategies_folder()
    }
    
    # Check modules (informational only)
    print("\n📦 Optional Features:")
    modules = check_modules()
    
    print_summary(results)
    
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
