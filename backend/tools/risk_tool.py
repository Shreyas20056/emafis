import yfinance as yf
import pandas as pd
import numpy as np

def fetch_risk_metrics(ticker: str, period: str = "1y", risk_free_rate: float = 0.068) -> dict:
    """
    Downloads historical daily prices for an Indian stock ticker and NIFTY 50 benchmark (^NSEI)
    to calculate risk metrics: Volatility, Sharpe Ratio, Max Drawdown, and Beta against NIFTY 50.
    Risk-free rate set to 6.8% (RBI 10-Yr G-Sec yield).
    """
    symbol = ticker.strip().upper()
    if not symbol.endswith((".NS", ".BO")):
        symbol = f"{symbol}.NS"

    benchmark = "^NSEI"  # NIFTY 50 Index

    try:
        data = yf.download([symbol, benchmark], period=period, progress=False)['Close']
        
        if data.empty or symbol not in data.columns:
            # Fallback if download failed
            return {}

        df = data.dropna()
        
        ticker_returns = df[symbol].pct_change().dropna()
        market_returns = df[benchmark].pct_change().dropna()

        if len(ticker_returns) < 30:
            return {}

        # 1. Annualized Volatility
        annualized_volatility = float(ticker_returns.std() * np.sqrt(252))

        # 2. Sharpe Ratio (Risk-adjusted return vs 6.8% RBI G-Sec yield)
        annualized_return = float(ticker_returns.mean() * 252)
        sharpe_ratio = float((annualized_return - risk_free_rate) / annualized_volatility) if annualized_volatility > 0 else 0.0

        # 3. Maximum Drawdown
        cumulative_returns = (1 + ticker_returns).cumprod()
        peak = cumulative_returns.cummax()
        drawdown = (cumulative_returns - peak) / peak
        max_drawdown = float(drawdown.min())

        # 4. Beta calculation vs NIFTY 50
        covariance = np.cov(ticker_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        beta = float(covariance / market_variance) if market_variance > 0 else 1.0

        # 5. Value at Risk (VaR - 95% Confidence Level Daily Loss)
        var_95 = float(np.percentile(ticker_returns, 5))

        return {
            "current_price": round(float(df[symbol].iloc[-1]), 2),
            "annualized_return_pct": round(annualized_return * 100, 2),
            "annualized_volatility_pct": round(annualized_volatility * 100, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "max_drawdown_pct": round(abs(max_drawdown) * 100, 2),
            "beta": round(beta, 2),
            "var_95_daily_pct": round(abs(var_95) * 100, 2)
        }
    except Exception as e:
        print(f"Error calculating NIFTY risk metrics for {ticker}: {e}")
        return {}