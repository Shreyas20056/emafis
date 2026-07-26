import yfinance as yf
import pandas as pd
import numpy as np

def fetch_technical_indicators(ticker: str, period: str = "6mo") -> dict:
    """
    Downloads stock data from Yahoo Finance and calculates core technical indicators.
    Period fixed to '6mo'.
    """
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    
    # Drop rows where 'Close' is missing
    df = df.dropna(subset=['Close'])

    if df.empty or len(df) < 50:
        return {}

    # 1. Simple Moving Averages (SMA)
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()

    # 2. Standard Wilder's RSI (14-period EWM)
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    
    rs = avg_gain / avg_loss.replace(0, np.nan) # Avoid division by zero
    df['RSI'] = 100 - (100 / (1 + rs))
    df['RSI'] = df['RSI'].fillna(50.0)          # Fallback neutral RSI

    # 3. MACD (12-period EMA, 26-period EMA, 9-period Signal)
    ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_12 - ema_26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # 4. Bollinger Bands (20-period SMA +/- 2 std dev)
    std_20 = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['SMA_20'] + (std_20 * 2)
    df['BB_Lower'] = df['SMA_20'] - (std_20 * 2)

    # Clean out trailing rows containing NaN values
    df = df.dropna()
    if df.empty or len(df) < 2:
        return {}

    # Grab the latest valid metrics
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    return {
        "current_price": round(float(latest['Close']), 2),
        "sma_20": round(float(latest['SMA_20']), 2),
        "sma_50": round(float(latest['SMA_50']), 2),
        "rsi": round(float(latest['RSI']), 2),
        "macd": round(float(latest['MACD']), 2),
        "macd_signal": round(float(latest['MACD_Signal']), 2),
        "macd_crossover": (
            "Bullish" if (prev['MACD'] < prev['MACD_Signal'] and latest['MACD'] > latest['MACD_Signal'])
            else ("Bearish" if (prev['MACD'] > prev['MACD_Signal'] and latest['MACD'] < latest['MACD_Signal']) else "Neutral")
        ),
        "bb_upper": round(float(latest['BB_Upper']), 2),
        "bb_lower": round(float(latest['BB_Lower']), 2),
        "trend_50d": "Bullish" if latest['Close'] > latest['SMA_50'] else "Bearish"
    }