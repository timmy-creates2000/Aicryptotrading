# telegram_commands.py — Interactive Telegram command handler with Config Panel

import json
import os
from datetime import datetime
from flask import request, Blueprint
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Import bot state management
from server import bot_status
from telegram_control_panel import get_config

# Import balance and strategy features
try:
    from balance_manager import get_balance_fetcher, BalanceFormatter
    BALANCE_ENABLED = True
except ImportError:
    BALANCE_ENABLED = False
    print("  [telegram] ⚠️  Balance features not available")

try:
    from strategy_rag import get_strategy_rag
    STRATEGIES_ENABLED = True
except ImportError:
    STRATEGIES_ENABLED = False
    print("  [telegram] ⚠️  Strategy features not available")

try:
    from strategy_uploader import get_strategy_uploader
    UPLOADER_ENABLED = True
except ImportError:
    UPLOADER_ENABLED = False
    print("  [telegram] ⚠️  Strategy uploader not available")

telegram_bp = Blueprint('telegram', __name__)

# ─── COMMAND STATE ──────────────────────────────────────────────
command_callbacks = {}


def register_command(cmd_name):
    """Decorator to register command handlers."""
    def decorator(func):
        command_callbacks[cmd_name] = func
        return func
    return decorator


def send_telegram_message(text: str, chat_id: str = None):
    """Send message to Telegram chat."""
    if not chat_id:
        chat_id = TELEGRAM_CHAT_ID
    
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        print("  [telegram] ⚠️  Telegram not configured")
        return False
    
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"  [telegram] Error: {e}")
        return False


def send_telegram_keyboard(text: str, buttons: list, chat_id: str = None):
    """Send message with inline keyboard buttons."""
    if not chat_id:
        chat_id = TELEGRAM_CHAT_ID
    
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        return False
    
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Build keyboard layout
    keyboard = {"inline_keyboard": []}
    for row in buttons:
        keyboard["inline_keyboard"].append(row)
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": keyboard
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"  [telegram] Error: {e}")
        return False


# ─── COMMAND HANDLERS ────────────────────────────────────────────

@register_command("start")
def cmd_start():
    """Handle /start command - Shows menu and starts bot if not running."""
    status = bot_status
    
    # Check if bot is already running
    if not status.get("running", False):
        # Start the bot
        try:
            import main
            threading.Thread(target=main.start, daemon=True).start()
            bot_msg = "✅ Bot started and scanning for signals!"
        except Exception as e:
            bot_msg = f"⚠️ Bot status: {str(e)}"
    else:
        bot_msg = "✅ Bot is already running!"
    
    return (
        f"🚀 <b>TRADING BOT CONTROLLER</b>\n\n"
        f"{bot_msg}\n\n"
        f"<b>Available commands:</b>\n"
        f"• /balance - View account balance\n"
        f"• /accounts - Compare demo/real\n"
        f"• /status - Bot status\n"
        f"• /stats - Win/loss stats\n"
        f"• /strategies - Manage strategies\n"
        f"• /help - All commands\n"
        f"• /resume - Resume trading\n"
        f"• /pause - Pause trading\n\n"
        f"Click buttons below or type command:"
    ), [
        [
            {"text": "💰 Balance", "callback_data": "cmd_balance"},
            {"text": "📊 Status", "callback_data": "cmd_status"}
        ],
        [
            {"text": "📚 Strategies", "callback_data": "cmd_strategies"},
            {"text": "📈 Stats", "callback_data": "cmd_stats"}
        ],
        [
            {"text": "▶️ Resume", "callback_data": "cmd_resume"},
            {"text": "⏸️  Pause", "callback_data": "cmd_pause"}
        ]
    ]


