# telegram_bot.py — Advanced Telegram alerts with retry, rate limiting & queuing

import requests
import os
import time
import json
import threading
from datetime import datetime, timedelta
from collections import deque
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_LOG_FILE = os.getenv("TELEGRAM_LOG_FILE", "telegram_messages.log")

# ─── MESSAGE QUEUE & RATE LIMITING ───────────────────────────────
message_queue = deque()
rate_limiter = {"last_sent": 0, "delay": 0.1}  # 10 msg/sec max
message_log = []
lock = threading.Lock()


def log_message(msg_type: str, content: str, status: str, details: str = ""):
    """Logs all Telegram messages to file for debugging."""
    with lock:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": msg_type,
            "content": content[:100],  # First 100 chars
            "status": status,
            "details": details
        }
        message_log.append(log_entry)
        
        try:
            with open(TELEGRAM_LOG_FILE, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"  [telegram] ⚠️  Could not write log: {e}")


def wait_for_rate_limit():
    """Enforces rate limiting (10 messages per second max)."""
    with lock:
        elapsed = time.time() - rate_limiter["last_sent"]
        if elapsed < rate_limiter["delay"]:
            sleep_time = rate_limiter["delay"] - elapsed
            time.sleep(sleep_time)
        rate_limiter["last_sent"] = time.time()


