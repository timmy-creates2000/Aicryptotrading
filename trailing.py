# trailing.py — Advanced trailing stop loss manager with trend analysis

import time
from datetime import datetime
from collections import deque
from config import TRAILING_STEP_PERCENT
from history import get_current_price
from trader import update_stop_loss, get_open_position
from telegram_bot import notify_trade_update


def calculate_trend_strength(price_history: deque) -> dict:
    """
    Analyzes price history to determine trend strength and direction.
    
    Returns:
        {
            "trend_direction": "UP" | "DOWN" | "SIDEWAYS",
            "momentum": float (0-1, higher = stronger),
            "volatility": float (0-1, higher = more volatile),
            "slope": float (average price change)
        }
    """
    if len(price_history) < 3:
        return {"trend_direction": "UNKNOWN", "momentum": 0, "volatility": 0, "slope": 0}
    
    prices = list(price_history)
    
    # Calculate slope (momentum)
    changes = []
    for i in range(1, len(prices)):
        change_pct = (prices[i] - prices[i-1]) / prices[i-1] if prices[i-1] != 0 else 0
        changes.append(change_pct)
    
    avg_change = sum(changes) / len(changes) if changes else 0
    momentum = min(abs(avg_change) * 1000, 1)  # Normalize to 0-1
    
    # Calculate volatility (standard deviation)
    if len(changes) > 1:
        variance = sum((x - avg_change) ** 2 for x in changes) / len(changes)
        volatility = min((variance ** 0.5) * 100, 1)  # Normalize
    else:
        volatility = 0
    
    # Determine trend direction
    if avg_change > 0.0001:
        trend_direction = "UP"
    elif avg_change < -0.0001:
        trend_direction = "DOWN"
    else:
        trend_direction = "SIDEWAYS"
    
    return {
        "trend_direction": trend_direction,
        "momentum": momentum,
        "volatility": volatility,
        "slope": avg_change
    }


def get_adaptive_step(trend: dict, side: str, volatility: float) -> float:
    """
    Adjusts trailing step percentage based on trend strength and volatility.
    
    - Strong uptrend (BUY): Tighter SL to protect more profit
    - Weak/sideways: Normal step
    - High volatility: Looser SL to avoid whipsaws
    """
    base_step = TRAILING_STEP_PERCENT / 100
    
    # Adjust for volatility (high volatility = looser SL)
    volatility_adjustment = 1 + (volatility * 0.5)
    
    # Adjust for trend strength
    if trend["trend_direction"] == "UP" and side == "Buy":
        trend_adjustment = 0.8  # Tighter on strong uptrend
    elif trend["trend_direction"] == "DOWN" and side == "Sell":
        trend_adjustment = 0.8  # Tighter on strong downtrend
    else:
        trend_adjustment = 1.0  # Normal
    
    return base_step * volatility_adjustment * trend_adjustment


