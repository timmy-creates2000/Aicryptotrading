# ai_analyst.py — Gemini AI signal analysis with technical indicators

import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from history import get_trade_history, get_candles, get_candles_raw
from technical_indicators import analyze_indicators, format_indicators_for_ai
from strategy_rag import get_strategy_context

load_dotenv()

# Validate Gemini API key at startup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY or len(GEMINI_API_KEY) < 20:
    raise ValueError(
        "GEMINI_API_KEY is missing or invalid in .env file. "
        "Get your key from https://aistudio.google.com/app/apikey"
    )

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def analyze_pair(symbol: str, interval: str = "15") -> dict:
    """
    Analyzes a trading pair using:
    - Past trade history
    - Candlestick data
    - Technical indicators (RSI, MACD, EMA, ATR, Volume)
    
    Returns: {signal, confidence, reason, indicators}
    """
    print(f"  [AI] Analyzing {symbol} ({interval}min)...")

    trade_history = get_trade_history(symbol)
    candle_data = get_candles(symbol, interval=interval)
    
    # Get raw candles for indicator calculation (not text)
    candles_raw = get_candles_raw(symbol, interval=interval)
    
    # Calculate technical indicators
    indicators_text = ""
    if candles_raw and len(candles_raw) > 0:
        try:
            indicators = analyze_indicators(candles_raw)
            indicators_text = format_indicators_for_ai(indicators)
        except Exception as e:
            print(f"  [AI] Could not calculate indicators: {e}")
            indicators_text = "Technical indicators: Not available"
    else:
        indicators_text = "Technical indicators: Not available"
    
    # Get strategy context (RAG)
    strategy_context = get_strategy_context()

    prompt = f"""
You are an expert crypto trading AI with deep knowledge of technical analysis.
Analyze the following data for {symbol} and provide a trading signal.

{strategy_context}

=== PAST TRADE HISTORY ===
{trade_history}

=== TECHNICAL INDICATORS (15-minute) ===
{indicators_text}

=== RECENT CANDLESTICK DATA ===
{candle_data}

=== ANALYSIS INSTRUCTIONS ===
1. Use RSI to confirm overbought/oversold conditions
2. Use MACD histogram to confirm trend direction
3. Use EMA crossovers to confirm momentum
4. Use ATR for volatility assessment
5. Use Volume to confirm price breakouts
6. Cross-reference with past winning patterns

Trading Rules:
- Only BUY if RSI < 70 AND MACD is bullish AND Price > EMA21
- Only SELL if RSI > 30 AND MACD is bearish AND Price < EMA21
- Ignore signals if volume is LOW
- Be conservative: prefer WAIT over risky signals

Respond ONLY with a valid JSON object (no extra text):
{{
  "signal": "BUY" or "SELL" or "WAIT",
  "confidence": <0-100>,
  "reason": "<brief explanation referencing indicators>",
  "entry_note": "<specific price level or condition>"
}}
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Clean up markdown
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)

        # Validate required fields
        result["symbol"] = symbol
        result["confidence"] = int(result.get("confidence", 0))
        result["signal"] = result.get("signal", "WAIT").upper()
        result["interval"] = interval

        return result

    except json.JSONDecodeError:
        print(f"  [AI] JSON parse error for {symbol}")
        return {
            "symbol": symbol,
            "signal": "WAIT",
            "confidence": 0,
            "reason": "AI response parsing failed",
            "interval": interval
        }
    except Exception as e:
        print(f"  [AI] Error analyzing {symbol}: {e}")
        return {
            "symbol": symbol,
            "signal": "WAIT",
            "confidence": 0,
            "reason": f"Analysis error: {str(e)}",
            "interval": interval
        }
