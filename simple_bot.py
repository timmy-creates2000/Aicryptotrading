#!/usr/bin/env python3
"""
Simple Crypto Trading Bot - Essentials Only
- Bybit REAL trading (mainnet)
- Gemini AI for signals
- Telegram notifications
- Auto-start on deploy
"""

import os
import time
import json
import threading
from datetime import datetime
from dotenv import load_dotenv
from pybit.unified_trading import HTTP
import google.generativeai as genai
import requests
from flask import Flask

load_dotenv()

# Flask app for Render health check
app = Flask(__name__)

@app.route('/')
def health():
    return {"status": "running", "bot": "simple_crypto_bot"}, 200

@app.route('/health')
def health_check():
    return {"status": "ok"}, 200

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Trading settings
WATCHLIST = ["DOGEUSDT", "XRPUSDT", "ADAUSDT", "TRXUSDT", "SHIBUSDT"]  # Cheap coins for small balance
TRADE_AMOUNT_USDT = 0.1  # Tiny trades - $0.10 per trade
LEVERAGE = 10  # Higher leverage to meet minimums
SCAN_INTERVAL = 60  # seconds
MIN_CONFIDENCE = 75  # AI confidence threshold

# ═══════════════════════════════════════════════════════════════
# BYBIT API
# ═══════════════════════════════════════════════════════════════

bybit = HTTP(testnet=False, api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET)

def get_price(symbol):
    """Get current price for a symbol."""
    try:
        response = bybit.get_tickers(category="linear", symbol=symbol)
        return float(response["result"]["list"][0]["lastPrice"])
    except Exception as e:
        print(f"❌ Error getting price for {symbol}: {e}")
        return None

def get_balance():
    """Get USDT balance."""
    try:
        response = bybit.get_wallet_balance(accountType="UNIFIED", coin="USDT")
        balance = float(response["result"]["list"][0]["coin"][0]["walletBalance"])
        return balance
    except Exception as e:
        print(f"❌ Error getting balance: {e}")
        return 0.0

def place_order(symbol, side, qty):
    """Place a market order."""
    try:
        bybit.set_leverage(
            category="linear",
            symbol=symbol,
            buyLeverage=str(LEVERAGE),
            sellLeverage=str(LEVERAGE)
        )
        
        response = bybit.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=str(qty),
            positionIdx=0
        )
        
        return response["result"]["orderId"]
    except Exception as e:
        print(f"❌ Order failed: {e}")
        return None

# ═══════════════════════════════════════════════════════════════
# GEMINI AI
# ═══════════════════════════════════════════════════════════════

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def get_ai_signal(symbol, price):
    """Get trading signal from Gemini AI."""
    prompt = f"""
You are a crypto trading expert. Analyze {symbol} at current price ${price}.

Based on market conditions, provide a trading signal.

Respond ONLY with valid JSON:
{{
  "signal": "BUY" or "SELL" or "WAIT",
  "confidence": 0-100,
  "reason": "brief explanation"
}}
"""
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        return result
    except Exception as e:
        print(f"❌ AI error for {symbol}: {e}")
        return {"signal": "WAIT", "confidence": 0, "reason": "AI error"}

# ═══════════════════════════════════════════════════════════════
# TELEGRAM
# ═══════════════════════════════════════════════════════════════

