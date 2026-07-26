import os
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from tools.fundamental_tool import fetch_fundamental_metrics

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
class FundamentalAgentOutput(BaseModel):
    ticker: str = Field(description="The stock ticker symbol analyzed")
    valuation_score: float = Field(
        ..., 
        description="Fundamental valuation score from -1.0 (Severely Overvalued/Poor Quality) to +1.0 (Highly Undervalued/High Quality)"
    )
    valuation_status: str = Field(
        ..., 
        description="Overall valuation assessment: 'Undervalued', 'Fairly Valued', or 'Overvalued'"
    )
    confidence: float = Field(..., description="Agent confidence score between 0.0 and 1.0")
    key_fundamental_drivers: list[str] = Field(
        ..., 
        description="List of string bullet points summarizing valuation multiples, profitability, or balance sheet health"
    )
    summary_explanation: str = Field(..., description="Detailed explanation of fundamental metrics and earnings strength")


# Parser for Pydantic schema enforcement
parser = PydanticOutputParser(pydantic_object=FundamentalAgentOutput)


# ==========================================
# 2. CORE FUNDAMENTAL AGENT LOGIC
# ==========================================
SYSTEM_PROMPT = """
You are a Senior Equity Research & Fundamental Analysis Agent evaluating corporate valuation and operational health.
You are evaluating ticker: {ticker}.

Analyze the provided fundamental metrics:
1. Valuation Multiples: Compare Trailing P/E and Forward P/E (Lower Forward P/E suggests earnings growth).
2. Profitability: Profit Margins and Operating Margins (>20% indicates a strong competitive moat).
3. Efficiency: Return on Equity (ROE > 15% is strong).
4. Solvency: Debt-to-Equity (>200 means heavy leverage/debt burden).
5. Growth: Revenue Growth % year-over-year.

Instructions:
- Provide a valuation_score from -1.0 (Severely Overvalued / Weak Financial Health) to +1.0 (Attractively Undervalued / Strong Moat).
- Explicitly set 'valuation_status' to 'Undervalued', 'Fairly Valued', or 'Overvalued'.
- Ensure 'key_fundamental_drivers' is a plain LIST OF STRINGS (e.g. ["Factor 1", "Factor 2"]). Do NOT use nested JSON objects.
- Base your analysis strictly on the provided quantitative metrics.

{format_instructions}
"""

def run_fundamental_agent(ticker: str) -> FundamentalAgentOutput:
    metrics = fetch_fundamental_metrics(ticker)
    
    if not metrics:
        return FundamentalAgentOutput(
            ticker=ticker,
            valuation_score=0.0,
            valuation_status="Fairly Valued",
            confidence=0.2,
            key_fundamental_drivers=["Unable to retrieve current balance sheet or valuation metrics"],
            summary_explanation=f"Could not retrieve fundamental financial metrics for {ticker}."
        )

    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=0.1,
        model_kwargs={"response_format": {"type": "json_object"}}
    )

    formatted_metrics = f"""
    Current Price: ${metrics['current_price']}
    Trailing P/E: {metrics['trailing_pe']}
    Forward P/E: {metrics['forward_pe']}
    Price-to-Sales (P/S): {metrics['price_to_sales']}
    Price-to-Book (P/B): {metrics['price_to_book']}
    Profit Margin: {metrics['profit_margins_pct']}%
    Operating Margin: {metrics['operating_margins_pct']}%
    Return on Equity (ROE): {metrics['return_on_equity_pct']}%
    Debt-to-Equity Ratio: {metrics['debt_to_equity']}
    Revenue Growth (YoY): {metrics['revenue_growth_pct']}%
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Here are the live fundamental indicators:\n\n{metrics_text}")
    ]).partial(format_instructions=parser.get_format_instructions())

    chain = prompt | llm | parser
    result = chain.invoke({"ticker": ticker, "metrics_text": formatted_metrics})
    return result


# ==========================================
# 3. DIRECT SCRIPT EXECUTION / LOCAL TEST
# ==========================================
if __name__ == "__main__":
    ticker = "NVDA"
    print(f"Running Fundamental Analysis Agent for {ticker}...")
    output = run_fundamental_agent(ticker)
    
    print("\n--- FUNDAMENTAL AGENT RESULT ---")
    print(f"Ticker: {output.ticker}")
    print(f"Valuation Score: {output.valuation_score}")
    print(f"Valuation Status: {output.valuation_status}")
    print(f"Confidence: {output.confidence}")
    print(f"Key Drivers: {output.key_fundamental_drivers}")
    print(f"Summary: {output.summary_explanation}")