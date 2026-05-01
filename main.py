# main.py — Trading Bot Controller
# Runs Flask server (for Render/UptimeRobot) + trading loop together

import os
import time
import threading
from datetime import datetime
from config import SCAN_INTERVAL_SECONDS, WATCHLIST
from scanner import scan_all_pairs
from trader import place_trade, get_open_position
from trailing import manage_trailing_stop
from server import start_server_thread, bot_status
from telegram_bot import (
    send_message,
    notify_scan_start,
    notify_best_signal,
    notify_trade_opened,
    notify_trade_closed,
    notify_no_signal,
    notify_bot_started,
    notify_bot_stopped,
)
from risk_management import get_risk_manager, check_trade_risk
from strategy_rag import get_strategy_rag

# ─── BOT STATE ────────────────────────────────────────────────────
is_running = False
current_trade = None


def print_banner():
    rag = get_strategy_rag()
    risk_manager = get_risk_manager()
    
    strategies_status = f"{rag.get_strategy_summary()['strategies_loaded']} strategy docs loaded" if rag.has_strategies() else "No strategy docs"
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║          🤖 TRADING BOT — BYBIT MAINNET (Real Trading)       ║
║                                                              ║
║   Pairs           : {} pairs in watchlist                 ║
║   Mode            : Multi-timeframe + Technical Indicators   ║
║   AI              : Gemini 1.5 Flash + RAG                   ║
║   Risk Management : Max {} losses, {} daily loss limit    ║
║   Strategy        : {}                ║
╚══════════════════════════════════════════════════════════════╝
""".format(
        len(WATCHLIST),
        risk_manager.max_consecutive_losses,
        f"{risk_manager.max_daily_loss_pct}%",
        strategies_status
    ))


def trading_loop():
    """The main bot loop — runs until stopped."""
    global is_running, current_trade

    bot_status["running"] = True
    notify_bot_started()
    print("✅ Bot started. Watching markets...\n")

    while is_running:
        try:
            # ── Check if paused ──
            if bot_status.get("paused", False):
                print("⏸️  Trading PAUSED. Waiting for resume...\n")
                time.sleep(SCAN_INTERVAL_SECONDS)
                continue

            # ── Step 1: Check if there's already an open trade ──
            if current_trade:
                symbol = current_trade["symbol"]
                bot_status["current_trade"] = symbol
                position = get_open_position(symbol)

                if position:
                    print(f"⏳ Trade still open on {symbol}. Waiting...")
                    time.sleep(SCAN_INTERVAL_SECONDS)
                    continue
                else:
                    # Trade closed externally (SL or TP hit)
                    print(f"✅ {symbol} trade closed. Resuming scan...\n")
                    current_trade = None
                    bot_status["current_trade"] = None

            # ── Step 2: Scan all pairs for best signal ──
            notify_scan_start(len(WATCHLIST))
            best_signal = scan_all_pairs()
            
            # Update last scan time
            bot_status["last_scan"] = datetime.now().strftime("%H:%M:%S")

            if not best_signal:
                notify_no_signal()
                print(f"⏳ No signal. Next scan in {SCAN_INTERVAL_SECONDS}s...\n")
                time.sleep(SCAN_INTERVAL_SECONDS)
                continue

            # ── Step 3: Place the trade ──
            notify_best_signal(best_signal)

            trade = place_trade(
                symbol=best_signal["symbol"],
                signal=best_signal["signal"]
            )

            if not trade:
                print("❌ Trade failed to place. Retrying on next scan.\n")
                time.sleep(SCAN_INTERVAL_SECONDS)
                continue

            current_trade = trade
            bot_status["current_trade"] = trade["symbol"]
            bot_status["total_trades"] += 1
            notify_trade_opened(trade, best_signal)

            # ── Step 4: Run trailing stop in a background thread ──
            def run_trailing():
                global current_trade
                summary = manage_trailing_stop(
                    trade=trade,
                    notify_callback=send_message
                )
                
                pnl = summary.get("pnl", 0)
                
                # Update stats
                if pnl > 0:
                    bot_status["wins"] += 1
                elif pnl < 0:
                    bot_status["losses"] += 1
                
                # Record trade in risk manager (check limits)
                check_trade_risk(pnl, trade["symbol"])
                
                # Pause bot if risk limits hit
                if bot_status.get("paused", False):
                    print("🛑 Risk limit hit - pausing bot")
                
                notify_trade_closed(summary)
                current_trade = None
                bot_status["current_trade"] = None

            trailing_thread = threading.Thread(target=run_trailing, daemon=True)
            trailing_thread.start()

            # Wait for trailing thread to finish before next scan
            trailing_thread.join()

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Bot error: {e}")
            time.sleep(10)

    print("\n🛑 Bot stopped.")
    bot_status["running"] = False
    notify_bot_stopped()


def start():
    global is_running
    if is_running:
        print("⚠️  Bot is already running!")
        return

    is_running = True
    print_banner()
    trading_loop()


def stop():
    global is_running
    is_running = False
    print("🛑 Stopping bot after current cycle...")


# ─── WEBHOOK AUTO-SETUP ─────────────────────────────────────────
def setup_telegram_webhook():
    """Automatically setup Telegram webhook on startup."""
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
    
    if not BOT_TOKEN or not RENDER_URL:
        print("  [webhook] ⚠️  Skipping webhook setup (missing config)")
        return
    
    try:
        import requests
        webhook_url = f"{RENDER_URL.rstrip('/')}/telegram/webhook"
        api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        
        print(f"  [webhook] 🔧 Setting up Telegram webhook...")
        response = requests.post(api_url, json={"url": webhook_url}, timeout=10)
        
        if response.status_code == 200 and response.json().get("ok"):
            print(f"  [webhook] ✅ Webhook configured: {webhook_url}")
        else:
            print(f"  [webhook] ⚠️  Webhook setup failed: {response.text}")
    except Exception as e:
        print(f"  [webhook] ⚠️  Could not setup webhook: {e}")


# ─── ENTRY POINT ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "═" * 50)
    print("  TRADING BOT — BYBIT")
    print("═" * 50)
    
    # Check if auto-start is enabled
    AUTO_START = os.getenv("AUTO_START_TRADING", "false").lower() == "true"
    
    try:
        # Start Flask server in background thread
        start_server_thread()
        
        # Auto-setup Telegram webhook
        setup_telegram_webhook()
        
        if AUTO_START:
            print("\n  ⚡ AUTO-START enabled - Starting trading bot...\n")
            start()
        else:
            print("\n  ⏸️  AUTO-START disabled - Bot ready, waiting for /start command\n")
            print("  💡 Use Telegram /start command to begin trading")
            print("  💡 Or set AUTO_START_TRADING=true in .env to auto-start\n")
            
            # Keep server running
            import time
            while True:
                time.sleep(60)
                
    except KeyboardInterrupt:
        stop()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
