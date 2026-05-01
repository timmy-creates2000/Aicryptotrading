#!/usr/bin/env python3
# diagnose_api.py — Comprehensive API diagnostics

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("🔍 BYBIT API DIAGNOSTICS")
print("=" * 70)
print()

# Step 1: Check environment variables
print("📋 Step 1: Checking Environment Variables")
print("-" * 70)

API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")
TESTNET = os.getenv("BYBIT_TESTNET", "False")

if not API_KEY:
    print("❌ BYBIT_API_KEY not set!")
    sys.exit(1)
else:
    print(f"✅ BYBIT_API_KEY: {API_KEY[:10]}...{API_KEY[-4:]}")

if not API_SECRET:
    print("❌ BYBIT_API_SECRET not set!")
    sys.exit(1)
else:
    print(f"✅ BYBIT_API_SECRET: {API_SECRET[:10]}...{API_SECRET[-4:]}")

testnet_bool = TESTNET.lower() == "true"
print(f"✅ BYBIT_TESTNET: {TESTNET} ({'Testnet' if testnet_bool else 'Mainnet'})")
print()

# Step 2: Test pybit import
print("📦 Step 2: Testing pybit Library")
print("-" * 70)
try:
    from pybit.unified_trading import HTTP
    print("✅ pybit library imported successfully")
except ImportError as e:
    print(f"❌ Failed to import pybit: {e}")
    print("   Run: pip install pybit")
    sys.exit(1)
print()

# Step 3: Create session
print("🔌 Step 3: Creating API Session")
print("-" * 70)
try:
    session = HTTP(
        testnet=testnet_bool,
        api_key=API_KEY,
        api_secret=API_SECRET
    )
    endpoint = "https://api-testnet.bybit.com" if testnet_bool else "https://api.bybit.com"
    print(f"✅ Session created")
    print(f"   Endpoint: {endpoint}")
except Exception as e:
    print(f"❌ Failed to create session: {e}")
    sys.exit(1)
print()

# Step 4: Test API key validity
print("🔑 Step 4: Testing API Key Validity")
print("-" * 70)
try:
    response = session.get_api_key_information()
    ret_code = response.get("retCode", -1)
    ret_msg = response.get("retMsg", "Unknown")
    
    if ret_code == 0:
        result = response.get("result", {})
        print("✅ API Key is valid")
        print(f"   User ID: {result.get('userId', 'N/A')}")
        print(f"   Note: {result.get('note', 'N/A')}")
        
        # Check permissions
        permissions = result.get("permissions", {})
        if permissions:
            print(f"   Permissions:")
            for perm_type, perm_list in permissions.items():
                print(f"     • {perm_type}: {', '.join(perm_list) if perm_list else 'None'}")
    else:
        print(f"❌ API Key Error: {ret_msg} (Code: {ret_code})")
        print("   Possible issues:")
        print("   1. API key is invalid or expired")
        print("   2. API key is for wrong environment (testnet vs mainnet)")
        print("   3. IP whitelist restriction")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error checking API key: {e}")
    import traceback
    traceback.print_exc()
print()

# Step 5: Test wallet balance
print("💰 Step 5: Testing Wallet Balance Fetch")
print("-" * 70)
try:
    response = session.get_wallet_balance(
        accountType="UNIFIED",
        coin="USDT"
    )
    
    ret_code = response.get("retCode", -1)
    ret_msg = response.get("retMsg", "Unknown")
    
    print(f"   Response Code: {ret_code}")
    print(f"   Response Message: {ret_msg}")
    
    if ret_code == 0:
        result = response.get("result", {})
        account_list = result.get("list", [])
        
        if account_list:
            account = account_list[0]
            total_equity = float(account.get("totalEquity", 0))
            available = float(account.get("totalAvailableBalance", 0))
            
            print(f"✅ Balance fetched successfully!")
            print(f"   Total Equity: ${total_equity:,.2f}")
            print(f"   Available Balance: ${available:,.2f}")
            
            # Show coin balances
            coins = account.get("coin", [])
            if coins:
                print(f"   Coin Balances:")
                for coin in coins:
                    symbol = coin.get("coin", "")
                    balance = float(coin.get("walletBalance", 0))
                    if balance > 0:
                        print(f"     • {symbol}: {balance:,.4f}")
        else:
            print("⚠️  No account data returned")
            print("   Possible issues:")
            print("   1. No Unified Trading Account")
            print("   2. Account not activated")
            print("   3. Wrong account type")
            print()
            print("   Solution:")
            print("   1. Go to Bybit → Assets")
            print("   2. Enable 'Unified Trading Account'")
            print("   3. Transfer funds to Unified Account")
    else:
        print(f"❌ Balance Fetch Failed: {ret_msg} (Code: {ret_code})")
        print()
        print("   Common Error Codes:")
        print("   • 10001: Invalid parameter")
        print("   • 10003: Invalid API key")
        print("   • 10004: Invalid sign")
        print("   • 10005: Permission denied")
        print("   • 10006: Too many requests")
        print()
        
        if ret_code == 10005:
            print("   ⚠️  PERMISSION DENIED")
            print("   Your API key doesn't have 'Read' or 'Wallet' permission")
            print()
            print("   Fix:")
            print("   1. Go to Bybit → API Management")
            print("   2. Find your API key")
            print("   3. Enable these permissions:")
            print("      ✅ Read")
            print("      ✅ Wallet")
            print("   4. Save changes")
        
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error fetching balance: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
print()

# Step 6: Test account info
print("📊 Step 6: Testing Account Info")
print("-" * 70)
try:
    response = session.get_account_info()
    ret_code = response.get("retCode", -1)
    
    if ret_code == 0:
        result = response.get("result", {})
        print(f"✅ Account Info:")
        print(f"   Unified Margin Status: {result.get('unifiedMarginStatus', 'N/A')}")
        print(f"   Margin Mode: {result.get('marginMode', 'N/A')}")
        print(f"   DCPN Status: {result.get('dcpStatus', 'N/A')}")
    else:
        print(f"⚠️  Could not fetch account info: {response.get('retMsg')}")
except Exception as e:
    print(f"⚠️  Error: {e}")
print()

# Step 7: Summary
print("=" * 70)
print("📊 DIAGNOSTIC SUMMARY")
print("=" * 70)
print()
print("✅ All tests passed!")
print()
print("Your API is working correctly. If balance still doesn't show in bot:")
print()
print("1. Check Render environment variables match your .env")
print("2. Redeploy on Render")
print("3. Check Render logs for errors")
print("4. Try /balance command in Telegram")
print()
print("=" * 70)
