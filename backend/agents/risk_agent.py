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
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

load_env_file()

from tools.risk_tool import fetch_risk_metrics


# ==========================================
# 1. STRUCTURED OUTPUT SCHEMA (Pydantic)
# ==========================================
class RiskAgentOutput(BaseModel):
    ticker: str
    risk_score: float = Field(
        ..., 
        description="Risk score from -1.0 (High Downside Risk) to +1.0 (Low Risk/Favorable Risk Profile)"
    )
    risk_level: str = Field(..., description="Overall risk rating: 'Low', 'Moderate', or 'High'")
    confidence: float = Field(..., description="Agent confidence rating between 0.0 and 1.0")
    key_risk_flags: list[str] = Field(..., description="Bullet points highlighting core risk factors")
    summary_explanation: str = Field(..., description="Detailed explanation evaluating the risk profile")


SYSTEM_PROMPT = """
You are a Senior Portfolio Risk Manager Agent evaluating downside exposure.
You are evaluating ticker: {ticker}.

Analyze the provided quantitative risk indicators carefully:
1. Volatility (>35% is High Volatility; <20% is Low Volatility).
2. Sharpe Ratio (>1.0 is Good Risk-Adjusted Return).
3. Max Drawdown (>30% is severe vulnerability).
4. Beta (>1.5 high market sensitivity; <1.0 less volatile).

Instructions:
- Provide a risk_score between -1.0 and +1.0.
- Assign risk_level: 'Low', 'Moderate', or 'High'.
- Extract key_risk_flags.
"""

def run_risk_agent(ticker: str) -> RiskAgentOutput:
    metrics = fetch_risk_metrics(ticker)
    
    if not metrics:
        return RiskAgentOutput(
            ticker=ticker,
            risk_score=-0.3,
            risk_level="High",
            confidence=0.1,
            key_risk_flags=["Unable to calculate historical risk metrics due to missing market data"],
            summary_explanation=f"Insufficient price history for {ticker} to run quantitative risk assessment models."
        )

    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        try:
            llm = ChatGroq(
                model="llama-3.3-70b-versatile", 
                temperature=0.1,
                groq_api_key=api_key
            ).with_structured_output(RiskAgentOutput)

            formatted_metrics = f"""
            Current Price: ${metrics.get('current_price')}
            Annualized Return: {metrics.get('annualized_return_pct')}%
            Annualized Volatility: {metrics.get('annualized_volatility_pct')}%
            Sharpe Ratio: {metrics.get('sharpe_ratio')}
            Maximum Historical Drawdown: {metrics.get('max_drawdown_pct')}%
            Beta: {metrics.get('beta')}
            Daily VaR (95%): -{metrics.get('var_95_daily_pct')}%
            """

            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", "Here are the computed quantitative risk metrics:\n\n{metrics_text}")
            ])

            chain = prompt | llm
            return chain.invoke({"ticker": ticker, "metrics_text": formatted_metrics})
        except Exception as e:
            print(f"Risk agent Groq fallback triggered ({e})")

    vol = metrics.get("annualized_volatility_pct", 25.0)
    sharpe = metrics.get("sharpe_ratio", 1.0)
    dd = metrics.get("max_drawdown_pct", 15.0)
    beta = metrics.get("beta", 1.0)

    score = 0.0
    flags = []
    if vol > 35:
        score -= 0.35
        flags.append(f"High volatility ({vol}%)")
    elif vol < 22:
        score += 0.2
        flags.append(f"Controlled volatility ({vol}%)")

    if sharpe > 1.0:
        score += 0.3
        flags.append(f"Strong Sharpe ratio ({sharpe})")
    elif sharpe < 0.3:
        score -= 0.3
        flags.append(f"Weak Sharpe ratio ({sharpe})")

    if dd > 30:
        score -= 0.25
        flags.append(f"Deep max drawdown ({dd}%)")

    score = max(-1.0, min(1.0, score))
    level = "High" if score < -0.25 else ("Low" if score > 0.25 else "Moderate")

    return RiskAgentOutput(
        ticker=ticker,
        risk_score=round(score, 2),
        risk_level=level,
        confidence=0.75,
        key_risk_flags=flags or ["Standard risk profile"],
        summary_explanation=f"Risk profile for {ticker}: Volatility = {vol}%, Sharpe = {sharpe}, Beta = {beta}."
    )


if __name__ == "__main__":
    ticker = "NVDA"
    print(f"Running Risk Assessment Agent for {ticker}...")
    output = run_risk_agent(ticker)
    print("\n--- RISK AGENT RESULT ---")
    print(output)