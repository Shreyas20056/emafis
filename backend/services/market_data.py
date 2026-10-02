import yfinance as yf
from typing import List, Dict, Any


def get_nse_symbol(ticker: str) -> str:
    """Ensures ticker symbol points to NSE (.NS) if no exchange extension is specified."""
    symbol = ticker.strip().upper()
    if not symbol.endswith((".NS", ".BO")):
        symbol = f"{symbol}.NS"
    return symbol


def get_current_price(ticker: str) -> float:
    """
    Get live real-time price for Indian stocks in ₹ (INR).
    """
    try:
        symbol = get_nse_symbol(ticker)
        data = yf.Ticker(symbol).history(period="2d")

        if data.empty and symbol.endswith(".NS"):
            # Fallback to direct symbol if .NS yielded nothing
            data = yf.Ticker(ticker.strip().upper()).history(period="2d")

        if data.empty:
            return 0.0
        return round(float(data["Close"].iloc[-1]), 2)
    except Exception as e:
        print(f"Price fetch error for {ticker}: {e}")
        return 0.0


def get_ohlcv(ticker: str, period: str = "3mo", interval: str = "1d") -> List[Dict[str, Any]]:
    """
    Return OHLCV price history for Indian stock charts in ₹ (INR).
    """
    try:
        symbol = get_nse_symbol(ticker)
        df = yf.Ticker(symbol).history(period=period, interval=interval)

        if df.empty and symbol.endswith(".NS"):
            df = yf.Ticker(ticker.strip().upper()).history(period=period, interval=interval)

        if df.empty:
            return []

        records = []
        for idx, row in df.iterrows():
            records.append({
                "time": idx.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"])
            })
        return records
    except Exception as e:
        print(f"OHLCV error for {ticker}: {e}")
        return []