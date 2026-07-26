import yfinance as yf
import pandas as pd

def fetch_macro_indicators(ticker: str, period: str = "1mo") -> dict:
    """
    Fetches macroeconomic indicators (10-Yr Treasury Yield, Crude Oil, USD Index)
    and evaluates the target stock's sector ETF performance.
    """
    # Standard macro tickers
    macro_tickers = {
        "^TNX": "10_Yr_Treasury_Yield", # Interest rate benchmark
        "CL=F": "Crude_Oil",            # Commodity/Inflation indicator
        "DX-Y.NYB": "USD_Index"          # US Dollar currency strength
    }
    
    # Map common stock tickers to their primary Sector ETFs
    sector_map = {
        "NVDA": "XLK", "AAPL": "XLK", "MSFT": "XLK", "GOOGL": "XLC", "META": "XLC",
        "AMZN": "XLY", "TSLA": "XLY", "JPM": "XLF", "BAC": "XLF", "PFE": "XLV"
    }
    sector_etf = sector_map.get(ticker.upper(), "SPY") # Default to S&P 500 ETF if unmapped

    all_tickers = list(macro_tickers.keys()) + [sector_etf]
    data = yf.download(all_tickers, period=period, progress=False)['Close']
    
    if data.empty:
        return {}

    macro_summary = {}
    
    # 1. Process 10-Yr Yield, Oil, and USD Index changes over 30 days
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

    # 2. Process Sector ETF performance
    if sector_etf in data.columns:
        etf_series = data[sector_etf].dropna()
        if not etf_series.empty:
            sector_change = float(((etf_series.iloc[-1] - etf_series.iloc[0]) / etf_series.iloc[0]) * 100)
            macro_summary["Sector_ETF"] = {
                "symbol": sector_etf,
                "1m_change_pct": round(sector_change, 2),
                "trend": "Bullish" if sector_change > 0 else "Bearish"
            }

    return macro_summary