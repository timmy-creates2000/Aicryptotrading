#!/usr/bin/env python3
"""Quick test script to verify bot configuration"""

import os
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*60)
print("🔍 TRADING BOT - CONFIGURATION TEST")
print("="*60 + "\n")

# Test 1: Environment Variables
print("1️⃣ Environment Variables:")
print("-" * 40)

env_vars = {
    "BYBIT_API_KEY": os.getenv("BYBIT_API_KEY"),
    "BYBIT_API_SECRET": os.getenv("BYBIT_API_SECRET"),
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
}

all_set = True
for key, value in env_vars.items():
    if value and value != f"your_{key.lower()}_here":
        masked = value[:8] + "..." if len(value) > 8 else "***"
        print(f"  ✅ {key}: {masked}")
    else:
        print(f"  ❌ {key}: NOT SET")
        all_set = False

print()

# Test 2: Python Dependencies
print("2️⃣ Python Dependencies:")
print("-" * 40)

dependencies = {
    "pybit": "Bybit API",
    "google.generativeai": "Gemini AI",
    "requests": "HTTP requests",
    "flask": "Web server",
    "dotenv": "Environment loader",
}

deps_ok = True
for module, description in dependencies.items():
    try:
        __import__(module.replace(".", "_") if "." in module else module)
        print(f"  ✅ {description} ({module})")
    except ImportError:
        print(f"  ❌ {description} ({module}) - NOT INSTALLED")
        deps_ok = False

print()

# Test 3: Custom Modules
print("3️⃣ Custom Modules:")
print("-" * 40)

modules = [
    "config",
    "scanner", 
    "trader",
    "telegram_bot",
    "strategy_rag",
    "balance_manager",
]

modules_ok = True
for module in modules:
    try:
        __import__(module)
        print(f"  ✅ {module}.py")
    except Exception as e:
        print(f"  ❌ {module}.py - {str(e)[:40]}")
        modules_ok = False

print()

# Test 4: Telegram Connection
print("4️⃣ Telegram Bot Connection:")
print("-" * 40)

telegram_ok = False
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

if bot_token and bot_token != "your_telegram_bot_token_here":
    try:
        import requests
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data.get("result", {})
                print(f"  ✅ Connected to: @{bot_info.get('username')}")
                print(f"  ✅ Bot name: {bot_info.get('first_name')}")
                telegram_ok = True
            else:
                print(f"  ❌ API Error: {data.get('description')}")
        else:
            print(f"  ❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Connection failed: {str(e)}")
else:
    print("  ⚠️  Token not configured")

print()

# Test 5: Bybit Connection
print("5️⃣ Bybit API Connection:")
print("-" * 40)

bybit_ok = False
api_key = os.getenv("BYBIT_API_KEY")
api_secret = os.getenv("BYBIT_API_SECRET")

if api_key and api_secret:
    try:
        from pybit.unified_trading import HTTP
        
        # Try testnet first
        session = HTTP(
            testnet=True,
            api_key=api_key,
            api_secret=api_secret
        )
        
        result = session.get_wallet_balance(accountType="UNIFIED")
        
        if result.get("retCode") == 0:
            print("  ✅ Connected to Bybit Testnet")
            bybit_ok = True
        else:
            # Try mainnet
            session = HTTP(
                testnet=False,
                api_key=api_key,
                api_secret=api_secret
            )
            
            result = session.get_wallet_balance(accountType="UNIFIED")
            
            if result.get("retCode") == 0:
                print("  ✅ Connected to Bybit Mainnet")
                print("  ⚠️  WARNING: Using REAL account!")
                bybit_ok = True
            else:
                print(f"  ❌ API Error: {result.get('retMsg')}")
    except Exception as e:
        print(f"  ❌ Connection failed: {str(e)}")
else:
    print("  ⚠️  API keys not configured")

print()

# Final Summary
print("="*60)
print("📊 SUMMARY")
print("="*60)

status = {
    "Environment Variables": all_set,
    "Python Dependencies": deps_ok,
    "Custom Modules": modules_ok,
    "Telegram Connection": telegram_ok,
    "Bybit Connection": bybit_ok,
}

for check, passed in status.items():
    icon = "✅" if passed else "❌"
    print(f"{icon} {check}")

print("="*60)

if all(status.values()):
    print("\n🎉 ALL CHECKS PASSED - BOT IS READY!")
    print("\nYou can now run:")
    print("  python main.py")
else:
    print("\n⚠️  SOME CHECKS FAILED")
    print("\nPlease fix the issues above before running the bot.")

print()
