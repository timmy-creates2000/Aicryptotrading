# technical_indicators.py — Calculate RSI, EMA, MACD, ATR, Volume for better signals

import numpy as np
from typing import list, dict


def calculate_sma(prices: list, period: int) -> list:
    """Calculate Simple Moving Average."""
    sma = []
    for i in range(len(prices)):
        if i < period - 1:
            sma.append(None)
        else:
            sma.append(sum(prices[i-period+1:i+1]) / period)
    return sma


def calculate_ema(prices: list, period: int) -> list:
    """Calculate Exponential Moving Average."""
    ema = []
    multiplier = 2 / (period + 1)
    
    for i in range(len(prices)):
        if i < period - 1:
            ema.append(None)
        elif i == period - 1:
            ema.append(sum(prices[0:period]) / period)
        else:
            ema.append((prices[i] * multiplier) + (ema[i-1] * (1 - multiplier)))
    
    return ema


def calculate_rsi(prices: list, period: int = 14) -> float:
    """
    Calculate RSI (Relative Strength Index).
    Returns current RSI value (0-100).
    """
    if len(prices) < period:
        return 50.0  # Neutral if not enough data
    
    gains = []
    losses = []
    
    # Calculate gains and losses
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    # Average gains and losses
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)


def calculate_macd(prices: list) -> dict:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    Returns: {
        'macd': current MACD value,
        'signal': signal line,
        'histogram': MACD - Signal,
        'trend': 'BULLISH' | 'BEARISH' | 'NEUTRAL'
    }
    """
    if len(prices) < 26:
        return {"macd": 0, "signal": 0, "histogram": 0, "trend": "NEUTRAL"}
    
    # Calculate EMAs
    ema_12 = calculate_ema(prices, 12)
    ema_26 = calculate_ema(prices, 26)
    
    # Calculate MACD line
    macd_line = []
    for i in range(len(prices)):
        if ema_12[i] is not None and ema_26[i] is not None:
            macd_line.append(ema_12[i] - ema_26[i])
        else:
            macd_line.append(None)
    
    # Calculate signal line (9-period EMA of MACD)
    macd_values = [v for v in macd_line if v is not None]
    signal_line = calculate_ema(macd_values, 9)
    
    current_macd = macd_line[-1] if macd_line[-1] is not None else 0
    current_signal = signal_line[-1] if signal_line[-1] is not None else 0
    histogram = current_macd - current_signal
    
    # Determine trend
    if histogram > 0:
        trend = "BULLISH"
    elif histogram < 0:
        trend = "BEARISH"
    else:
        trend = "NEUTRAL"
    
    return {
        "macd": round(current_macd, 6),
        "signal": round(current_signal, 6),
        "histogram": round(histogram, 6),
        "trend": trend
    }


def calculate_atr(high: list, low: list, close: list, period: int = 14) -> float:
    """
    Calculate ATR (Average True Range).
    High, low, close should be lists of same length.
    Returns current ATR value.
    """
    if len(high) < period or len(low) < period or len(close) < period:
        return 0.0
    
    true_ranges = []
    
    for i in range(len(close)):
        if i == 0:
            tr = high[i] - low[i]
        else:
            tr = max(
                high[i] - low[i],
                abs(high[i] - close[i-1]),
                abs(low[i] - close[i-1])
            )
        true_ranges.append(tr)
    
    atr = sum(true_ranges[-period:]) / period
    return round(atr, 2)


def calculate_volume_trend(volumes: list, period: int = 20) -> dict:
    """
    Analyze volume trends.
    Returns: {
        'current_volume': latest volume,
        'average_volume': average over period,
        'volume_ratio': current / average,
        'trend': 'HIGH' | 'NORMAL' | 'LOW'
    }
    """
    if len(volumes) == 0:
        return {
            "current_volume": 0,
            "average_volume": 0,
            "volume_ratio": 1.0,
            "trend": "NORMAL"
        }
    
    current = volumes[-1]
    avg = sum(volumes[-period:]) / min(period, len(volumes))
    ratio = current / avg if avg > 0 else 1.0
    
    if ratio > 1.5:
        trend = "HIGH"
    elif ratio < 0.7:
        trend = "LOW"
    else:
        trend = "NORMAL"
    
    return {
        "current_volume": int(current),
        "average_volume": int(avg),
        "volume_ratio": round(ratio, 2),
        "trend": trend
    }


def analyze_indicators(candles: list) -> dict:
    """
    Comprehensive technical analysis from candle data.
    
    Input: candles list from history.get_candles()
    Each candle: [timestamp, open, high, low, close, volume, ...]
    
    Returns full indicator analysis dict
    """
    if not candles or len(candles) < 26:
        return {
            "rsi": 50,
            "rsi_signal": "NEUTRAL",
            "macd": {"macd": 0, "signal": 0, "histogram": 0, "trend": "NEUTRAL"},
            "atr": 0,
            "volume": {"trend": "NORMAL", "volume_ratio": 1.0},
            "ema_9": None,
            "ema_21": None,
            "price_vs_ema": "NEUTRAL"
        }
    
    # Extract OHLCV data
    closes = [float(c[4]) for c in candles]
    highs = [float(c[2]) for c in candles]
    lows = [float(c[3]) for c in candles]
    volumes = [float(c[5]) if len(c) > 5 else 0 for c in candles]
    
    # Calculate indicators
    rsi = calculate_rsi(closes, 14)
    macd_data = calculate_macd(closes)
    atr = calculate_atr(highs, lows, closes, 14)
    volume_data = calculate_volume_trend(volumes, 20)
    
    # Calculate EMAs
    ema_9_list = calculate_ema(closes, 9)
    ema_21_list = calculate_ema(closes, 21)
    
    ema_9 = ema_9_list[-1] if ema_9_list[-1] is not None else None
    ema_21 = ema_21_list[-1] if ema_21_list[-1] is not None else None
    current_price = closes[-1]
    
    # Price position relative to EMAs
    if ema_9 and ema_21:
        if current_price > ema_9 > ema_21:
            price_vs_ema = "STRONGLY_BULLISH"
        elif current_price > ema_21:
            price_vs_ema = "BULLISH"
        elif current_price < ema_9 < ema_21:
            price_vs_ema = "STRONGLY_BEARISH"
        elif current_price < ema_21:
            price_vs_ema = "BEARISH"
        else:
            price_vs_ema = "NEUTRAL"
    else:
        price_vs_ema = "NEUTRAL"
    
    # RSI signal
    if rsi > 70:
        rsi_signal = "OVERBOUGHT"
    elif rsi < 30:
        rsi_signal = "OVERSOLD"
    elif rsi > 55:
        rsi_signal = "BULLISH"
    elif rsi < 45:
        rsi_signal = "BEARISH"
    else:
        rsi_signal = "NEUTRAL"
    
    return {
        "rsi": rsi,
        "rsi_signal": rsi_signal,
        "macd": macd_data,
        "atr": atr,
        "volume": volume_data,
        "ema_9": round(ema_9, 2) if ema_9 else None,
        "ema_21": round(ema_21, 2) if ema_21 else None,
        "price_vs_ema": price_vs_ema,
        "current_price": round(current_price, 2)
    }


def format_indicators_for_ai(analysis: dict) -> str:
    """Format indicators as readable text for AI analysis."""
    msg = "📊 TECHNICAL INDICATORS:\n"
    msg += f"Price: {analysis['current_price']}\n"
    msg += f"RSI(14): {analysis['rsi']} → {analysis['rsi_signal']}\n"
    msg += f"EMA 9/21: {analysis['ema_9']} / {analysis['ema_21']} → {analysis['price_vs_ema']}\n"
    msg += f"MACD: {analysis['macd']['macd']:.6f} Signal: {analysis['macd']['signal']:.6f} → {analysis['macd']['trend']}\n"
    msg += f"ATR(14): {analysis['atr']}\n"
    msg += f"Volume: {analysis['volume']['volume_ratio']}x average → {analysis['volume']['trend']}\n"
    
    return msg
