import os
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from tools.technical_tool import fetch_technical_indicators

BACKEND_DIR = Path(__file__).resolve().parent.parent

def load_env_file() -> None:
    env_path = BACKEND_DIR / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

load_env_file()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("Missing Groq API key. Set GROQ_API_KEY in the backend .env file.")

os.environ["GROQ_API_KEY"] = GROQ_API_KEY


# ==========================================
# 1. STRUCTURED OUTPUT SCHEMA
# ==========================================
class TechnicalAgentOutput(BaseModel):
    ticker: str
    technical_score: float = Field(
        ..., 
        description="Technical trend score ranging from -1.0 (Strong Bearish) to +1.0 (Strong Bullish)"
    )
    confidence: float = Field(..., description="Agent confidence score from 0.0 to 1.0")
    key_signals: list[str] = Field(..., description="Key technical highlights (e.g. RSI level, Golden Cross)")
    trend_condition: str = Field(..., description="Overall trend (e.g. Bullish Momentum, Oversold Reversal, Bearish Breakdown)")
    summary_explanation: str = Field(..., description="Detailed breakdown of technical chart patterns")


SYSTEM_PROMPT = """
You are a Senior Technical Analysis Agent specializing in quantitative chart patterns and momentum indicators.
You are evaluating the recent technical indicators for ticker: {ticker}.

Analyze the provided technical metrics:
1. RSI: Below 30 is Oversold (Bullish potential), Above 70 is Overbought (Bearish potential).
2. Moving Averages: Price above 20-SMA and 50-SMA indicates an Uptrend.
3. MACD: Bullish crossover is a strong buy signal; Bearish crossover is a sell signal.
4. Bollinger Bands: Price near BB Lower indicates potential bounce; near BB Upper indicates resistance.

Determine an overall technical trend score between -1.0 (Very Bearish) and +1.0 (Very Bullish).
DO NOT invent price levels or indicators not present in the data.
"""

def run_technical_agent(ticker: str) -> TechnicalAgentOutput:
    metrics = fetch_technical_indicators(ticker)
    
    if not metrics:
        return TechnicalAgentOutput(
            ticker=ticker,
            technical_score=0.0,
            confidence=0.1,
            key_signals=["Insufficient historical price data"],
            trend_condition="Neutral / Unknown",
            summary_explanation=f"Could not retrieve sufficient price history for {ticker} to compute technical indicators."
        )

    # Replaced with ChatGroq
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=0.1
    ).with_structured_output(TechnicalAgentOutput)

    formatted_metrics = f"""
    Current Price: ${metrics['current_price']}
    20-Day SMA: ${metrics['sma_20']}
    50-Day SMA: ${metrics['sma_50']} (Trend vs 50D: {metrics['trend_50d']})
    RSI (14-period): {metrics['rsi']}
    MACD Line: {metrics['macd']} | MACD Signal: {metrics['macd_signal']}
    MACD Crossover Event: {metrics['macd_crossover']}
    Bollinger Bands: Upper ${metrics['bb_upper']} | Lower ${metrics['bb_lower']}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Here are the computed technical indicators:\n\n{metrics_text}")
    ])

    chain = prompt | llm
    result = chain.invoke({"ticker": ticker, "metrics_text": formatted_metrics})
    return result


if __name__ == "__main__":
    ticker = "NVDA"
    print(f"Running Technical Analysis Agent for {ticker}...")
    output = run_technical_agent(ticker)
    
    print("\n--- TECHNICAL AGENT RESULT ---")
    print(f"Ticker: {output.ticker}")
    print(f"Technical Score: {output.technical_score}")
    print(f"Confidence: {output.confidence}")
    print(f"Trend Condition: {output.trend_condition}")
    print(f"Key Signals: {output.key_signals}")
    print(f"Summary: {output.summary_explanation}")