# history.py — Fetches past trade history from Bybit

from pybit.unified_trading import HTTP
from config import HISTORY_LIMIT
import os
from dotenv import load_dotenv

load_dotenv()

def get_session():
    return HTTP(
        testnet=os.getenv("BYBIT_TESTNET", "True") == "True",
        api_key=os.getenv("BYBIT_API_KEY"),
        api_secret=os.getenv("BYBIT_API_SECRET"),
    )

def get_trade_history(symbol: str) -> str:
    """
    Fetches last N closed trades for a symbol from Bybit.
    Returns a readable text summary for AI analysis.
    """
    try:
        session = get_session()
        response = session.get_closed_pnl(
            category="linear",
            symbol=symbol,
            limit=HISTORY_LIMIT
        )

        trades = response.get("result", {}).get("list", [])

        if not trades:
            return f"No previous trade history found for {symbol}."

        summary_lines = [f"Last {len(trades)} closed trades for {symbol}:\n"]

        wins = 0
        losses = 0

        for i, trade in enumerate(trades, 1):
            side = trade.get("side", "Unknown")
            entry = float(trade.get("avgEntryPrice", 0))
            exit_price = float(trade.get("avgExitPrice", 0))
            pnl = float(trade.get("closedPnl", 0))
            result = "WIN ✅" if pnl > 0 else "LOSS ❌"

            if pnl > 0:
                wins += 1
            else:
                losses += 1

            summary_lines.append(
                f"Trade {i}: {side} | Entry: {entry} | Exit: {exit_price} | PnL: {pnl:.4f} USDT | {result}"
            )

        total = wins + losses
        win_rate = (wins / total * 100) if total > 0 else 0
        summary_lines.append(f"\nWin Rate: {win_rate:.1f}% ({wins}W / {losses}L)")

        return "\n".join(summary_lines)

    except Exception as e:
        return f"Could not fetch trade history for {symbol}: {str(e)}"


def get_candles(symbol: str, interval: str = "15", limit: int = 50) -> str:
    """
    Fetches recent candlestick data for a symbol.
    Returns readable text for AI analysis.
    """
    try:
        session = get_session()
        response = session.get_kline(
            category="linear",
            symbol=symbol,
            interval=interval,
            limit=limit
        )

        candles = response.get("result", {}).get("list", [])

        if not candles:
            return f"No candle data found for {symbol}."

        lines = [f"Last {len(candles)} candles ({interval}min) for {symbol}:\n"]
        lines.append("Format: [Open, High, Low, Close, Volume]\n")

        for candle in candles[-10:]:  # Show last 10 to save tokens
            timestamp, open_, high, low, close, volume, _ = candle
            lines.append(f"O:{open_} H:{high} L:{low} C:{close} V:{volume}")

        latest = candles[0]
        lines.append(f"\nLatest Close Price: {latest[4]}")

        return "\n".join(lines)

    except Exception as e:
        return f"Could not fetch candles for {symbol}: {str(e)}"


def get_current_price(symbol: str) -> float:
    """Returns the current market price for a symbol."""
    try:
        session = get_session()
        response = session.get_tickers(category="linear", symbol=symbol)
        price = float(response["result"]["list"][0]["lastPrice"])
        return price
    except Exception as e:
        print(f"[history] Error fetching price for {symbol}: {e}")
        return 0.0