@register_command("status")
def cmd_status():
    """Show current bot status."""
    status = bot_status
    msg = (
        f"📊 <b>BOT STATUS</b>\n\n"
        f"<b>Running:</b> {'✅ YES' if status['running'] else '❌ NO'}\n"
        f"<b>Current Trade:</b> {status.get('current_trade', 'None')}\n"
        f"<b>Last Scan:</b> {status.get('last_scan', 'Never')}\n"
        f"<b>Total Trades:</b> {status['total_trades']}\n"
        f"<b>Wins:</b> {status['wins']} ✅\n"
        f"<b>Losses:</b> {status['losses']} ❌\n"
        f"<b>Win Rate:</b> "
    )
    
    if status['total_trades'] > 0:
        win_rate = (status['wins'] / status['total_trades'] * 100)
        msg += f"{win_rate:.1f}%"
    else:
        msg += "N/A"
    
    msg += f"\n<b>Updated:</b> {datetime.now().strftime('%H:%M:%S')}"
    
    return msg, None


@register_command("stats")
def cmd_stats():
    """Show detailed statistics."""
    status = bot_status
    
    if status['total_trades'] == 0:
        return "📈 <b>NO TRADES YET</b>\nBet your first trade to see stats.", None
    
    win_rate = (status['wins'] / status['total_trades'] * 100)
    loss_rate = (status['losses'] / status['total_trades'] * 100)
    
    msg = (
        f"📈 <b>TRADE STATISTICS</b>\n\n"
        f"<b>Total Trades:</b> {status['total_trades']}\n"
        f"<b>Wins:</b> {status['wins']} ({win_rate:.1f}%)\n"
        f"<b>Losses:</b> {status['losses']} ({loss_rate:.1f}%)\n"
        f"<b>Win/Loss Ratio:</b> 1:{status['losses']/max(status['wins'], 1):.2f}\n\n"
        f"<b>Streaks:</b>\n"
        f"Current streak tracking enabled\n\n"
        f"<b>Note:</b> Full P&L tracking in development"
    )
    
    return msg, None


@register_command("help")
def cmd_help():
    """Show all available commands."""
    msg = (
        "<b>📋 AVAILABLE COMMANDS</b>\n\n"
        "<b>💰 Balance & Accounts:</b>\n"
        "/balance - View current balance\n"
        "/accounts - Compare demo/real\n\n"
        "<b>📚 Strategy Management:</b>\n"
        "/strategies - Manage strategies\n"
        "/reload_strategies - Reload all\n\n"
        "<b>🤖 Bot Control:</b>\n"
        "/start - Show main menu\n"
        "/status - Current bot status\n"
        "/stats - Win/loss statistics\n"
        "/resume - Resume trading\n"
        "/pause - Pause trading\n"
        "/stop - Stop the bot\n\n"
        "<b>⚙️ Configuration:</b>\n"
        "/config - Trading settings\n"
        "/mode - Switch DEMO/REAL\n"
        "/logs - View telegram logs\n\n"
        "<b>💡 Tip:</b> Use buttons for quick access!"
    )
    
    return msg, None


@register_command("resume")
def cmd_resume():
    """Resume trading."""
    bot_status["running"] = True
    return (
        "▶️ <b>TRADING RESUMED</b>\n\n"
        "Bot is now actively scanning for signals.\n"
        "New trades will be placed automatically."
    ), None


@register_command("pause")
def cmd_pause():
    """Pause trading (keep open trades)."""
    bot_status["running"] = False
    return (
        "⏸️  <b>TRADING PAUSED</b>\n\n"
        "No new trades will be opened.\n"
        "Existing trades will continue with trailing stops."
    ), None


@register_command("stop")
def cmd_stop():
    """Stop the bot."""
    bot_status["running"] = False
    msg = (
        "🛑 <b>BOT STOPPED</b>\n\n"
        "The trading bot has been stopped.\n"
        "To restart, use /resume"
    )
    return msg, None


