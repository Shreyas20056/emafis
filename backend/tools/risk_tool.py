import yfinance as yf
import pandas as pd
import numpy as np

def fetch_risk_metrics(ticker: str, period: str = "1y", risk_free_rate: float = 0.04) -> dict:
    """
    Downloads historical daily prices for a ticker and market benchmark (^GSPC)
    to calculate risk metrics: Volatility, Sharpe Ratio, Max Drawdown, and Beta.
    """
    # Download ticker and benchmark data concurrently
    data = yf.download([ticker, "^GSPC"], period=period, progress=False)['Close']
    
    if data.empty or ticker not in data.columns:
        return {}

    df = data.dropna()
    
    # Calculate daily percentage returns
    ticker_returns = df[ticker].pct_change().dropna()
    market_returns = df['^GSPC'].pct_change().dropna()

    if len(ticker_returns) < 50:
        return {}

    # 1. Annualized Volatility (Standard Deviation * sqrt(252 trading days))
    annualized_volatility = float(ticker_returns.std() * np.sqrt(252))

    # 2. Sharpe Ratio (Risk-adjusted return)
    annualized_return = float(ticker_returns.mean() * 252)
    sharpe_ratio = float((annualized_return - risk_free_rate) / annualized_volatility) if annualized_volatility > 0 else 0.0

    # 3. Maximum Drawdown (Peak to Trough drop)
    cumulative_returns = (1 + ticker_returns).cumprod()
    peak = cumulative_returns.cummax()
    drawdown = (cumulative_returns - peak) / peak
    max_drawdown = float(drawdown.min())  # Will be a negative float, e.g., -0.18 (-18%)

    # 4. Beta calculation (Market Risk Sensitivity)
    covariance = np.cov(ticker_returns, market_returns)[0][1]
    market_variance = np.var(market_returns)
    beta = float(covariance / market_variance) if market_variance > 0 else 1.0

    # 5. Value at Risk (VaR - 95% Confidence Level Daily Loss)
    var_95 = float(np.percentile(ticker_returns, 5))  # Bottom 5th percentile return

    return {
        "current_price": round(float(df[ticker].iloc[-1]), 2),
        "annualized_return_pct": round(annualized_return * 100, 2),
        "annualized_volatility_pct": round(annualized_volatility * 100, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "max_drawdown_pct": round(abs(max_drawdown) * 100, 2),
        "beta": round(beta, 2),
        "var_95_daily_pct": round(abs(var_95) * 100, 2)
    }