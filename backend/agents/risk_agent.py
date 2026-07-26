import os
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from tools.risk_tool import fetch_risk_metrics

# ==========================================
# 0. ENVIRONMENT SETUP
# ==========================================
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
# 1. STRUCTURED OUTPUT SCHEMA (Pydantic)
# ==========================================
class RiskAgentOutput(BaseModel):
    ticker: str
    risk_score: float = Field(
        ..., 
        description="Risk penalty score ranging from -1.0 (High Downside Risk/Bearish) to +1.0 (Low Risk/Strong Risk-Adjusted Buy)"
    )
    risk_level: str = Field(..., description="Overall risk rating: 'Low', 'Moderate', or 'High'")
    confidence: float = Field(..., description="Agent confidence rating between 0.0 and 1.0")
    key_risk_flags: list[str] = Field(..., description="Bullet points highlighting core risk factors")
    summary_explanation: str = Field(..., description="Detailed explanation evaluating the risk profile")


# ==========================================
# 2. CORE RISK AGENT LOGIC
# ==========================================
SYSTEM_PROMPT = """
You are a Senior Portfolio Risk Manager Agent evaluating qualitative & quantitative downside exposure.
You are evaluating ticker: {ticker}.

Analyze the provided quantitative risk indicators carefully:
1. Volatility (>35% is High Volatility; <20% is Low Volatility).
2. Sharpe Ratio (>1.0 is Good Risk-Adjusted Return; <0.5 is Poor Risk-Adjusted Return).
3. Max Drawdown (>30% represents severe downside vulnerability).
4. Beta (>1.5 means highly sensitive to market drops; <1.0 means less volatile than S&P 500).

Instructions:
- Provide a risk_score between -1.0 (High Risk/Aggressive Sell) and +1.0 (Low Risk/Safe Buy).
- Assign an explicit risk_level: 'Low', 'Moderate', or 'High'.
- Extract key_risk_flags summarizing drawdown threats, market volatility, or bad Sharpe Ratios.
- Base your analysis ONLY on the provided metrics.
"""

def run_risk_agent(ticker: str) -> RiskAgentOutput:
    metrics = fetch_risk_metrics(ticker)
    
    if not metrics:
        return RiskAgentOutput(
            ticker=ticker,
            risk_score=-0.5,
            risk_level="High",
            confidence=0.1,
            key_risk_flags=["Unable to calculate historical risk metrics due to missing market data"],
            summary_explanation=f"Insufficient price history for {ticker} to run quantitative risk assessment models."
        )

    # Initialize Groq LLM with structured output
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=0.1
    ).with_structured_output(RiskAgentOutput)

    formatted_metrics = f"""
    Current Price: ${metrics['current_price']}
    Annualized Return: {metrics['annualized_return_pct']}%
    Annualized Volatility: {metrics['annualized_volatility_pct']}%
    Sharpe Ratio (Risk-Adjusted Return): {metrics['sharpe_ratio']}
    Maximum Historical Drawdown: {metrics['max_drawdown_pct']}%
    Beta (Market Sensitivity vs S&P 500): {metrics['beta']}
    Daily Value at Risk (95% VaR): -{metrics['var_95_daily_pct']}%
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Here are the computed quantitative risk metrics:\n\n{metrics_text}")
    ])

    chain = prompt | llm
    result = chain.invoke({"ticker": ticker, "metrics_text": formatted_metrics})
    return result


# ==========================================
# 3. DIRECT SCRIPT EXECUTION / LOCAL TEST
# ==========================================
if __name__ == "__main__":
    ticker = "NVDA"
    print(f"Running Risk Assessment Agent for {ticker}...")
    output = run_risk_agent(ticker)
    
    print("\n--- RISK AGENT RESULT ---")
    print(f"Ticker: {output.ticker}")
    print(f"Risk Score: {output.risk_score}")
    print(f"Risk Level: {output.risk_level}")
    print(f"Confidence: {output.confidence}")
    print(f"Risk Flags: {output.key_risk_flags}")
    print(f"Summary: {output.summary_explanation}")