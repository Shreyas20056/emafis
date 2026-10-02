import os
import sys
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Ensure backend directory is in sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

def load_env_file() -> None:
    env_path = BACKEND_DIR / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.strip().split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

load_env_file()

from core.llm import get_groq_llm
from tools.technical_tool import fetch_technical_indicators



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
3. MACD: Bullish crossover is a buy signal; Bearish crossover is a sell signal.
4. Bollinger Bands: Price near BB Lower indicates potential bounce; near BB Upper indicates resistance.

Determine an overall technical trend score between -1.0 and +1.0.
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

    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        try:
            llm = get_groq_llm(temperature=0.1).with_structured_output(TechnicalAgentOutput)


            formatted_metrics = f"""
            Current Price: ${metrics.get('current_price')}
            20-Day SMA: ${metrics.get('sma_20')}
            50-Day SMA: ${metrics.get('sma_50')} (Trend vs 50D: {metrics.get('trend_50d')})
            RSI (14-period): {metrics.get('rsi')}
            MACD Line: {metrics.get('macd')} | MACD Signal: {metrics.get('macd_signal')}
            MACD Crossover Event: {metrics.get('macd_crossover')}
            Bollinger Bands: Upper ${metrics.get('bb_upper')} | Lower ${metrics.get('bb_lower')}
            """

            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", "Here are the computed technical indicators:\n\n{metrics_text}")
            ])

            chain = prompt | llm
            return chain.invoke({"ticker": ticker, "metrics_text": formatted_metrics})
        except Exception as e:
            print(f"Technical agent Groq fallback triggered ({e})")

    rsi = metrics.get("rsi", 50.0)
    macd_cross = metrics.get("macd_crossover", "Neutral")
    trend_50d = metrics.get("trend_50d", "Neutral")

    score = 0.0
    signals = []
    if rsi < 30:
        score += 0.4
        signals.append(f"RSI Oversold ({rsi})")
    elif rsi > 70:
        score -= 0.4
        signals.append(f"RSI Overbought ({rsi})")

    if macd_cross == "Bullish":
        score += 0.35
        signals.append("MACD Bullish Crossover")
    elif macd_cross == "Bearish":
        score -= 0.35
        signals.append("MACD Bearish Crossover")

    if trend_50d == "Bullish":
        score += 0.25
        signals.append("Trading above 50-day SMA")
    else:
        score -= 0.25
        signals.append("Trading below 50-day SMA")

    score = max(-1.0, min(1.0, score))
    condition = "Bullish Momentum" if score > 0.25 else ("Bearish Breakdown" if score < -0.25 else "Neutral Consolidation")

    return TechnicalAgentOutput(
        ticker=ticker,
        technical_score=round(score, 2),
        confidence=0.80,
        key_signals=signals or ["Consolidation near moving averages"],
        trend_condition=condition,
        summary_explanation=f"Technical chart evaluation for {ticker}: RSI = {rsi}, MACD = {macd_cross}, Trend = {trend_50d}."
    )


if __name__ == "__main__":
    ticker = "NVDA"
    print(f"Running Technical Analysis Agent for {ticker}...")
    output = run_technical_agent(ticker)
    print("\n--- TECHNICAL AGENT RESULT ---")
    print(output)