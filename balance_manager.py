# balance_manager.py — Balance management with caching and Bybit API integration

import threading
import time
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Import after load_dotenv
try:
    from trader import get_session
    from telegram_control_panel import get_config
except ImportError:
    print("  [balance] Warning: Could not import trader or telegram_control_panel")
    get_session = None
    get_config = None


# ─── BALANCE CACHE ───────────────────────────────────────────────

class BalanceCache:
    """Thread-safe in-memory cache for balance data with TTL support."""
    
    def __init__(self, ttl_seconds: int = 30):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl: int = ttl_seconds
        self.lock: threading.Lock = threading.Lock()
    
    def get(self, mode: str) -> Optional[Dict[str, Any]]:
        """Get cached balance data if not expired."""
        with self.lock:
            if mode not in self.cache:
                return None
            
            cache_entry = self.cache[mode]
            timestamp = cache_entry.get("timestamp", 0)
            current_time = time.time()
            
            if current_time - timestamp < self.ttl:
                return cache_entry.get("data")
            
            del self.cache[mode]
            return None
    
    def set(self, mode: str, data: Dict[str, Any]) -> None:
        """Store balance data with current timestamp."""
        with self.lock:
            self.cache[mode] = {
                "data": data,
                "timestamp": time.time()
            }
    
    def clear(self, mode: Optional[str] = None) -> None:
        """Clear cache for specific mode or all modes."""
        with self.lock:
            if mode is None:
                self.cache.clear()
            elif mode in self.cache:
                del self.cache[mode]
    
    def is_fresh(self, mode: str) -> bool:
        """Check if cached data exists and is within TTL."""
        with self.lock:
            if mode not in self.cache:
                return False
            
            cache_entry = self.cache[mode]
            timestamp = cache_entry.get("timestamp", 0)
            current_time = time.time()
            
            return current_time - timestamp < self.ttl


# Global cache instance
_balance_cache = BalanceCache(ttl_seconds=30)


def get_balance_cache() -> BalanceCache:
    """Get global balance cache instance."""
    return _balance_cache


# ─── DATA MODELS ─────────────────────────────────────────────────

@dataclass
class BalanceData:
    """Data model for account balance information."""
    total_equity: float
    available_balance: float
    usdt_balance: float
    coin_balances: Dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    mode: str = "DEMO"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_equity": self.total_equity,
            "available_balance": self.available_balance,
            "usdt_balance": self.usdt_balance,
            "coin_balances": self.coin_balances,
            "timestamp": self.timestamp,
            "mode": self.mode
        }
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any], mode: str = "DEMO") -> "BalanceData":
        """Create BalanceData from Bybit API response."""
        try:
            result = response.get("result", {})
            account_list = result.get("list", [])
            
            if not account_list:
                return cls(0.0, 0.0, 0.0, {}, time.time(), mode)
            
            account = account_list[0]
            total_equity = float(account.get("totalEquity", 0))
            available_balance = float(account.get("totalAvailableBalance", 0))
            
            # Parse coin balances
            coin_balances = {}
            for coin in account.get("coin", []):
                symbol = coin.get("coin", "")
                balance = float(coin.get("walletBalance", 0))
                if balance > 0:
                    coin_balances[symbol] = balance
            
            usdt_balance = coin_balances.get("USDT", 0.0)
            
            return cls(
                total_equity=total_equity,
                available_balance=available_balance,
                usdt_balance=usdt_balance,
                coin_balances=coin_balances,
                timestamp=time.time(),
                mode=mode
            )
        except Exception as e:
            print(f"  [balance] Error parsing API response: {e}")
            return cls(0.0, 0.0, 0.0, {}, time.time(), mode)


@dataclass
class BalanceCheckResult:
    """Result of balance sufficiency check."""
    is_sufficient: bool
    available_balance: float
    required_amount: float
    buffer_amount: float
    warning_message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_sufficient": self.is_sufficient,
            "available_balance": self.available_balance,
            "required_amount": self.required_amount,
            "buffer_amount": self.buffer_amount,
            "warning_message": self.warning_message
        }


# ─── BALANCE FETCHER ─────────────────────────────────────────────

