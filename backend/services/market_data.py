import yfinance as yf
from typing import Optional

def get_current_price(ticker: str) -> float:
    """
    Get latest price. Supports Indian stocks automatically.
    """
    try:
        symbol = ticker.upper()
        if not symbol.endswith((".NS", ".BO")) and symbol.isalpha():
            symbol = f"{symbol}.NS"          # NSE by default

        data = yf.Ticker(symbol).history(period="2d")
        if data.empty:
            # fallback to US ticker
            data = yf.Ticker(ticker).history(period="2d")

        if data.empty:
            return 0.0
        return float(data["Close"].iloc[-1])
    except Exception as e:
        print(f"Price fetch error for {ticker}: {e}")
        return 0.0


def get_ohlcv(ticker: str, period: str = "3mo", interval: str = "1d"):
    """
    Return OHLCV data for charts (used by frontend).
    """
    try:
        symbol = ticker.upper()
        if not symbol.endswith((".NS", ".BO")) and symbol.isalpha():
            symbol = f"{symbol}.NS"

        df = yf.Ticker(symbol).history(period=period, interval=interval)
        if df.empty:
            return []

        records = []
        for idx, row in df.iterrows():
            records.append({
                "time": idx.strftime("%Y-%m-%d"),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"])
            })
        return records
    except Exception as e:
        print(f"OHLCV error for {ticker}: {e}")
        return []