@register_command("config")
def cmd_config():
    """Show current trading configuration."""
    cfg = get_config()
    status = cfg.get_status()
    
    msg = (
        f"⚙️ <b>TRADING CONFIG</b>\n\n"
        f"<b>Mode:</b> {status['mode']}\n"
        f"<b>Trade Amount:</b> ${status['trade_amount']}\n"
        f"<b>Leverage:</b> {status['leverage']}x\n"
        f"<b>Stop Loss:</b> {status['stop_loss']}%\n"
        f"<b>Take Profit:</b> {status['take_profit']}%\n"
        f"<b>Max Losses:</b> {status['max_losses']} in a row\n"
        f"<b>Daily Loss Limit:</b> {status['max_daily_loss']}%\n\n"
        f"<b>Commands:</b>\n"
        f"/mode - Switch DEMO/REAL\n"
        f"/amount - Set trade amount\n"
        f"/leverage - Set leverage\n"
        f"/keys - Manage API keys"
    )
    
    return msg, [
        [
            {"text": "🔄 Switch Mode", "callback_data": "cmd_mode"},
            {"text": "💵 Set Amount", "callback_data": "cmd_amount"}
        ],
        [
            {"text": "📈 Set Leverage", "callback_data": "cmd_leverage"}
        ]
    ]


@register_command("mode")
def cmd_mode():
    """Show mode switcher."""
    cfg = get_config()
    current_mode = cfg.config["mode"]
    next_mode = "REAL" if current_mode == "DEMO" else "DEMO"
    
    msg = (
        f"🔄 <b>SWITCH MODE</b>\n\n"
        f"Current: <b>{current_mode}</b>\n"
        f"Next: <b>{next_mode}</b>\n\n"
        f"Choose action:"
    )
    
    return msg, [
        [
            {"text": f"✅ Switch to {next_mode}", "callback_data": f"switch_mode_{next_mode}"}
        ],
        [
            {"text": "❌ Cancel", "callback_data": "cmd_config"}
        ]
    ]


@register_command("amount")
def cmd_amount():
    """Show trade amount options."""
    msg = (
        "💵 <b>SET TRADE AMOUNT</b>\n\n"
        "Select trade amount per trade (in USDT):\n"
        "Choose based on your account size"
    )
    
    amounts = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
    buttons = []
    
    for i in range(0, len(amounts), 2):
        row = [{"text": f"${amounts[i]}", "callback_data": f"set_amount_{amounts[i]}"}]
        if i + 1 < len(amounts):
            row.append({"text": f"${amounts[i+1]}", "callback_data": f"set_amount_{amounts[i+1]}"})
        buttons.append(row)
    
    buttons.append([{"text": "❌ Cancel", "callback_data": "cmd_config"}])
    
    return msg, buttons


@register_command("leverage")
def cmd_leverage():
    """Show leverage options."""
    msg = (
        "📈 <b>SET LEVERAGE</b>\n\n"
        "Select leverage multiplier:\n"
        "⚠️ Higher leverage = Higher risk"
    )
    
    leverages = [1, 2, 3, 5, 10]
    buttons = []
    
    for lever in leverages:
        risk = "🟢 Low" if lever <= 2 else "🟡 Medium" if lever <= 5 else "🔴 High"
        buttons.append([{"text": f"{lever}x ({risk})", "callback_data": f"set_leverage_{lever}"}])
    
    buttons.append([{"text": "❌ Cancel", "callback_data": "cmd_config"}])
    
    return msg, buttons


@register_command("keys")
def cmd_keys():
    """Manage API keys."""
    msg = (
        "🔑 <b>MANAGE API KEYS</b>\n\n"
        "Select which keys to add:\n"
        "Demo: For testing with real prices\n"
        "Real: For live trading"
    )
    
    return msg, [
        [
            {"text": "🎮 Demo Keys", "callback_data": "add_demo_keys"},
            {"text": "💰 Real Keys", "callback_data": "add_real_keys"}
        ],
        [
            {"text": "❌ Cancel", "callback_data": "cmd_config"}
        ]
    ]