def send_message_with_retry(text: str, msg_type: str = "GENERAL", max_retries: int = 3) -> bool:
    """
    Sends a message with exponential backoff retry logic.
    
    Returns:
        True if sent successfully, False if all retries failed
    """
    if not BOT_TOKEN or not CHAT_ID:
        print("  [telegram] ⚠️  Telegram not configured — skipping alert")
        log_message(msg_type, text, "SKIPPED", "Not configured")
        return False

    wait_for_rate_limit()

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"  [telegram] ✅ {msg_type} alert sent")
                log_message(msg_type, text, "SUCCESS", f"Attempt {attempt + 1}")
                return True
            
            # Rate limit error — back off
            elif response.status_code == 429:
                retry_after = int(response.json().get("parameters", {}).get("retry_after", 1))
                print(f"  [telegram] ⏱️  Rate limited. Waiting {retry_after}s...")
                log_message(msg_type, text, "RATE_LIMITED", f"Retry after {retry_after}s")
                time.sleep(retry_after)
                continue
            
            # Other error — retry with backoff
            else:
                error_msg = response.json().get("description", response.text)
                print(f"  [telegram] ⚠️  Error ({response.status_code}): {error_msg}")
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    print(f"  [telegram] 🔄 Retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})...")
                    log_message(msg_type, text, "RETRY", f"{error_msg} - Retry {attempt + 1}")
                    time.sleep(wait_time)
                else:
                    log_message(msg_type, text, "FAILED", error_msg)
                    return False
        
        except requests.Timeout:
            print(f"  [telegram] ⏱️  Timeout (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                log_message(msg_type, text, "TIMEOUT", "All retries exhausted")
                return False
        
        except Exception as e:
            print(f"  [telegram] ❌ Error: {e}")
            if attempt == max_retries - 1:
                log_message(msg_type, text, "ERROR", str(e))
                return False
    
    return False


def send_message(text: str):
    """Alias for send_message_with_retry for backwards compatibility."""
    return send_message_with_retry(text, "GENERAL")


def notify_scan_start(pairs_count: int):
    """Notifies when scan starts."""
    msg = f"🔍 <b>SCAN STARTING</b>\n" \
          f"Time: {datetime.now().strftime('%H:%M:%S')}\n" \
          f"Pairs: {pairs_count}\n" \
          f"Confidence threshold: 75%"
    send_message_with_retry(msg, "SCAN_START")


def notify_best_signal(analysis: dict):
    """Notifies when best signal is found."""
    confidence_bar = "▓" * (analysis.get("confidence", 0) // 10) + "░" * (10 - analysis.get("confidence", 0) // 10)
    msg = (
        f"🏆 <b>BEST SIGNAL FOUND</b>\n"
        f"Pair: <b>{analysis.get('symbol', 'N/A')}</b>\n"
        f"Signal: <b>{analysis.get('signal', 'WAIT')}</b>\n"
        f"Confidence: {confidence_bar} {analysis.get('confidence', 0)}%\n"
        f"Reason: <i>{analysis.get('reason', 'No reason provided')}</i>"
    )
    send_message_with_retry(msg, "BEST_SIGNAL")


def notify_trade_opened(trade: dict, analysis: dict):
    """Notifies when trade is placed - with detailed info."""
    risk_reward = "N/A"
    if trade.get("entry_price") and trade.get("stop_loss") and trade.get("take_profit"):
        risk = abs(trade["entry_price"] - trade["stop_loss"])
        reward = abs(trade["take_profit"] - trade["entry_price"])
        if risk > 0:
            risk_reward = f"1:{reward/risk:.2f}"
    
    msg = (
        f"⚡ <b>TRADE OPENED</b>\n"
        f"<b>Pair:</b> {trade.get('symbol', 'N/A')}\n"
        f"<b>Side:</b> {trade.get('side', 'N/A')}\n"
        f"<b>Entry:</b> {trade.get('entry_price', 'N/A')}\n"
        f"<b>SL:</b> {trade.get('stop_loss', 'N/A')}\n"
        f"<b>TP:</b> {trade.get('take_profit', 'N/A')}\n"
        f"<b>Qty:</b> {trade.get('quantity', 'N/A')}\n"
        f"<b>R:R:</b> {risk_reward}\n"
        f"<b>AI Confidence:</b> {analysis.get('confidence', 'N/A')}%\n"
        f"📊 <i>Trailing stop ACTIVE</i>"
    )
    send_message_with_retry(msg, "TRADE_OPENED")


def notify_trade_update(symbol: str, current_price: float, current_sl: float, locked_profit: float):
    """Notifies of trailing stop updates during trade."""
    msg = (
        f"📊 <b>TRAIL UPDATE</b>\n"
        f"Pair: <b>{symbol}</b>\n"
        f"Price: {current_price}\n"
        f"New SL: {current_sl}\n"
        f"💰 Locked: +{locked_profit} USDT"
    )
    send_message_with_retry(msg, "TRAIL_UPDATE")


def notify_trade_closed(summary: dict):
    """Notifies when trade closes - with full analytics."""
    pnl = summary.get("pnl", 0)
    locked = summary.get("locked_profit", 0)
    emoji = "✅ WIN" if pnl > 0 else "❌ LOSS" if pnl < 0 else "⏸️  BREAK-EVEN"
    roi_pct = "N/A"
    
    if summary.get("entry_price") and summary.get("entry_price") > 0:
        roi_pct = f"{(pnl / (summary['entry_price'] * summary.get('quantity', 1)) * 100):.2f}%" if summary.get('quantity') else "N/A"
    
    msg = (
        f"{emoji}\n"
        f"<b>Pair:</b> {summary.get('symbol', 'N/A')}\n"
        f"<b>Entry:</b> {summary.get('entry_price', 'N/A')} → <b>Exit:</b> {summary.get('exit_price', 'N/A')}\n"
        f"<b>PnL:</b> {'+' if pnl >= 0 else ''}{pnl:.4f} USDT (ROI: {roi_pct})\n"
        f"<b>Locked Profit:</b> {locked:.4f} USDT\n"
        f"📈 <b>Duration:</b> {summary.get('duration_minutes', 'N/A')} min\n"
        f"🔄 <b>SL Updates:</b> {summary.get('sl_updates', 0)}\n"
        f"<b>Final Trend:</b> {summary.get('final_trend', 'UNKNOWN')}"
    )
    send_message_with_retry(msg, "TRADE_CLOSED")


def notify_no_signal():
    """Notifies when no signal is found."""
    msg = f"⏳ <b>No signal found</b>\nTime: {datetime.now().strftime('%H:%M:%S')}\nWaiting for next scan..."
    send_message_with_retry(msg, "NO_SIGNAL")


def notify_bot_started():
    """Notifies when bot starts."""
    msg = f"🚀 <b>TRADING BOT STARTED</b>\n" \
          f"Time: {datetime.now().strftime('%H:%M:%S')}\n" \
          f"Mode: Testnet\n" \
          f"Status: Scanning for signals..."
    send_message_with_retry(msg, "BOT_STARTED")


def notify_bot_stopped():
    """Notifies when bot stops."""
    msg = f"🛑 <b>TRADING BOT STOPPED</b>\n" \
          f"Time: {datetime.now().strftime('%H:%M:%S')}"
    send_message_with_retry(msg, "BOT_STOPPED")


def notify_error(error_type: str, error_msg: str):
    """Notifies of critical errors."""
    msg = (
        f"❌ <b>ERROR ALERT</b>\n"
        f"<b>Type:</b> {error_type}\n"
        f"<b>Message:</b> {error_msg}\n"
        f"Time: {datetime.now().strftime('%H:%M:%S')}"
    )
    send_message_with_retry(msg, "ERROR")


def get_message_stats():
    """Returns statistics on sent messages."""
    with lock:
        total = len(message_log)
        success = sum(1 for m in message_log if m["status"] == "SUCCESS")
        failed = sum(1 for m in message_log if m["status"] == "FAILED")
        rate_limited = sum(1 for m in message_log if m["status"] == "RATE_LIMITED")
    
    return {
        "total_attempts": total,
        "successful": success,
        "failed": failed,
        "rate_limited": rate_limited,
        "success_rate": f"{(success/total*100):.1f}%" if total > 0 else "0%"
    }

