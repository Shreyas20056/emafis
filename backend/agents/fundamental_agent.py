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
from tools.fundamental_tool import fetch_fundamental_metrics



# ==========================================
# 1. STRUCTURED OUTPUT SCHEMA (Pydantic)
# ==========================================
class FundamentalAgentOutput(BaseModel):
    ticker: str = Field(description="The stock ticker symbol analyzed")
    valuation_score: float = Field(
        ..., 
        description="Fundamental valuation score from -1.0 (Severely Overvalued) to +1.0 (Highly Undervalued)"
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


parser = PydanticOutputParser(pydantic_object=FundamentalAgentOutput)


# ==========================================
# 2. CORE FUNDAMENTAL AGENT LOGIC
# ==========================================
SYSTEM_PROMPT = """
You are a Senior Equity Research & Fundamental Analysis Agent evaluating corporate valuation and operational health.
You are evaluating ticker: {ticker}.

Analyze the provided fundamental metrics:
1. Valuation Multiples: Compare Trailing P/E and Forward P/E.
2. Profitability: Profit Margins and Operating Margins (>20% is strong).
3. Efficiency: Return on Equity (ROE > 15% is strong).
4. Solvency: Debt-to-Equity.
5. Growth: Revenue Growth % YoY.

Instructions:
- Provide a valuation_score from -1.0 to +1.0.
- Explicitly set 'valuation_status' to 'Undervalued', 'Fairly Valued', or 'Overvalued'.
- Ensure 'key_fundamental_drivers' is a plain LIST OF STRINGS.
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

    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        try:
            llm = get_groq_llm(
                temperature=0.1,
                model_kwargs={"response_format": {"type": "json_object"}}
            )


            formatted_metrics = f"""
            Current Price: ${metrics.get('current_price')}
            Trailing P/E: {metrics.get('trailing_pe')}
            Forward P/E: {metrics.get('forward_pe')}
            Price-to-Sales (P/S): {metrics.get('price_to_sales')}
            Price-to-Book (P/B): {metrics.get('price_to_book')}
            Profit Margin: {metrics.get('profit_margins_pct')}%
            Operating Margin: {metrics.get('operating_margins_pct')}%
            Return on Equity (ROE): {metrics.get('return_on_equity_pct')}%
            Debt-to-Equity Ratio: {metrics.get('debt_to_equity')}
            Revenue Growth (YoY): {metrics.get('revenue_growth_pct')}%
            """

            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", "Here are the live fundamental indicators:\n\n{metrics_text}")
            ]).partial(format_instructions=parser.get_format_instructions())

            chain = prompt | llm | parser
            return chain.invoke({"ticker": ticker, "metrics_text": formatted_metrics})
        except Exception as e:
            print(f"Fundamental agent Groq fallback triggered ({e})")

    # Rule-based quantitative fallback
    pe = metrics.get("trailing_pe")
    roe = metrics.get("return_on_equity_pct")
    f_pe = metrics.get("forward_pe")
    score = 0.0
    drivers = []

    if isinstance(pe, (int, float)) and pe > 0:
        if pe < 20:
            score += 0.3
            drivers.append(f"Favorable P/E ratio of {pe}")
        elif pe > 45:
            score -= 0.3
            drivers.append(f"Elevated P/E ratio of {pe}")
    if isinstance(roe, (int, float)) and roe > 15:
        score += 0.3
        drivers.append(f"Strong Return on Equity at {roe}%")
    if isinstance(f_pe, (int, float)) and isinstance(pe, (int, float)) and f_pe < pe:
        score += 0.2
        drivers.append(f"Forward P/E ({f_pe}) below Trailing P/E ({pe}), indicating growth")

    score = max(-1.0, min(1.0, score))
    status = "Undervalued" if score > 0.25 else ("Overvalued" if score < -0.25 else "Fairly Valued")

    return FundamentalAgentOutput(
        ticker=ticker,
        valuation_score=round(score, 2),
        valuation_status=status,
        confidence=0.70,
        key_fundamental_drivers=drivers or ["Fair balance sheet and growth metrics"],
        summary_explanation=f"Fundamental evaluation for {ticker}: Trailing P/E = {pe}, ROE = {roe}%."
    )


if __name__ == "__main__":
    ticker = "NVDA"
    print(f"Running Fundamental Analysis Agent for {ticker}...")
    output = run_fundamental_agent(ticker)
    print("\n--- FUNDAMENTAL AGENT RESULT ---")
    print(output)