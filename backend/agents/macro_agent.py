import os
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from tools.macro_tool import fetch_macro_indicators

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
class MacroAgentOutput(BaseModel):
    ticker: str = Field(description="The stock ticker symbol analyzed")
    macro_score: float = Field(
        ..., 
        description="Macroeconomic score from -1.0 (Severe Headwinds/Bearish) to +1.0 (Strong Tailwinds/Bullish)"
    )
    confidence: float = Field(..., description="Agent confidence score between 0.0 and 1.0")
    key_macro_factors: list[str] = Field(..., description="List of string bullet points summarizing interest rate, commodity, or currency impacts")
    macro_environment: str = Field(..., description="Environment summary (e.g., 'Rate-Sensitive Growth Exposure', 'Inflation Tailwinds')")
    summary_explanation: str = Field(..., description="Detailed explanation of macro factors affecting the stock")


# Create parser instance
parser = PydanticOutputParser(pydantic_object=MacroAgentOutput)


# ==========================================
# 2. CORE MACRO AGENT LOGIC
# ==========================================
SYSTEM_PROMPT = """
You are a Senior Macroeconomic Analyst Agent evaluating broader market economic trends.
You are analyzing macroeconomic headwinds and tailwinds for ticker: {ticker}.

Analyze the provided macroeconomic indicators:
1. 10-Year Treasury Yields (^TNX): Rising interest rates harm high-growth valuation tech stocks, but benefit financial sector stocks.
2. Crude Oil (CL=F): Spiking oil prices increase corporate input costs and trigger inflation concerns.
3. US Dollar Index (USD_Index): A strengthening dollar reduces foreign earnings conversion for multinational exporters.
4. Sector ETF Performance: Shows whether the stock's broader sector is experiencing tailwinds or headwinds.

Instructions:
- Provide a macro_score from -1.0 (Strong Economic Headwinds) to +1.0 (Strong Economic Tailwinds).
- Ensure 'key_macro_factors' is a plain LIST OF STRINGS (e.g. ["Factor 1", "Factor 2"]). Do NOT use nested JSON objects for key_macro_factors.
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

    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
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
    result = chain.invoke({"ticker": ticker, "metrics_text": formatted_metrics})
    return result


# ==========================================
# 3. DIRECT SCRIPT EXECUTION / LOCAL TEST
# ==========================================
if __name__ == "__main__":
    ticker = "NVDA"
    print(f"Running Macroeconomic Agent for {ticker}...")
    output = run_macro_agent(ticker)
    
    print("\n--- MACRO AGENT RESULT ---")
    print(f"Ticker: {output.ticker}")
    print(f"Macro Score: {output.macro_score}")
    print(f"Confidence: {output.confidence}")
    print(f"Macro Environment: {output.macro_environment}")
    print(f"Macro Factors: {output.key_macro_factors}")
    print(f"Summary: {output.summary_explanation}")