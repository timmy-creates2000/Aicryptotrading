# risk_management.py — Risk controls: loss streak, daily P&L limits

import json
import os
from datetime import datetime, date
from server import bot_status
from telegram_bot import notify_error


class RiskManager:
    """
    Manages trading risk:
    - Stops after 3 consecutive losses
    - Stops if daily loss exceeds 5% of balance
    - Tracks streak and daily P&L
    """
    
    def __init__(self, balance_usdt: float = 1000.0):
        self.initial_balance = balance_usdt
        self.current_balance = balance_usdt
        self.loss_streak = 0
        self.win_streak = 0
        self.daily_pnl = 0.0
        self.daily_date = date.today()
        self.max_consecutive_losses = 3
        self.max_daily_loss_pct = 5.0  # 5% daily loss limit
        self.trades_today = []
        self.is_paused = False
        self.pause_reason = ""
        
        # Try to load from file
        self.load_state()
    
    def load_state(self):
        """Load risk state from disk."""
        try:
            if os.path.exists("risk_state.json"):
                with open("risk_state.json", "r") as f:
                    state = json.load(f)
                    self.loss_streak = state.get("loss_streak", 0)
                    self.win_streak = state.get("win_streak", 0)
                    self.daily_pnl = state.get("daily_pnl", 0.0)
                    self.current_balance = state.get("current_balance", self.initial_balance)
        except Exception as e:
            print(f"  [risk] Could not load state: {e}")
    
    def save_state(self):
        """Save risk state to disk."""
        try:
            state = {
                "loss_streak": self.loss_streak,
                "win_streak": self.win_streak,
                "daily_pnl": self.daily_pnl,
                "current_balance": self.current_balance,
                "timestamp": datetime.now().isoformat()
            }
            with open("risk_state.json", "w") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"  [risk] Could not save state: {e}")
    
    def record_trade(self, pnl: float, symbol: str) -> dict:
        """
        Record a trade result and check risk limits.
        
        Returns: {
            'allowed': True/False,
            'reason': explanation,
            'should_pause': True/False,
            'status': current risk status
        }
        """
        # Reset daily stats if new day
        today = date.today()
        if today != self.daily_date:
            self.daily_date = today
            self.daily_pnl = 0.0
            self.trades_today = []
            self.loss_streak = 0
            self.win_streak = 0
            self.is_paused = False
            print(f"  [risk] 📅 New day - risk counters reset")
        
        # Update balance and P&L
        self.current_balance += pnl
        self.daily_pnl += pnl
        self.trades_today.append({
            "symbol": symbol,
            "pnl": pnl,
            "time": datetime.now().isoformat()
        })
        
        # Update streaks
        if pnl > 0:
            self.win_streak += 1
            self.loss_streak = 0
        elif pnl < 0:
            self.loss_streak += 1
            self.win_streak = 0
        else:
            # Break even - reset both
            self.loss_streak = 0
            self.win_streak = 0
        
        # Check risk limits
        should_pause = False
        reason = ""
        
        # Check consecutive losses
        if self.loss_streak >= self.max_consecutive_losses:
            should_pause = True
            reason = f"❌ {self.loss_streak} consecutive losses - PAUSING for 1 hour"
            self.is_paused = True
            self.pause_reason = reason
            print(f"  [risk] {reason}")
        
        # Check daily loss limit
        daily_loss_pct = abs(self.daily_pnl) / self.initial_balance * 100 if self.daily_pnl < 0 else 0
        if daily_loss_pct > self.max_daily_loss_pct:
            should_pause = True
            reason = f"⚠️  Daily loss {daily_loss_pct:.1f}% exceeds {self.max_daily_loss_pct}% limit - STOPPING"
            self.is_paused = True
            self.pause_reason = reason
            print(f"  [risk] {reason}")
        
        # Save state
        self.save_state()
        
        return {
            "allowed": True,  # Trade was recorded
            "should_pause": should_pause,
            "reason": reason,
            "status": self.get_status()
        }
    
    def get_status(self) -> dict:
        """Get current risk status."""
        daily_loss_pct = abs(self.daily_pnl) / self.initial_balance * 100 if self.daily_pnl < 0 else 0
        
        return {
            "balance": round(self.current_balance, 2),
            "daily_pnl": round(self.daily_pnl, 2),
            "daily_loss_pct": round(daily_loss_pct, 2),
            "loss_streak": self.loss_streak,
            "win_streak": self.win_streak,
            "trades_today": len(self.trades_today),
            "is_paused": self.is_paused,
            "pause_reason": self.pause_reason,
            "max_consecutive_losses": self.max_consecutive_losses,
            "max_daily_loss_pct": self.max_daily_loss_pct
        }
    
    def format_for_telegram(self) -> str:
        """Format risk status for Telegram."""
        status = self.get_status()
        
        # Color coding for PnL
        if status["daily_pnl"] > 0:
            pnl_emoji = "✅"
        elif status["daily_pnl"] < 0:
            pnl_emoji = "❌"
        else:
            pnl_emoji = "⏸️"
        
        # Streak emoji
        if self.loss_streak > 0:
            streak_emoji = "🔴"
            streak_text = f"Loss streak: {self.loss_streak}/{self.max_consecutive_losses}"
        elif self.win_streak > 0:
            streak_emoji = "🟢"
            streak_text = f"Win streak: {self.win_streak}"
        else:
            streak_emoji = "⚪"
            streak_text = "No streak"
        
        msg = f"<b>💰 RISK STATUS</b>\n\n"
        msg += f"Balance: ${status['balance']}\n"
        msg += f"{pnl_emoji} Daily P&L: {status['daily_pnl']:+.2f} ({status['daily_loss_pct']:.1f}%)\n"
        msg += f"{streak_emoji} {streak_text}\n"
        msg += f"Trades Today: {status['trades_today']}\n\n"
        
        if status["is_paused"]:
            msg += f"🚫 <b>PAUSED</b>\n{status['pause_reason']}"
        else:
            msg += f"✅ Trading Active\n"
            msg += f"Risk Limits: {self.max_consecutive_losses} losses, {self.max_daily_loss_pct}% daily"
        
        return msg


# Global risk manager instance
_risk_manager = None


def get_risk_manager(balance: float = 1000.0) -> RiskManager:
    """Get or create global risk manager."""
    global _risk_manager
    if _risk_manager is None:
        _risk_manager = RiskManager(balance)
    return _risk_manager


def check_trade_risk(pnl: float, symbol: str) -> bool:
    """
    Record a trade and check if bot should pause.
    
    Returns: True if trading should continue, False if should pause
    """
    rm = get_risk_manager()
    result = rm.record_trade(pnl, symbol)
    
    if result["should_pause"]:
        msg = f"⚠️ {result['reason']}\n\n{rm.format_for_telegram()}"
        try:
            notify_error("RISK_LIMIT_HIT", result["reason"])
        except:
            pass
        
        # Update bot status to paused
        bot_status["paused"] = True
        return False
    
    return True


def get_risk_status() -> dict:
    """Get current risk status."""
    rm = get_risk_manager()
    return rm.get_status()