@register_command("strategies")
def cmd_strategies():
    """List and manage strategy documents (RAG)."""
    if not STRATEGIES_ENABLED:
        return "❌ Strategy features not available", None
    
    try:
        # List files in strategies folder
        strategies_folder = "strategies"
        if not os.path.exists(strategies_folder):
            os.makedirs(strategies_folder)
        
        strategy_files = [f for f in os.listdir(strategies_folder) 
                         if f.endswith(('.txt', '.md', '.pdf'))]
        
        msg = (
            "📚 <b>STRATEGY DOCUMENTS (RAG)</b>\n\n"
            f"Active: {len(strategy_files)}\n"
            f"Folder: strategies/\n\n"
        )
        
        buttons = []
        
        if strategy_files:
            msg += "<b>Current Strategies:</b>\n"
            for i, filename in enumerate(strategy_files, 1):
                filepath = os.path.join(strategies_folder, filename)
                size_kb = os.path.getsize(filepath) / 1024
                msg += f"{i}. {filename} ({size_kb:.1f} KB)\n"
                
                # Add preview and delete buttons for each file
                buttons.append([
                    {"text": f"👁️ {filename[:20]}...", "callback_data": f"strategy_preview_{filename}"},
                    {"text": "🗑️", "callback_data": f"strategy_delete_{filename}"}
                ])
            
            msg += "\n"
        else:
            msg += "No strategies uploaded yet.\n\n"
        
        msg += "💡 <b>Upload Guide:</b>\n"
        msg += "Send me .txt, .md, or .pdf files directly!\n\n"
        msg += "📝 Strategy examples:\n"
        msg += "• Supply/demand zones\n"
        msg += "• Entry/exit rules\n"
        msg += "• Risk management\n"
        msg += "• ICT, SMC strategies"
        
        buttons.append([{"text": "🔄 Reload All", "callback_data": "cmd_reload_strategies"}])
        buttons.append([{"text": "❌ Back", "callback_data": "cmd_help"}])
        
        return msg, buttons
        
    except Exception as e:
        return f"❌ Error: {str(e)}", None


@register_command("upload_strategy")
def cmd_upload_strategy():
    """Guide for uploading strategy documents."""
    msg = (
        "📤 <b>UPLOAD STRATEGY GUIDE</b>\n\n"
        "<b>Option 1: Text Message (Easy)</b>\n"
        "1. Type your strategy rules\n"
        "2. I'll save to strategies/ folder\n"
        "3. Format: 'strategy_name.txt: your strategy text here'\n\n"
        
        "<b>Option 2: Telegram File (Files)</b>\n"
        "1. Create .txt or .md file\n"
        "2. Send as document/file\n"
        "3. I'll save to strategies/\n\n"
        
        "<b>Option 3: Manual Upload</b>\n"
        "1. Connect to your server/Render\n"
        "2. Upload to strategies/ folder\n"
        "3. Bot reads automatically\n\n"
        
        "<b>Example Strategy:</b>\n"
        "<code>supply_demand.txt:\n"
        "- Find 3x touch zones\n"
        "- Entry at break with confirmation\n"
        "- SL: 2% below zone\n"
        "- TP: 2:1 risk/reward</code>"
    )
    
    buttons = [
        [{"text": "📋 Show Strategies", "callback_data": "cmd_strategies"}],
        [{"text": "❌ Cancel", "callback_data": "cmd_help"}]
    ]
    
    return msg, buttons


# ─── CALLBACK HANDLERS FOR CONFIG ────────────────────────────────

def handle_switch_mode(mode: str, chat_id: str):
    """Handle mode switch callback."""
    cfg = get_config()
    cfg.set_mode(mode)
    
    # Clear balance cache when switching modes
    if BALANCE_ENABLED:
        try:
            from balance_manager import get_balance_cache
            cache = get_balance_cache()
            cache.clear()
        except:
            pass
    
    msg = (
        f"✅ <b>MODE SWITCHED</b>\n\n"
        f"New mode: <b>{mode}</b>\n"
        f"API keys: Updated\n"
        f"Status: Ready\n\n"
        f"⚠️ <b>Note:</b> Restart bot for changes to take effect"
    )
    send_telegram_message(msg, chat_id)


