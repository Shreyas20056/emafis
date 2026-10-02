import os
import sys
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

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

from core.llm import get_groq_llm
from tools.macro_tool import fetch_macro_indicators



# ==========================================
# 1. STRUCTURED OUTPUT SCHEMA (Pydantic)
# ==========================================
class MacroAgentOutput(BaseModel):
    ticker: str = Field(description="The stock ticker symbol analyzed")
    macro_score: float = Field(
        ..., 
        description="Macroeconomic score from -1.0 (Severe Headwinds) to +1.0 (Strong Tailwinds)"
    )
    confidence: float = Field(..., description="Agent confidence score between 0.0 and 1.0")
    key_macro_factors: list[str] = Field(..., description="List of string bullet points summarizing interest rate, commodity, or currency impacts")
    macro_environment: str = Field(..., description="Environment summary")
    summary_explanation: str = Field(..., description="Detailed explanation of macro factors affecting the stock")


parser = PydanticOutputParser(pydantic_object=MacroAgentOutput)


SYSTEM_PROMPT = """
You are a Senior Macroeconomic Analyst Agent evaluating broader market economic trends.
You are analyzing macroeconomic headwinds and tailwinds for ticker: {ticker}.

Analyze the provided macroeconomic indicators:
1. 10-Year Treasury Yields (^TNX): Rising yields increase borrowing costs.
2. Crude Oil (CL=F): Spiking oil increases input costs.
3. US Dollar Index (USD_Index): Strong dollar affects export competitiveness.
4. Sector ETF Performance: Shows sector momentum.

Instructions:
- Provide a macro_score from -1.0 to +1.0.
- Ensure 'key_macro_factors' is a plain LIST OF STRINGS.
- Base your analysis strictly on the provided macro metrics.

{format_instructions}
"""

def run_macro_agent(ticker: str) -> MacroAgentOutput:
    metrics = fetch_macro_indicators(ticker)
    
    if not metrics:
        return MacroAgentOutput(
            ticker=ticker,
            macro_score=0.0,
            confidence=0.2,
            key_macro_factors=["Unable to retrieve current macroeconomic benchmark data"],
            macro_environment="Neutral / Data Unavailable",
            summary_explanation=f"Could not retrieve macroeconomic indicators for {ticker}."
        )

    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        try:
            llm = get_groq_llm(
                temperature=0.1,
                model_kwargs={"response_format": {"type": "json_object"}}
            )


            formatted_metrics = f"""
            10-Year Treasury Yield: {metrics.get('10_Yr_Treasury_Yield', {}).get('value', 'N/A')}% (1-Month Change: {metrics.get('10_Yr_Treasury_Yield', {}).get('1m_change_pct', 'N/A')}%)
            Crude Oil Price: ${metrics.get('Crude_Oil', {}).get('value', 'N/A')} (1-Month Change: {metrics.get('Crude_Oil', {}).get('1m_change_pct', 'N/A')}%)
            US Dollar Index: {metrics.get('USD_Index', {}).get('value', 'N/A')} (1-Month Change: {metrics.get('USD_Index', {}).get('1m_change_pct', 'N/A')}%)
            Sector ETF ({metrics.get('Sector_ETF', {}).get('symbol', 'SPY')}): 1-Month Trend is {metrics.get('Sector_ETF', {}).get('trend', 'N/A')} ({metrics.get('Sector_ETF', {}).get('1m_change_pct', 'N/A')}%)
            """

            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", "Here are the live macroeconomic indicators:\n\n{metrics_text}")
            ]).partial(format_instructions=parser.get_format_instructions())

            chain = prompt | llm | parser
            return chain.invoke({"ticker": ticker, "metrics_text": formatted_metrics})
        except Exception as e:
            print(f"Macro agent Groq fallback triggered ({e})")

    # Fallback quantitative logic
    sector_info = metrics.get("Sector_ETF", {})
    sector_change = sector_info.get("1m_change_pct", 0.0)
    score = 0.3 if sector_change > 2 else (-0.3 if sector_change < -2 else 0.0)
    factors = [f"Sector ETF ({sector_info.get('symbol', 'SPY')}) 1M change: {sector_change}%"]

    return MacroAgentOutput(
        ticker=ticker,
        macro_score=round(score, 2),
        confidence=0.70,
        key_macro_factors=factors,
        macro_environment="Bullish Sector Momentum" if score > 0 else ("Bearish Sector Headwinds" if score < 0 else "Neutral Macro Regime"),
        summary_explanation=f"Macro environment for {ticker} evaluated via sector performance ({sector_info.get('symbol', 'SPY')}: {sector_change}%)."
    )


if __name__ == "__main__":
    ticker = "NVDA"
    print(f"Running Macroeconomic Agent for {ticker}...")
    output = run_macro_agent(ticker)
    print("\n--- MACRO AGENT RESULT ---")
    print(output)