# telegram_control_panel.py — Easy controls via Telegram for trading config

import json
import os
from datetime import datetime
from dotenv import load_dotenv, set_key

load_dotenv()

CONFIG_FILE = "trading_config.json"
ENV_FILE = ".env"


class TradingConfig:
    """Manage trading configuration via Telegram."""
    
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """Load config from file or create defaults."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        
        # Create defaults
        return {
            "mode": "DEMO",  # DEMO or REAL
            "trade_amount": 0.5,
            "leverage": 5,
            "stop_loss_pct": 1.0,
            "take_profit_pct": 2.0,
            "max_consecutive_losses": 3,
            "max_daily_loss_pct": 5.0,
            "demo_api_key": os.getenv("BYBIT_API_KEY", ""),
            "demo_api_secret": os.getenv("BYBIT_API_SECRET", ""),
            "real_api_key": "",
            "real_api_secret": "",
            "last_updated": datetime.now().isoformat()
        }
    
    def save_config(self):
        """Save config to file."""
        self.config["last_updated"] = datetime.now().isoformat()
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def set_mode(self, mode: str) -> bool:
        """Switch between DEMO and REAL mode."""
        if mode.upper() not in ["DEMO", "REAL"]:
            return False
        
        self.config["mode"] = mode.upper()
        self.save_config()
        
        # Clear session cache to force recreation with new mode
        try:
            from bybit_session import clear_session_cache
            clear_session_cache()
            print(f"  [config] Switched to {mode.upper()} mode")
        except ImportError:
            print("  [config] Warning: Could not clear session cache")
        
        # Update .env (legacy support)
        if mode.upper() == "DEMO":
            key = self.config.get("demo_api_key", "")
            secret = self.config.get("demo_api_secret", "")
            testnet = "True"
        else:
            key = self.config.get("real_api_key", "")
            secret = self.config.get("real_api_secret", "")
            testnet = "False"
        
        if key and secret:
            set_key(ENV_FILE, "BYBIT_API_KEY", key)
            set_key(ENV_FILE, "BYBIT_API_SECRET", secret)
            set_key(ENV_FILE, "BYBIT_TESTNET", testnet)
        
        return True
    
    def set_trade_amount(self, amount: float) -> bool:
        """Set trade amount in USDT."""
        if amount <= 0 or amount > 100:
            return False
        
        self.config["trade_amount"] = amount
        self.save_config()
        
        # Update config.py
        self.update_python_config()
        
        return True
    
    def set_leverage(self, leverage: int) -> bool:
        """Set leverage multiplier (1-10)."""
        if leverage < 1 or leverage > 10:
            return False
        
        self.config["leverage"] = leverage
        self.save_config()
        self.update_python_config()
        
        return True
    
    def set_demo_keys(self, api_key: str, api_secret: str):
        """Store demo API keys."""
        self.config["demo_api_key"] = api_key
        self.config["demo_api_secret"] = api_secret
        self.save_config()
    
    def set_real_keys(self, api_key: str, api_secret: str):
        """Store real API keys."""
        self.config["real_api_key"] = api_key
        self.config["real_api_secret"] = api_secret
        self.save_config()
    
    def update_python_config(self):
        """Update config.py with new values."""
        try:
            config_file = "config.py"
            if not os.path.exists(config_file):
                return
            
            with open(config_file, "r") as f:
                content = f.read()
            
            # Update TRADE_QUANTITY_USDT
            content = self.replace_config_value(
                content, 
                "TRADE_QUANTITY_USDT",
                self.config["trade_amount"]
            )
            
            # Update LEVERAGE
            content = self.replace_config_value(
                content,
                "LEVERAGE",
                self.config["leverage"]
            )
            
            with open(config_file, "w") as f:
                f.write(content)
        except Exception as e:
            print(f"  [config] Could not update config.py: {e}")
    
    def replace_config_value(self, content: str, key: str, value) -> str:
        """Replace a config value in Python file."""
        import re
        pattern = rf'{key}\s*=\s*[\d.]+'
        replacement = f'{key} = {value}'
        return re.sub(pattern, replacement, content)
    
    def get_status(self) -> dict:
        """Get current config status."""
        return {
            "mode": self.config["mode"],
            "trade_amount": self.config["trade_amount"],
            "leverage": self.config["leverage"],
            "stop_loss": self.config["stop_loss_pct"],
            "take_profit": self.config["take_profit_pct"],
            "max_losses": self.config["max_consecutive_losses"],
            "max_daily_loss": self.config["max_daily_loss_pct"]
        }


# Global config instance
_config = None


def get_config() -> TradingConfig:
    """Get or create global config."""
    global _config
    if _config is None:
        _config = TradingConfig()
    return _config