def handle_set_amount(amount: float, chat_id: str):
    """Handle trade amount change."""
    cfg = get_config()
    if cfg.set_trade_amount(amount):
        msg = (
            f"✅ <b>TRADE AMOUNT SET</b>\n\n"
            f"New amount: ${amount}\n"
            f"Per trade: ${amount}\n"
            f"Status: Active on next trade"
        )
    else:
        msg = f"❌ Invalid amount: {amount}"
    
    send_telegram_message(msg, chat_id)


def handle_set_leverage(leverage: int, chat_id: str):
    """Handle leverage change."""
    cfg = get_config()
    if cfg.set_leverage(leverage):
        risk_level = "🟢 Low" if leverage <= 2 else "🟡 Medium" if leverage <= 5 else "🔴 High"
        msg = (
            f"✅ <b>LEVERAGE SET</b>\n\n"
            f"New leverage: {leverage}x\n"
            f"Risk level: {risk_level}\n"
            f"Status: Active on next trade"
        )
    else:
        msg = f"❌ Invalid leverage: {leverage} (use 1-10)"
    
    send_telegram_message(msg, chat_id)


def handle_add_demo_keys(chat_id: str):
    """Prompt to add demo keys."""
    msg = (
        "🎮 <b>ADD DEMO KEYS</b>\n\n"
        "Send your API credentials in this format:\n\n"
        "<code>demo_key=YOUR_API_KEY\n"
        "demo_secret=YOUR_API_SECRET</code>\n\n"
        "Get from: Bybit → Settings → API → Demo Trading"
    )
    send_telegram_message(msg, chat_id)


def handle_add_real_keys(chat_id: str):
    """Prompt to add real keys."""
    msg = (
        "💰 <b>ADD REAL KEYS</b>\n\n"
        "⚠️ <b>IMPORTANT:</b> Only add real keys when ready for live trading!\n\n"
        "Send in this format:\n\n"
        "<code>real_key=YOUR_API_KEY\n"
        "real_secret=YOUR_API_SECRET</code>\n\n"
        "Get from: Bybit → Settings → API → Real Account"
    )
    send_telegram_message(msg, chat_id)


def handle_strategy_preview(filename: str, chat_id: str):
    """Show preview of strategy file content."""
    if not STRATEGIES_ENABLED:
        send_telegram_message("❌ Strategy features not available", chat_id)
        return
    
    try:
        filepath = os.path.join("strategies", filename)
        
        if not os.path.exists(filepath):
            send_telegram_message(f"❌ File not found: {filename}", chat_id)
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Show first 500 characters
        preview_length = 500
        preview = content[:preview_length]
        
        msg = (
            f"📄 <b>STRATEGY PREVIEW</b>\n\n"
            f"<b>File:</b> {filename}\n"
            f"<b>Size:</b> {len(content)} chars\n\n"
            f"<code>{preview}</code>"
        )
        
        buttons = []
        if len(content) > preview_length:
            msg += f"\n\n... ({len(content) - preview_length} more characters)"
            buttons.append([{"text": "📖 Show Full Content", "callback_data": f"strategy_full_{filename}"}])
        
        buttons.append([{"text": "❌ Back", "callback_data": "cmd_strategies"}])
        
        send_telegram_keyboard(msg, buttons, chat_id)
        
    except Exception as e:
        send_telegram_message(f"❌ Error reading file: {str(e)}", chat_id)


