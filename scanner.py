# scanner.py — Scans all pairs and picks the best signal (with multi-timeframe)

from config import WATCHLIST, MIN_CONFIDENCE_TO_TRADE
from multi_timeframe import analyze_multi_timeframe
from strategy_rag import get_strategy_context


def scan_all_pairs() -> dict | None:
    """
    Scans every pair in the watchlist using multi-timeframe analysis.
    Returns the highest confidence signal that meets the minimum threshold.
    
    Multi-timeframe rule: Only trades when 2+ timeframes agree.
    Returns None if no qualifying signal found.
    """
    print(f"\n🔍 Scanning {len(WATCHLIST)} pairs (Multi-Timeframe)...")
    print("─" * 50)

    results = []

    for symbol in WATCHLIST:
        analysis = analyze_multi_timeframe(symbol)
        signal = analysis.get("signal", "WAIT")
        confidence = analysis.get("confidence", 0)
        alignment = analysis.get("alignment", 0)

        # Only consider signals with 2+ timeframe alignment
        if signal != "WAIT" and alignment >= 2:
            status = "✅"
        else:
            status = "⏳"
        
        print(f"  {status} {symbol}: {signal} | {alignment}/3 timeframes | Confidence: {confidence}%")

        if signal in ["BUY", "SELL"] and alignment >= 2:
            results.append(analysis)

    print("─" * 50)

    if not results:
        print("  No multi-timeframe aligned signals. Waiting for next scan...\n")
        return None

    # Sort by confidence — highest wins
    results.sort(key=lambda x: x["confidence"], reverse=True)
    best = results[0]

    if best["confidence"] < MIN_CONFIDENCE_TO_TRADE:
        print(f"  Best signal ({best['symbol']}) only {best['confidence']}% confidence — below {MIN_CONFIDENCE_TO_TRADE}% threshold. Skipping.\n")
        return None

    print(f"\n🏆 BEST SIGNAL: {best['symbol']} | {best['signal']} | {best['alignment']}/3 timeframes aligned | {best['confidence']}% confidence")
    print(f"   Reason: {best['reason']}\n")

    return best
