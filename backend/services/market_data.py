import yfinance as yf
from typing import List, Dict, Any

# Cached map of resolved ticker symbols for speed
WORKING_SYMBOL_CACHE: Dict[str, str] = {}

# Standard Index & Ticker Symbol Mapping
EXPLICIT_SYMBOL_MAP: Dict[str, List[str]] = {
    "NIFTY": ["^NSEI"],
    "NIFTY50": ["^NSEI"],
    "NIFTY 50": ["^NSEI"],
    "BANKNIFTY": ["^NSEBANK"],
    "NIFTYBANK": ["^NSEBANK"],
    "NIFTY BANK": ["^NSEBANK"],
    "NIFTY SMALLCAP": ["^CNXSC", "HDFCSML250.NS"],
    "NIFTYSMALLCAP": ["^CNXSC"],
    "NIFTY MIDCAP": ["NIFTYMIDCAP150.NS"],
    "SENSEX": ["^BSESN"],
    "TATAMOTORS": ["TATAMOTORS.NS", "TMPV.NS", "TMCV.NS", "TATAMOTORS.BO"],
    "ZOMATO": ["ZOMATO.NS", "ETERNAM.NS", "ZOMATO.BO"],
}


def get_possible_symbols(ticker: str) -> List[str]:
    """Returns candidate yfinance symbols for a given search query or stock ticker."""
    clean = ticker.strip().upper()

    # Check cache first
    if clean in WORKING_SYMBOL_CACHE:
        return [WORKING_SYMBOL_CACHE[clean]]

    # Check explicit map
    if clean in EXPLICIT_SYMBOL_MAP:
        return EXPLICIT_SYMBOL_MAP[clean]

    if clean.endswith((".NS", ".BO")) or clean.startswith("^"):
        return [clean]

    return [f"{clean}.NS", clean, f"{clean}.BO"]


def get_current_price(ticker: str) -> float:
    """
    Get live real-time price for Indian stocks or indices.
    """
    candidates = get_possible_symbols(ticker)
    clean_ticker = ticker.strip().upper()

    for sym in candidates:
        try:
            data = yf.Ticker(sym).history(period="5d")
            if not data.empty:
                WORKING_SYMBOL_CACHE[clean_ticker] = sym
                return round(float(data["Close"].iloc[-1]), 2)
        except Exception:
            continue

    print(f"[WARN] Price fetch failed for {ticker}")
    return 0.0


def get_ohlcv(ticker: str, period: str = "3mo", interval: str = "1d") -> List[Dict[str, Any]]:
    """
    Return OHLCV price history for stock or index charts in ₹ (INR) or currency.
    """
    candidates = get_possible_symbols(ticker)
    clean_ticker = ticker.strip().upper()

    for sym in candidates:
        try:
            df = yf.Ticker(sym).history(period=period, interval=interval)
            if df.empty:
                # Retry with 6mo or 1y if shorter period yielded empty
                df = yf.Ticker(sym).history(period="6mo", interval=interval)

            if not df.empty:
                WORKING_SYMBOL_CACHE[clean_ticker] = sym
                records = []
                for idx, row in df.iterrows():
                    records.append({
                        "time": idx.strftime("%Y-%m-%d"),
                        "open": round(float(row["Open"]), 2),
                        "high": round(float(row["High"]), 2),
                        "low": round(float(row["Low"]), 2),
                        "close": round(float(row["Close"]), 2),
                        "volume": int(row["Volume"]) if "Volume" in row and not pd_isna(row["Volume"]) else 0
                    })
                return records
        except Exception as e:
            print(f"[WARN] Error loading chart for candidate {sym}: {e}")
            continue

    print(f"[WARN] OHLCV chart fetch failed for all candidates of {ticker}")
    return []


def pd_isna(val) -> bool:
    try:
        import math
        return math.isnan(val)
    except Exception:
        return False