def handle_strategy_delete(filename: str, chat_id: str):
    """Show confirmation dialog for strategy deletion."""
    msg = (
        f"⚠️ <b>DELETE STRATEGY</b>\n\n"
        f"Are you sure you want to delete:\n"
        f"<b>{filename}</b>\n\n"
        f"This action cannot be undone."
    )
    
    buttons = [
        [{"text": "✅ Yes, Delete", "callback_data": f"strategy_delete_confirm_{filename}"}],
        [{"text": "❌ Cancel", "callback_data": "cmd_strategies"}]
    ]
    
    send_telegram_keyboard(msg, buttons, chat_id)


def handle_strategy_delete_confirm(filename: str, chat_id: str):
    """Execute strategy file deletion."""
    if not STRATEGIES_ENABLED:
        send_telegram_message("❌ Strategy features not available", chat_id)
        return
    
    try:
        filepath = os.path.join("strategies", filename)
        
        if not os.path.exists(filepath):
            send_telegram_message(f"❌ File not found: {filename}", chat_id)
            return
        
        # Delete file
        os.remove(filepath)
        
        # Reload RAG system
        rag = get_strategy_rag()
        rag.load_strategies()
        
        msg = (
            f"✅ <b>STRATEGY DELETED</b>\n\n"
            f"File: {filename}\n"
            f"RAG system reloaded\n\n"
            f"Use /strategies to view remaining files"
        )
        
        send_telegram_message(msg, chat_id)
        
    except Exception as e:
        send_telegram_message(f"❌ Error deleting file: {str(e)}", chat_id)


@register_command("logs")
def cmd_logs():
    """Show telegram message logs."""
    try:
        log_file = os.getenv("TELEGRAM_LOG_FILE", "telegram_messages.log")
        
        if not os.path.exists(log_file):
            return "📋 No logs found yet.", None
        
        # Read last 10 messages
        with open(log_file, "r") as f:
            lines = f.readlines()[-10:]
        
        msg = "<b>📋 RECENT TELEGRAM LOGS (Last 10)</b>\n\n"
        
        for line in lines:
            try:
                log_entry = json.loads(line)
                msg += (
                    f"<b>{log_entry['type']}</b> - "
                    f"{log_entry['status']}\n"
                    f"Time: {log_entry['timestamp'][:19]}\n\n"
                )
            except:
                pass
        
        return msg, None
    
    except Exception as e:
        return f"❌ Error reading logs: {e}", None


@register_command("force_close")
def cmd_force_close():
    """Force close current trade."""
    current_trade = bot_status.get("current_trade")
    
    if not current_trade:
        return "⚠️  No open trade to close.", None
    
    # TODO: Implement actual force close via trader.py
    return (
        f"🔄 <b>FORCE CLOSING</b>\n\n"
        f"Trade: {current_trade}\n"
        f"(Feature in development)"
    ), None


# ─── NEW BALANCE COMMANDS ────────────────────────────────────────

@register_command("balance")
def cmd_balance():
    """Show current account balance."""
    if not BALANCE_ENABLED:
        return "❌ Balance features not available. Install balance_manager.py", None
    
    try:
        fetcher = get_balance_fetcher()
        config = get_config()
        current_mode = config.config.get("mode", "DEMO")
        
        balance_data = fetcher.get_balance(current_mode)
        
        if not balance_data:
            return "❌ <b>Could not fetch balance</b>\n\nPlease check your API keys.", [
                [{"text": "🔄 Retry", "callback_data": "balance_refresh"}],
                [{"text": "⚙️ Settings", "callback_data": "cmd_config"}]
            ]
        
        msg = BalanceFormatter.format_display(balance_data)
        
        buttons = [
            [{"text": "🔄 Refresh", "callback_data": "balance_refresh"}],
            [{"text": "💰 Compare Accounts", "callback_data": "cmd_accounts"}]
        ]
        
        return msg, buttons
        
    except Exception as e:
        return f"❌ Error: {str(e)}", None


