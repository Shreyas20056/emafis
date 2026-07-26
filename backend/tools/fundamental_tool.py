import yfinance as yf

def fetch_fundamental_metrics(ticker: str) -> dict:
    """
    Fetches core fundamental valuation and profitability metrics
    from Yahoo Finance (info dict).
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}

        if not info or 'regularMarketPrice' not in info and 'currentPrice' not in info:
            return {}

        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0.0)
        
        return {
            "current_price": round(float(current_price), 2),
            "trailing_pe": round(float(info.get('trailingPE', 0.0)), 2) if info.get('trailingPE') else "N/A",
            "forward_pe": round(float(info.get('forwardPE', 0.0)), 2) if info.get('forwardPE') else "N/A",
            "price_to_sales": round(float(info.get('priceToSalesTrailing12Months', 0.0)), 2) if info.get('priceToSalesTrailing12Months') else "N/A",
            "price_to_book": round(float(info.get('priceToBook', 0.0)), 2) if info.get('priceToBook') else "N/A",
            "profit_margins_pct": round(float(info.get('profitMargins', 0.0)) * 100, 2) if info.get('profitMargins') else "N/A",
            "operating_margins_pct": round(float(info.get('operatingMargins', 0.0)) * 100, 2) if info.get('operatingMargins') else "N/A",
            "return_on_equity_pct": round(float(info.get('returnOnEquity', 0.0)) * 100, 2) if info.get('returnOnEquity') else "N/A",
            "debt_to_equity": round(float(info.get('debtToEquity', 0.0)), 2) if info.get('debtToEquity') else "N/A",
            "free_cash_flow": info.get('freeCashflow', 'N/A'),
            "revenue_growth_pct": round(float(info.get('revenueGrowth', 0.0)) * 100, 2) if info.get('revenueGrowth') else "N/A"
        }
    except Exception as e:
        print(f"Error fetching fundamental data for {ticker}: {e}")
        return {}