#!/usr/bin/env python3
# test_api.py — Test Bybit API connection and balance fetch

import os
from dotenv import load_dotenv
from pybit.unified_trading import HTTP

load_dotenv()

print("╔══════════════════════════════════════════════════════════════╗")
print("║          🔧 BYBIT API CONNECTION TEST                        ║")
print("╚══════════════════════════════════════════════════════════════╝")
print()

# Get credentials
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")
TESTNET = os.getenv("BYBIT_TESTNET", "True") == "True"

print(f"📋 Configuration:")
print(f"   API Key: {API_KEY[:10]}..." if API_KEY else "   API Key: NOT SET")
print(f"   API Secret: {API_SECRET[:10]}..." if API_SECRET else "   API Secret: NOT SET")
print(f"   Testnet: {TESTNET}")
print(f"   Endpoint: {'https://api-testnet.bybit.com' if TESTNET else 'https://api.bybit.com'}")
print()

if not API_KEY or not API_SECRET:
    print("❌ API credentials not set in .env file!")
    print("   Please add BYBIT_API_KEY and BYBIT_API_SECRET")
    exit(1)

# Test connection
print("🔌 Testing API connection...")
try:
    session = HTTP(
        testnet=TESTNET,
        api_key=API_KEY,
        api_secret=API_SECRET
    )
    
    print("✅ Session created successfully")
    print()
    
    # Test 1: Get server time
    print("📡 Test 1: Get server time...")
    try:
        time_response = session.get_server_time()
        if time_response.get("retCode") == 0:
            print(f"✅ Server time: {time_response.get('result', {}).get('timeSecond')}")
        else:
            print(f"⚠️  Response: {time_response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 2: Get wallet balance
    print("💰 Test 2: Get wallet balance...")
    try:
        balance_response = session.get_wallet_balance(
            accountType="UNIFIED",
            coin="USDT"
        )
        
        print(f"📊 Response Code: {balance_response.get('retCode')}")
        print(f"📊 Response Message: {balance_response.get('retMsg')}")
        
        if balance_response.get("retCode") == 0:
            result = balance_response.get("result", {})
            account_list = result.get("list", [])
            
            if account_list:
                account = account_list[0]
                total_equity = float(account.get("totalEquity", 0))
                available = float(account.get("totalAvailableBalance", 0))
                
                print()
                print("✅ Balance fetched successfully!")
                print(f"   Total Equity: ${total_equity:,.2f}")
                print(f"   Available: ${available:,.2f}")
                print()
                
                # Show coin balances
                coins = account.get("coin", [])
                if coins:
                    print("   Coin Balances:")
                    for coin in coins:
                        symbol = coin.get("coin", "")
                        balance = float(coin.get("walletBalance", 0))
                        if balance > 0:
                            print(f"     • {symbol}: {balance:,.4f}")
            else:
                print("⚠️  No account data in response")
                print(f"   Full response: {balance_response}")
        else:
            print(f"❌ API Error: {balance_response.get('retMsg')}")
            print(f"   Full response: {balance_response}")
    
    except Exception as e:
        print(f"❌ Error fetching balance: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # Test 3: Get account info
    print("📋 Test 3: Get account info...")
    try:
        account_response = session.get_account_info()
        
        if account_response.get("retCode") == 0:
            result = account_response.get("result", {})
            print(f"✅ Account Type: {result.get('unifiedMarginStatus')}")
            print(f"   Margin Mode: {result.get('marginMode')}")
        else:
            print(f"⚠️  Response: {account_response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    ✅ TEST COMPLETE                          ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
except Exception as e:
    print(f"❌ Failed to create session: {e}")
    import traceback
    traceback.print_exc()