@register_command("accounts")
def cmd_accounts():
    """Compare demo and real account balances."""
    if not BALANCE_ENABLED:
        return "❌ Balance features not available", None
    
    try:
        fetcher = get_balance_fetcher()
        config = get_config()
        current_mode = config.config.get("mode", "DEMO")
        
        balances = fetcher.get_both_balances()
        demo_balance = balances.get("DEMO")
        real_balance = balances.get("REAL")
        
        msg = BalanceFormatter.format_comparison(demo_balance, real_balance, current_mode)
        
        buttons = []
        if current_mode == "DEMO":
            buttons.append([{"text": "🔄 Switch to REAL", "callback_data": "mode_switch_REAL"}])
        else:
            buttons.append([{"text": "🎮 Switch to DEMO", "callback_data": "mode_switch_DEMO"}])
        
        buttons.append([{"text": "🔄 Refresh", "callback_data": "cmd_accounts"}])
        
        return msg, buttons
        
    except Exception as e:
        return f"❌ Error: {str(e)}", None


@register_command("reload_strategies")
def cmd_reload_strategies():
    """Reload all strategy documents."""
    if not STRATEGIES_ENABLED:
        return "❌ Strategy features not available", None
    
    try:
        rag = get_strategy_rag()
        rag.load_strategies()
        
        summary = rag.get_strategy_summary()
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        msg = f"✅ <b>STRATEGIES RELOADED</b>\n\n"
        msg += f"<b>Loaded:</b> {summary['strategies_loaded']} files\n"
        msg += f"<b>Total:</b> {summary['total_chars']:,} characters\n"
        msg += f"<b>Time:</b> {timestamp}"
        
        buttons = [
            [{"text": "📚 View Strategies", "callback_data": "cmd_strategies"}]
        ]
        
        return msg, buttons
        
    except Exception as e:
        return f"❌ Error: {str(e)}", None


# ─── TELEGRAM WEBHOOK HANDLER ───────────────────────────────────

