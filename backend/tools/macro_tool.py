import yfinance as yf
import pandas as pd

def fetch_macro_indicators(ticker: str, period: str = "1mo") -> dict:
    """
    Fetches Indian macroeconomic indicators (NIFTY 50 ^NSEI, Bank NIFTY ^NSEBANK, USD/INR INR=X, Crude Oil BZ=F)
    and evaluates the target stock's sector trend.
    """
    macro_tickers = {
        "^NSEI": "NIFTY_50_Index",       # Indian market benchmark
        "^NSEBANK": "BANK_NIFTY_Index", # Financial sector benchmark
        "INR=X": "USD_INR_Exchange",    # Currency strength (USD/INR)
        "BZ=F": "Brent_Crude_Oil"       # Commodity / Inflation indicator
    }
    
    all_tickers = list(macro_tickers.keys())
    try:
        data = yf.download(all_tickers, period=period, progress=False)['Close']
        
        if data.empty:
            return {}

        macro_summary = {}
        
        for sym, label in macro_tickers.items():
            if sym in data.columns:
                series = data[sym].dropna()
                if not series.empty:
                    current_val = float(series.iloc[-1])
                    monthly_pct_change = float(((series.iloc[-1] - series.iloc[0]) / series.iloc[0]) * 100)
                    macro_summary[label] = {
                        "value": round(current_val, 2),
                        "1m_change_pct": round(monthly_pct_change, 2)
                    }

        # NIFTY 50 overall trend
        if "^NSEI" in data.columns:
            nifty_series = data["^NSEI"].dropna()
            if not nifty_series.empty:
                nifty_change = float(((nifty_series.iloc[-1] - nifty_series.iloc[0]) / nifty_series.iloc[0]) * 100)
                macro_summary["Sector_ETF"] = {
                    "symbol": "NIFTY 50 Index",
                    "1m_change_pct": round(nifty_change, 2),
                    "trend": "Bullish" if nifty_change > 0 else "Bearish"
                }

        return macro_summary
    except Exception as e:
        print(f"Error fetching Indian macro metrics for {ticker}: {e}")
        return {}