# multi_timeframe.py — Analyze multiple timeframes, trade only when aligned

from ai_analyst import analyze_pair
from technical_indicators import analyze_indicators
from history import get_candles


def analyze_multi_timeframe(symbol: str) -> dict:
    """
    Analyzes a symbol across 3 timeframes: 5min, 15min, 1hour.
    Only returns a strong signal when 2+ timeframes AGREE.
    
    Returns: {
        'symbol': symbol,
        'signal': 'BUY' | 'SELL' | 'WAIT',
        'confidence': 0-100,
        'alignment': number of timeframes that agree (0-3),
        'timeframes': {
            '5m': { signal, confidence },
            '15m': { signal, confidence },
            '1h': { signal, confidence }
        },
        'reason': explanation of alignment
    }
    """
    print(f"  [MTF] Multi-timeframe analysis for {symbol}...")
    
    timeframes = ["5", "15", "60"]  # 5min, 15min, 1hour
    results = {}
    signals = []
    confidences = []
    
    # Analyze each timeframe
    for tf in timeframes:
        try:
            analysis = analyze_pair(symbol, interval=tf)
            signal = analysis.get("signal", "WAIT")
            confidence = analysis.get("confidence", 0)
            
            results[f"{tf}m"] = {
                "signal": signal,
                "confidence": confidence,
                "reason": analysis.get("reason", "")
            }
            
            if signal in ["BUY", "SELL"]:
                signals.append(signal)
                confidences.append(confidence)
            
            print(f"    {tf}m: {signal} ({confidence}%)")
            
        except Exception as e:
            print(f"    {tf}m: Error - {e}")
            results[f"{tf}m"] = {
                "signal": "WAIT",
                "confidence": 0,
                "reason": f"Error: {e}"
            }
    
    # Determine alignment
    alignment = 0
    final_signal = "WAIT"
    reason = ""
    
    # Check if signals align
    if len(signals) == 0:
        alignment = 0
        final_signal = "WAIT"
        reason = "No timeframe has a clear signal"
    
    elif len(set(signals)) == 1:  # All signals are the same
        alignment = len(signals)
        final_signal = signals[0]
        confidence_avg = sum(confidences) / len(confidences)
        reason = f"All {alignment} timeframes AGREE on {final_signal} (avg {confidence_avg:.0f}% confidence)"
    
    elif len(signals) >= 2:
        # Check if at least 2 timeframes agree
        buy_count = signals.count("BUY")
        sell_count = signals.count("SELL")
        
        if buy_count >= 2:
            alignment = buy_count
            final_signal = "BUY"
            confidence_avg = sum([c for s, c in zip(signals, confidences) if s == "BUY"]) / buy_count
            reason = f"{buy_count} timeframes AGREE on BUY (avg {confidence_avg:.0f}% confidence)"
        
        elif sell_count >= 2:
            alignment = sell_count
            final_signal = "SELL"
            confidence_avg = sum([c for s, c in zip(signals, confidences) if s == "SELL"]) / sell_count
            reason = f"{sell_count} timeframes AGREE on SELL (avg {confidence_avg:.0f}% confidence)"
        
        else:
            alignment = 1
            final_signal = "WAIT"
            reason = "Only 1 timeframe has a signal (need 2+ for confirmation)"
    
    else:
        alignment = 0
        final_signal = "WAIT"
        reason = "No sufficient alignment across timeframes"
    
    # Calculate final confidence (highest from aligned signals)
    final_confidence = max(confidences) if confidences else 0
    
    # Reduce confidence if not all 3 timeframes agree
    if alignment < 3:
        final_confidence = max(0, final_confidence - (3 - alignment) * 10)
    
    return {
        "symbol": symbol,
        "signal": final_signal,
        "confidence": int(final_confidence),
        "alignment": alignment,
        "timeframes": results,
        "reason": reason
    }


def format_mtf_for_telegram(analysis: dict) -> str:
    """Format multi-timeframe analysis for Telegram display."""
    alignment_emoji = {
        0: "⚪",
        1: "🟡",
        2: "🟢",
        3: "🟢✅"
    }
    
    emoji = alignment_emoji.get(analysis["alignment"], "⚪")
    
    msg = f"{emoji} <b>MULTI-TIMEFRAME ANALYSIS</b>\n"
    msg += f"Symbol: {analysis['symbol']}\n"
    msg += f"Signal: <b>{analysis['signal']}</b>\n"
    msg += f"Alignment: {analysis['alignment']}/3 timeframes\n"
    msg += f"Confidence: {analysis['confidence']}%\n\n"
    
    msg += "<b>Timeframe Details:</b>\n"
    for tf_name, tf_data in analysis["timeframes"].items():
        signal_emoji = "🔵" if tf_data["signal"] == "BUY" else "🔴" if tf_data["signal"] == "SELL" else "⚪"
        msg += f"{signal_emoji} {tf_name}: {tf_data['signal']} ({tf_data['confidence']}%)\n"
    
    msg += f"\n<i>{analysis['reason']}</i>"
    
    return msg
