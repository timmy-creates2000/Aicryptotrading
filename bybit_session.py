# bybit_session.py — Simplified Bybit API session (REAL TRADING ONLY)

import os
from pybit.unified_trading import HTTP
from dotenv import load_dotenv

load_dotenv()


def get_session() -> HTTP:
    """
    Get Bybit API session for REAL trading (Mainnet only).
    
    Returns:
        HTTP: Configured Bybit API session
    
    Raises:
        ValueError: If API keys are not configured
    """
    api_key = os.getenv("BYBIT_API_KEY")
    api_secret = os.getenv("BYBIT_API_SECRET")
    
    if not api_key or not api_secret:
        raise ValueError(
            "BYBIT_API_KEY and BYBIT_API_SECRET must be set in environment variables"
        )
    
    # Validate key format
    if len(api_key) < 10:
        raise ValueError(
            f"Invalid API key: too short ({len(api_key)} chars). "
            f"Please check your .env file."
        )
    
    print(f"  [session] Creating REAL trading session (Mainnet)")
    print(f"  [session] API Key: {api_key[:8]}...{api_key[-4:]}")
    
    # Always use mainnet (real trading)
    return HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret,
    )
