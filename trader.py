# trader.py — Places and closes trades on Bybit

from pybit.unified_trading import HTTP
from config import (
    TRADE_QUANTITY_USDT,
    LEVERAGE,
    INITIAL_STOP_LOSS_PERCENT,
    INITIAL_TAKE_PROFIT_PERCENT
)
from history import get_current_price
import os
from dotenv import load_dotenv

load_dotenv()


def get_session():
    """Create Bybit API session with correct configuration."""
    testnet = os.getenv("BYBIT_TESTNET", "False").lower() == "true"
    api_key = os.getenv("BYBIT_API_KEY")
    api_secret = os.getenv("BYBIT_API_SECRET")
    
    if not api_key or not api_secret:
        raise ValueError("BYBIT_API_KEY and BYBIT_API_SECRET must be set in .env")
    
    return HTTP(
        testnet=testnet,
        api_key=api_key,
        api_secret=api_secret,
    )


def set_leverage(symbol: str):
    try:
        session = get_session()
        session.set_leverage(
            category="linear",
            symbol=symbol,
            buyLeverage=str(LEVERAGE),
            sellLeverage=str(LEVERAGE),
        )
    except Exception as e:
        print(f"  [trader] Leverage already set or error: {e}")


def get_quantity(symbol: str, price: float) -> float:
    """Calculate trade quantity based on USDT amount and leverage."""
    raw_qty = (TRADE_QUANTITY_USDT * LEVERAGE) / price

    # Round to reasonable decimal places
    if price > 1000:
        return round(raw_qty, 3)
    elif price > 1:
        return round(raw_qty, 2)
    else:
        return round(raw_qty, 0)


def place_trade(symbol: str, signal: str) -> dict | None:
    """
    Places a BUY or SELL trade on Bybit.
    Returns trade details if successful, None if failed.
    """
    try:
        session = get_session()
        set_leverage(symbol)

        price = get_current_price(symbol)
        if price == 0:
            print(f"  [trader] Could not get price for {symbol}")
            return None

        qty = get_quantity(symbol, price)
        side = "Buy" if signal == "BUY" else "Sell"

        # Calculate SL and TP
        sl_pct = INITIAL_STOP_LOSS_PERCENT / 100
        tp_pct = INITIAL_TAKE_PROFIT_PERCENT / 100

        if side == "Buy":
            stop_loss = round(price * (1 - sl_pct), 2)
            take_profit = round(price * (1 + tp_pct), 2)
        else:
            stop_loss = round(price * (1 + sl_pct), 2)
            take_profit = round(price * (1 - tp_pct), 2)

        print(f"  [trader] Placing {side} on {symbol}")
        print(f"  [trader] Entry: {price} | SL: {stop_loss} | TP: {take_profit} | Qty: {qty}")

        response = session.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=str(qty),
            stopLoss=str(stop_loss),
            takeProfit=str(take_profit),
            timeInForce="IOC",
        )

        order_id = response["result"].get("orderId", "unknown")
        print(f"  [trader] ✅ Order placed! ID: {order_id}")

        return {
            "symbol": symbol,
            "side": side,
            "entry_price": price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "quantity": qty,
            "order_id": order_id,
        }

    except Exception as e:
        print(f"  [trader] ❌ Failed to place trade: {e}")
        return None


def close_trade(symbol: str, side: str, quantity: float) -> bool:
    """Closes an open position manually."""
    try:
        session = get_session()
        close_side = "Sell" if side == "Buy" else "Buy"

        session.place_order(
            category="linear",
            symbol=symbol,
            side=close_side,
            orderType="Market",
            qty=str(quantity),
            reduceOnly=True,
            timeInForce="IOC",
        )

        print(f"  [trader] ✅ Position closed for {symbol}")
        return True

    except Exception as e:
        print(f"  [trader] ❌ Failed to close trade: {e}")
        return False


def get_open_position(symbol: str) -> dict | None:
    """Returns current open position for a symbol, or None."""
    try:
        session = get_session()
        response = session.get_positions(category="linear", symbol=symbol)
        positions = response.get("result", {}).get("list", [])

        for pos in positions:
            size = float(pos.get("size", 0))
            if size > 0:
                return {
                    "symbol": symbol,
                    "side": pos.get("side"),
                    "size": size,
                    "entry_price": float(pos.get("avgPrice", 0)),
                    "unrealised_pnl": float(pos.get("unrealisedPnl", 0)),
                    "stop_loss": float(pos.get("stopLoss", 0)),
                }
        return None

    except Exception as e:
        print(f"  [trader] Error checking position: {e}")
        return None


def update_stop_loss(symbol: str, side: str, new_sl: float) -> bool:
    """Updates the stop loss of an open position."""
    try:
        session = get_session()
        session.set_trading_stop(
            category="linear",
            symbol=symbol,
            stopLoss=str(round(new_sl, 2)),
            positionIdx=0 if side == "Buy" else 1,
        )
        return True
    except Exception as e:
        print(f"  [trailing] SL update failed: {e}")
        return False
