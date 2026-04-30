# config.py — Bot settings and watchlist

# ─── PAIRS TO SCAN ───────────────────────────────────────────────
WATCHLIST = [
    "XAUUSDT",   # Gold
    "BTCUSDT",   # Bitcoin
    "ETHUSDT",   # Ethereum
    "BNBUSDT",   # BNB
    "SOLUSDT",   # Solana
    "XRPUSDT",   # XRP
    "ADAUSDT",   # Cardano
    "DOGEUSDT",  # Dogecoin
    "AVAXUSDT",  # Avalanche
    "DOTUSDT",   # Polkadot
    "MATICUSDT", # Polygon
    "LINKUSDT",  # Chainlink
    "UNIUSDT",   # Uniswap
    "LTCUSDT",   # Litecoin
    "ATOMUSDT",  # Cosmos
]

# ─── TRADING SETTINGS ────────────────────────────────────────────
SCAN_INTERVAL_SECONDS = 60        # How often to scan all pairs
MIN_CONFIDENCE_TO_TRADE = 75      # AI must be this % confident to place trade
TRAILING_STEP_PERCENT = 0.3       # Move SL every 0.3% price movement
INITIAL_STOP_LOSS_PERCENT = 1.0   # SL = 1% from entry
INITIAL_TAKE_PROFIT_PERCENT = 2.0 # TP = 2% from entry (trailing takes over)
TRADE_QUANTITY_USDT = 5.0         # Trade size in USDT (testnet)
LEVERAGE = 5                      # Leverage multiplier (keep low for safety)
HISTORY_LIMIT = 50                # How many past trades to feed AI

# ─── CANDLE SETTINGS ─────────────────────────────────────────────
CANDLE_INTERVAL = "15"            # 15-minute candles
CANDLE_LIMIT = 50                 # Last 50 candles for analysis