class BalanceFetcher:
    """Fetches balance data from Bybit API with caching."""
    
    def __init__(self):
        self.cache = get_balance_cache()
    
    def get_balance(self, mode: str = None, force_refresh: bool = False) -> Optional[BalanceData]:
        """Get balance for specified mode (DEMO or REAL). Uses cache unless force_refresh=True."""
        if mode is None and get_config:
            config = get_config()
            mode = config.config.get("mode", "DEMO")
        elif mode is None:
            mode = "DEMO"
        
        # Check cache first
        if not force_refresh:
            cached_data = self.cache.get(mode)
            if cached_data:
                return BalanceData(**cached_data)
        
        # Fetch from API
        if not get_session:
            print("  [balance] Error: get_session not available")
            return None
        
        try:
            session = get_session()
            response = session.get_wallet_balance(
                accountType="UNIFIED",
                coin="USDT"
            )
            
            balance_data = BalanceData.from_api_response(response, mode)
            self.cache.set(mode, balance_data.to_dict())
            
            return balance_data
            
        except Exception as e:
            print(f"  [balance] Error fetching balance for {mode}: {e}")
            
            # Try to return expired cache as fallback
            cached_data = self.cache.get(mode)
            if cached_data:
                print(f"  [balance] Returning expired cache data")
                return BalanceData(**cached_data)
            
            return None
    
    def get_both_balances(self) -> Dict[str, Optional[BalanceData]]:
        """Fetch balances for both DEMO and REAL modes."""
        demo_balance = self.get_balance("DEMO")
        real_balance = self.get_balance("REAL")
        
        return {
            "DEMO": demo_balance,
            "REAL": real_balance
        }
    
    def check_sufficient_balance(self, required_amount: float, mode: str = None) -> BalanceCheckResult:
        """Check if available balance is sufficient for trade. Requires 10% buffer."""
        balance_data = self.get_balance(mode)
        
        if not balance_data:
            return BalanceCheckResult(
                is_sufficient=False,
                available_balance=0.0,
                required_amount=required_amount,
                buffer_amount=required_amount * 0.1,
                warning_message="Could not fetch balance from API"
            )
        
        buffer = required_amount * 0.1
        total_required = required_amount + buffer
        is_sufficient = balance_data.available_balance >= total_required
        
        warning = ""
        if not is_sufficient:
            shortage = total_required - balance_data.available_balance
            warning = f"Insufficient balance. Need ${total_required:.2f}, have ${balance_data.available_balance:.2f} (short ${shortage:.2f})"
        
        return BalanceCheckResult(
            is_sufficient=is_sufficient,
            available_balance=balance_data.available_balance,
            required_amount=required_amount,
            buffer_amount=buffer,
            warning_message=warning
        )


# ─── BALANCE FORMATTER ───────────────────────────────────────────

class BalanceFormatter:
    """Formats balance data for Telegram display."""
    
    @staticmethod
    def format_currency(amount: float, decimals: int = 2) -> str:
        """Format currency with comma separators."""
        return f"{amount:,.{decimals}f}"
    
    @staticmethod
    def get_balance_status_emoji(balance: float) -> str:
        """Get emoji indicator based on balance amount."""
        if balance > 100:
            return "🟢"
        elif balance >= 10:
            return "🟡"
        else:
            return "🔴"
    
    @staticmethod
    def format_display(balance_data: BalanceData) -> str:
        """Format balance data for single account display."""
        if not balance_data:
            return "❌ <b>Balance unavailable</b>"
        
        emoji = BalanceFormatter.get_balance_status_emoji(balance_data.usdt_balance)
        usdt_formatted = BalanceFormatter.format_currency(balance_data.usdt_balance)
        equity_formatted = BalanceFormatter.format_currency(balance_data.total_equity)
        available_formatted = BalanceFormatter.format_currency(balance_data.available_balance)
        
        timestamp = datetime.fromtimestamp(balance_data.timestamp).strftime("%H:%M:%S")
        
        msg = f"{emoji} <b>{balance_data.mode} ACCOUNT</b>\n\n"
        msg += f"<b>USDT Balance:</b> <code>${usdt_formatted}</code>\n"
        msg += f"<b>Total Equity:</b> <code>${equity_formatted}</code>\n"
        msg += f"<b>Available:</b> <code>${available_formatted}</code>\n\n"
        
        if balance_data.coin_balances:
            msg += "<b>Other Coins:</b>\n"
            for coin, amount in balance_data.coin_balances.items():
                if coin != "USDT" and amount > 0:
                    msg += f"  • {coin}: {BalanceFormatter.format_currency(amount, 4)}\n"
            msg += "\n"
        
        msg += f"<i>Updated: {timestamp}</i>"
        
        return msg
    
    @staticmethod
    def format_comparison(demo_balance: Optional[BalanceData], real_balance: Optional[BalanceData], current_mode: str) -> str:
        """Format side-by-side comparison of demo and real balances."""
        msg = "💰 <b>ACCOUNT COMPARISON</b>\n\n"
        
        # Demo account
        if demo_balance:
            demo_emoji = BalanceFormatter.get_balance_status_emoji(demo_balance.usdt_balance)
            demo_usdt = BalanceFormatter.format_currency(demo_balance.usdt_balance)
            active_marker = " ✅" if current_mode == "DEMO" else ""
            msg += f"{demo_emoji} <b>DEMO{active_marker}</b>\n"
            msg += f"  USDT: <code>${demo_usdt}</code>\n"
            msg += f"  Equity: <code>${BalanceFormatter.format_currency(demo_balance.total_equity)}</code>\n\n"
        else:
            msg += "🔴 <b>DEMO</b>\n  <i>Unavailable</i>\n\n"
        
        # Real account
        if real_balance:
            real_emoji = BalanceFormatter.get_balance_status_emoji(real_balance.usdt_balance)
            real_usdt = BalanceFormatter.format_currency(real_balance.usdt_balance)
            active_marker = " ✅" if current_mode == "REAL" else ""
            msg += f"{real_emoji} <b>REAL{active_marker}</b>\n"
            msg += f"  USDT: <code>${real_usdt}</code>\n"
            msg += f"  Equity: <code>${BalanceFormatter.format_currency(real_balance.total_equity)}</code>\n\n"
        else:
            msg += "🔴 <b>REAL</b>\n  <i>Unavailable</i>\n\n"
        
        msg += f"<i>Current mode: {current_mode}</i>"
        
        return msg


# Global fetcher instance
_balance_fetcher = None


def get_balance_fetcher() -> BalanceFetcher:
    """Get or create global balance fetcher instance."""
    global _balance_fetcher
    if _balance_fetcher is None:
        _balance_fetcher = BalanceFetcher()
    return _balance_fetcher
