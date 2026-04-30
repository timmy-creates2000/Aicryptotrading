# server.py — Tiny web server for Render + UptimeRobot health checks + Telegram webhook

from flask import Flask, jsonify
import threading
import os

app = Flask(__name__)

# ─── Bot status tracker ──────────────────────────────────────────
bot_status = {
    "running": False,
    "current_trade": None,
    "last_scan": None,
    "total_trades": 0,
    "wins": 0,
    "losses": 0,
    "paused": False,
}

# Register Telegram commands blueprint
try:
    from telegram_commands import telegram_bp
    app.register_blueprint(telegram_bp)
    TELEGRAM_ENABLED = True
except ImportError:
    TELEGRAM_ENABLED = False
    print("  [server] ⚠️  Telegram commands not available")


@app.route("/")
def home():
    """UptimeRobot pings this every 5 minutes to keep bot alive."""
    return jsonify({
        "status": "alive",
        "bot_running": bot_status["running"],
        "current_trade": bot_status["current_trade"],
        "last_scan": bot_status["last_scan"],
        "total_trades": bot_status["total_trades"],
        "wins": bot_status["wins"],
        "losses": bot_status["losses"],
        "win_rate": f"{(bot_status['wins'] / bot_status['total_trades'] * 100):.1f}%" 
                    if bot_status["total_trades"] > 0 else "N/A"
    })


@app.route("/health")
def health():
    """Simple health check endpoint."""
    return jsonify({"status": "ok"}), 200


@app.route("/status")
def status():
    """Detailed bot status."""
    return jsonify(bot_status)


def run_server():
    """Runs Flask in a background thread."""
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


def start_server_thread():
    """Start the web server in background so bot loop can run on main thread."""
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print(f"  [server] ✅ Web server started on port {os.environ.get('PORT', 8080)}")