def manage_trailing_stop(trade: dict, notify_callback=None) -> dict:
    """
    Advanced trailing stop manager with trend analysis.
    Monitors open trade, moves SL intelligently based on trend strength.

    trade: dict with symbol, side, entry_price, stop_loss, quantity, order_id
    notify_callback: function to send Telegram alerts
    Returns final trade summary dict.
    """

    symbol = trade["symbol"]
    side = trade["side"]
    entry_price = trade["entry_price"]
    current_sl = trade["stop_loss"]
    
    best_price = entry_price
    locked_profit = 0.0
    
    # Price history for trend analysis (last 24 checks = 4 mins)
    price_history = deque(maxlen=24)
    price_history.append(entry_price)
    
    # Error tracking
    consecutive_errors = 0
    max_consecutive_errors = 5
    iteration_count = 0
    
    # Logging
    start_time = datetime.now()
    sl_update_count = 0
    
    print(f"\n📊 TRAILING STOP STARTED — {symbol}")
    print(f"   Side: {side} | Entry: {entry_price} | Initial SL: {current_sl}")
    print(f"   Quantity: {trade['quantity']} | Order ID: {trade.get('order_id', 'N/A')}")
    print(f"   Start time: {start_time.strftime('%H:%M:%S')}")

    while True:
        time.sleep(10)  # Check every 10 seconds
        iteration_count += 1

        # ─── POSITION CHECK ───────────────────────────────────────────
        try:
            position = get_open_position(symbol)
            if position is None:
                consecutive_errors += 1
                if consecutive_errors > max_consecutive_errors:
                    print(f"\n⚠️  Max errors ({max_consecutive_errors}) reached. Exiting trailing.")
                    break
                print(f"  [trailing] Position check failed ({consecutive_errors}/{max_consecutive_errors}). Retrying...")
                continue
            
            consecutive_errors = 0  # Reset on success
            unrealised_pnl = position.get("unrealised_pnl", 0)
            
        except Exception as e:
            print(f"  [trailing] ❌ Error checking position: {e}")
            consecutive_errors += 1
            if consecutive_errors > max_consecutive_errors:
                print(f"\n⚠️  Max errors ({max_consecutive_errors}) reached. Exiting trailing.")
                break
            continue

        # ─── PRICE CHECK ───────────────────────────────────────────
        try:
            current_price = get_current_price(symbol)
            
            # Validate price
            if current_price <= 0:
                print(f"  [trailing] ⚠️  Invalid price ({current_price}). Skipping iteration.")
                continue
                
            price_history.append(current_price)
            
        except Exception as e:
            print(f"  [trailing] ❌ Error getting price: {e}")
            continue

        # ─── TREND ANALYSIS ───────────────────────────────────────────
        trend = calculate_trend_strength(price_history)
        adaptive_step = get_adaptive_step(trend, side, trend["volatility"])
        
        # Debug info every 6 iterations (60 seconds)
        if iteration_count % 6 == 0:
            print(f"  [trend] {trend['trend_direction']} | Momentum: {trend['momentum']:.2f} | "
                  f"Volatility: {trend['volatility']:.2f} | Adaptive Step: {adaptive_step*100:.2f}%")
            print(f"  [trade] Price: {current_price} | PnL: {unrealised_pnl:.2f} USDT")

        # ─── TRAILING LOGIC ───────────────────────────────────────────
        if side == "Buy":
            # For BUY: move SL up as price rises
            if current_price > best_price * (1 + adaptive_step):
                best_price = current_price
                new_sl = round(current_price * (1 - adaptive_step), 2)

                if new_sl > current_sl:
                    try:
                        # Attempt to update on exchange
                        update_success = update_stop_loss(symbol, side, new_sl)
                        
                        current_sl = new_sl
                        locked_profit = round((current_sl - entry_price) * trade["quantity"], 4)
                        sl_update_count += 1
                        
                        msg = (
                            f"📈 TRAIL UPDATE — {symbol} (#{sl_update_count})\n"
                            f"🎯 Price: {current_price}\n"
                            f"🛑 SL: {current_sl}\n"
                            f"💰 Locked: +{locked_profit} USDT\n"
                            f"📊 Trend: {trend['trend_direction']} (momentum: {trend['momentum']:.2f})"
                        )
                        print(f"  [trailing] ✅ {msg.split(chr(10))[0]}")
                        if notify_callback:
                            notify_callback(msg)
                        
                        # Also notify via Telegram with better formatting
                        notify_trade_update(symbol, current_price, current_sl, locked_profit)
                            
                    except Exception as e:
                        print(f"  [trailing] ⚠️  SL update failed: {e}")

        else:  # SELL
            # For SELL: move SL down as price falls
            if current_price < best_price * (1 - adaptive_step):
                best_price = current_price
                new_sl = round(current_price * (1 + adaptive_step), 2)

                if new_sl < current_sl:
                    try:
                        # Attempt to update on exchange
                        update_success = update_stop_loss(symbol, side, new_sl)
                        
                        current_sl = new_sl
                        locked_profit = round((entry_price - current_sl) * trade["quantity"], 4)
                        sl_update_count += 1
                        
                        msg = (
                            f"📉 TRAIL UPDATE — {symbol} (#{sl_update_count})\n"
                            f"🎯 Price: {current_price}\n"
                            f"🛑 SL: {current_sl}\n"
                            f"💰 Locked: +{locked_profit} USDT\n"
                            f"📊 Trend: {trend['trend_direction']} (momentum: {trend['momentum']:.2f})"
                        )
                        print(f"  [trailing] ✅ {msg.split(chr(10))[0]}")
                        if notify_callback:
                            notify_callback(msg)
                        
                        # Also notify via Telegram with better formatting
                        notify_trade_update(symbol, current_price, current_sl, locked_profit)
                            
                    except Exception as e:
                        print(f"  [trailing] ⚠️  SL update failed: {e}")

    # ─── TRADE CLOSED ─────────────────────────────────────────────
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60  # minutes
    
    print(f"\n✅ TRAILING STOPPED for {symbol}")
    print(f"   Duration: {duration:.1f} minutes")
    print(f"   SL Updates: {sl_update_count}")
    print(f"   Locked Profit: +{locked_profit} USDT")

    # Build final summary with validation
    try:
        final_price = get_current_price(symbol)
        
        if final_price <= 0:
            print(f"  ⚠️  Final price invalid ({final_price}). Using entry price.")
            final_price = entry_price
        
        if side == "Buy":
            final_pnl = round((final_price - entry_price) * trade["quantity"], 4)
        else:
            final_pnl = round((entry_price - final_price) * trade["quantity"], 4)
            
    except Exception as e:
        print(f"  ⚠️  Error getting final price: {e}")
        final_price = entry_price
        final_pnl = locked_profit

    return {
        "symbol": symbol,
        "side": side,
        "entry_price": entry_price,
        "exit_price": final_price,
        "pnl": final_pnl,
        "locked_profit": locked_profit,
        "duration_minutes": duration,
        "sl_updates": sl_update_count,
        "final_trend": trend["trend_direction"],
    }