@telegram_bp.route("/telegram/webhook", methods=["POST"])
def telegram_webhook():
    """Handle incoming Telegram messages."""
    try:
        data = request.get_json()
        
        # Handle regular messages
        if "message" in data:
            message = data["message"]
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text", "").strip()
            
            # Handle document uploads
            if "document" in message:
                if UPLOADER_ENABLED:
                    document = message["document"]
                    file_id = document.get("file_id")
                    filename = document.get("file_name", "unknown.txt")
                    
                    uploader = get_strategy_uploader(TELEGRAM_BOT_TOKEN)
                    success, msg, file_info = uploader.download_and_save(file_id, filename)
                    
                    if success:
                        response = (
                            f"✅ <b>UPLOAD SUCCESSFUL</b>\n\n"
                            f"{msg}\n\n"
                            f"<b>File Info:</b>\n"
                            f"• Name: {file_info.filename}\n"
                            f"• Size: {file_info.file_size / 1024:.1f} KB\n"
                            f"• Type: {file_info.file_type}\n\n"
                            f"💡 Strategy loaded into RAG system"
                        )
                    else:
                        response = f"❌ <b>UPLOAD FAILED</b>\n\n{msg}"
                    
                    send_telegram_message(response, chat_id)
                else:
                    send_telegram_message(
                        "❌ Strategy upload not available. Please check configuration.",
                        chat_id
                    )
            
            # Handle text commands
            elif text.startswith("/"):
                cmd = text.split()[0].lstrip("/").lower()
                
                if cmd in command_callbacks:
                    result = command_callbacks[cmd]()
                    
                    if isinstance(result, tuple):
                        msg_text, buttons = result
                        if buttons:
                            send_telegram_keyboard(msg_text, buttons, chat_id)
                        else:
                            send_telegram_message(msg_text, chat_id)
                    else:
                        send_telegram_message(result, chat_id)
                else:
                    send_telegram_message(
                        f"❌ Unknown command: /{cmd}\n\nType /help for available commands",
                        chat_id
                    )
        
        # Handle button clicks (callback queries)
        elif "callback_query" in data:
            callback = data["callback_query"]
            chat_id = callback.get("from", {}).get("id")
            callback_data = callback.get("data", "").lower()
            
            # Handle config callbacks
            if callback_data.startswith("switch_mode_"):
                mode = callback_data.replace("switch_mode_", "").upper()
                handle_switch_mode(mode, chat_id)
            
            elif callback_data.startswith("set_amount_"):
                amount = float(callback_data.replace("set_amount_", ""))
                handle_set_amount(amount, chat_id)
            
            elif callback_data.startswith("set_leverage_"):
                leverage = int(callback_data.replace("set_leverage_", ""))
                handle_set_leverage(leverage, chat_id)
            
            elif callback_data == "add_demo_keys":
                handle_add_demo_keys(chat_id)
            
            elif callback_data == "add_real_keys":
                handle_add_real_keys(chat_id)
            
            # Handle balance callbacks
            elif callback_data == "balance_refresh":
                if BALANCE_ENABLED:
                    try:
                        fetcher = get_balance_fetcher()
                        config = get_config()
                        current_mode = config.config.get("mode", "DEMO")
                        balance_data = fetcher.get_balance(current_mode, force_refresh=True)
                        
                        if balance_data:
                            msg = BalanceFormatter.format_display(balance_data)
                            send_telegram_message(msg, chat_id)
                        else:
                            send_telegram_message("❌ Could not refresh balance", chat_id)
                    except Exception as e:
                        send_telegram_message(f"❌ Error: {str(e)}", chat_id)
            
            elif callback_data.startswith("mode_switch_"):
                mode = callback_data.replace("mode_switch_", "").upper()
                handle_switch_mode(mode, chat_id)
            
            # Handle strategy callbacks
            elif callback_data.startswith("strategy_preview_"):
                filename = callback_data.replace("strategy_preview_", "")
                handle_strategy_preview(filename, chat_id)
            
            elif callback_data.startswith("strategy_delete_"):
                filename = callback_data.replace("strategy_delete_", "")
                handle_strategy_delete(filename, chat_id)
            
            elif callback_data.startswith("strategy_delete_confirm_"):
                filename = callback_data.replace("strategy_delete_confirm_", "")
                handle_strategy_delete_confirm(filename, chat_id)
            
            # Handle command callbacks
            elif callback_data.startswith("cmd_"):
                cmd = callback_data.replace("cmd_", "").lower()
                
                if cmd in command_callbacks:
                    result = command_callbacks[cmd]()
                    
                    if isinstance(result, tuple):
                        msg_text, buttons = result
                        if buttons:
                            send_telegram_keyboard(msg_text, buttons, chat_id)
                        else:
                            send_telegram_message(msg_text, chat_id)
                    else:
                        send_telegram_message(result, chat_id)
        
        return {"ok": True}
    
    except Exception as e:
        print(f"  [telegram] Webhook error: {e}")
        return {"ok": False}, 400


# ─── MONITORING FUNCTION ────────────────────────────────────────

def get_bot_status_display():
    """Get formatted bot status for display."""
    status = bot_status
    
    emoji = "🟢" if status["running"] else "🔴"
    msg = f"{emoji} <b>BOT STATUS</b>\n"
    msg += f"Running: {'✅ YES' if status['running'] else '❌ NO'}\n"
    msg += f"Current Trade: {status.get('current_trade', 'None')}\n"
    msg += f"Total Trades: {status['total_trades']}\n"
    msg += f"Win Rate: {(status['wins'] / max(status['total_trades'], 1) * 100):.1f}%"
    
    return msg


def setup_telegram_webhook(bot_token: str, webhook_url: str):
    """Setup Telegram webhook (call once to register)."""
    import requests
    
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    payload = {"url": webhook_url}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("  [telegram] ✅ Webhook registered")
            return True
    except Exception as e:
        print(f"  [telegram] ❌ Webhook setup failed: {e}")
    
    return False