def send_telegram(message):
    """Send message to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
    except:
        pass

# ═══════════════════════════════════════════════════════════════
# TRADING LOGIC
# ═══════════════════════════════════════════════════════════════

def scan_markets():
    """Scan all pairs and return best signal."""
    print(f"\n🔍 Scanning {len(WATCHLIST)} pairs...")
    
    signals = []
    
    for symbol in WATCHLIST:
        price = get_price(symbol)
        if not price:
            continue
        
        analysis = get_ai_signal(symbol, price)
        signal = analysis.get("signal", "WAIT")
        confidence = analysis.get("confidence", 0)
        
        print(f"  {symbol}: {signal} ({confidence}%)")
        
        if signal in ["BUY", "SELL"] and confidence >= MIN_CONFIDENCE:
            signals.append({
                "symbol": symbol,
                "signal": signal,
                "confidence": confidence,
                "price": price,
                "reason": analysis.get("reason", "")
            })
    
    if not signals:
        print("  No strong signals found")
        return None
    
    # Return highest confidence signal
    best = max(signals, key=lambda x: x["confidence"])
    print(f"\n🏆 Best: {best['symbol']} {best['signal']} ({best['confidence']}%)")
    return best

def execute_trade(signal):
    """Execute a trade based on signal."""
    symbol = signal["symbol"]
    side = signal["signal"]
    price = signal["price"]
    
    # Calculate quantity - round to appropriate decimals based on price
    if price < 1:
        qty = round((TRADE_AMOUNT_USDT * LEVERAGE) / price, 0)  # Whole numbers for cheap coins
    elif price < 10:
        qty = round((TRADE_AMOUNT_USDT * LEVERAGE) / price, 1)
    else:
        qty = round((TRADE_AMOUNT_USDT * LEVERAGE) / price, 3)
    
    print(f"\n📊 Executing {side} on {symbol}")
    print(f"   Price: ${price}")
    print(f"   Quantity: {qty}")
    print(f"   Value: ${TRADE_AMOUNT_USDT} × {LEVERAGE}x = ${TRADE_AMOUNT_USDT * LEVERAGE}")
    
    order_id = place_order(symbol, side, qty)
    
    if order_id:
        msg = (
            f"✅ TRADE EXECUTED\n\n"
            f"Symbol: {symbol}\n"
            f"Side: {side}\n"
            f"Price: ${price}\n"
            f"Quantity: {qty}\n"
            f"Confidence: {signal['confidence']}%\n"
            f"Reason: {signal['reason']}\n\n"
            f"Order ID: {order_id}"
        )
        send_telegram(msg)
        print(f"✅ Order placed: {order_id}")
        return True
    else:
        send_telegram(f"❌ Trade failed for {symbol}")
        return False

# ═══════════════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════════════

def main():
    """Main trading loop."""
    print("\n" + "="*60)
    print("🤖 SIMPLE CRYPTO TRADING BOT")
    print("="*60)
    print(f"Mode: REAL TRADING (Bybit Mainnet)")
    print(f"Pairs: {', '.join(WATCHLIST)}")
    print(f"Trade Size: ${TRADE_AMOUNT_USDT} × {LEVERAGE}x leverage")
    print(f"Scan Interval: {SCAN_INTERVAL}s")
    print("="*60 + "\n")
    
    # Check balance
    balance = get_balance()
    print(f"💰 Balance: ${balance:.2f} USDT\n")
    
    if balance < TRADE_AMOUNT_USDT:
        print(f"⚠️  Warning: Balance ${balance:.2f} is low. Bot will trade with ${TRADE_AMOUNT_USDT} per trade.")
        send_telegram(f"⚠️ Bot started with low balance: ${balance:.2f}\nTrade size: ${TRADE_AMOUNT_USDT} × {LEVERAGE}x = ${TRADE_AMOUNT_USDT * LEVERAGE}")
    
    send_telegram(f"🤖 Bot started!\nBalance: ${balance:.2f}\nWatching: {', '.join(WATCHLIST)}")
    
    while True:
        try:
            # Scan markets
            signal = scan_markets()
            
            # Execute if signal found
            if signal:
                execute_trade(signal)
                # Wait longer after trade
                print(f"\n⏳ Waiting 5 minutes before next scan...")
                time.sleep(300)
            else:
                print(f"\n⏳ Next scan in {SCAN_INTERVAL}s...")
                time.sleep(SCAN_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
            send_telegram("🛑 Bot stopped")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    # Start Flask server in background thread
    port = int(os.getenv("PORT", 10000))
    flask_thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=port, debug=False),
        daemon=True
    )
    flask_thread.start()
    print(f"✅ Health check server started on port {port}")
    
    # Start trading bot
    main()
