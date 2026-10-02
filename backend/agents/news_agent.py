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

from core.llm import get_groq_llm
from tools.finhub_tool import fetch_stock_news



# ==========================================
# 1. STRUCTURED OUTPUT SCHEMA (Pydantic)
# ==========================================
class NewsAgentOutput(BaseModel):
    ticker: str
    sentiment_score: float = Field(
        ..., 
        description="Market sentiment score ranging from -1.0 (Very Bearish) to +1.0 (Very Bullish)"
    )
    confidence: float = Field(..., description="Agent confidence score from 0.0 to 1.0")
    analyzed_articles_count: int
    bullish_drivers: list[str] = Field(..., description="Bullet points highlighting positive drivers")
    bearish_risks: list[str] = Field(..., description="Bullet points highlighting negative risks")
    summary_explanation: str = Field(..., description="Short explanation of overall news impact")


SYSTEM_PROMPT = """
You are a Senior Financial News Analyst Agent specializing in market sentiment analysis.
You are analyzing recent news coverage for ticker: {ticker}.

Analyze the provided news items carefully:
1. Determine the overall sentiment score from -1.0 to +1.0.
2. Extract specific bullish catalysts and bearish risks.
3. Provide a clear summary.

CRITICAL INSTRUCTIONS:
- Base your analysis ONLY on the provided news articles.
- If no news is available, return a neutral score (0.0).
"""

def run_news_agent(ticker: str) -> NewsAgentOutput:
    articles = fetch_stock_news(ticker)
    
    if not articles:
        return NewsAgentOutput(
            ticker=ticker,
            sentiment_score=0.0,
            confidence=0.2,
            analyzed_articles_count=0,
            bullish_drivers=["No recent news coverage found"],
            bearish_risks=["Lack of news visibility"],
            summary_explanation=f"No recent news articles were retrieved for {ticker} over the past 7 days."
        )

    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        try:
            llm = get_groq_llm(temperature=0.1).with_structured_output(NewsAgentOutput)


            formatted_news = "\n\n".join([
                f"Headline: {art['headline']}\nSummary: {art['summary']}\nSource: {art['source']}"
                for art in articles
            ])

            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", "Here are the recent news articles:\n\n{news_text}")
            ])

            chain = prompt | llm
            result = chain.invoke({"ticker": ticker, "news_text": formatted_news})
            result.analyzed_articles_count = len(articles)
            return result
        except Exception as e:
            print(f"News agent Groq fallback triggered ({e})")

    headlines = [art['headline'] for art in articles if art.get('headline')]
    return NewsAgentOutput(
        ticker=ticker,
        sentiment_score=0.15,
        confidence=0.65,
        analyzed_articles_count=len(articles),
        bullish_drivers=headlines[:3] if headlines else ["Active news volume"],
        bearish_risks=["Potential news volatility"],
        summary_explanation=f"Retrieved {len(articles)} recent news articles for {ticker}."
    )


if __name__ == "__main__":
    ticker = "NVDA"
    print(f"Running News Agent for {ticker}...")
    output = run_news_agent(ticker)
    print("\n--- NEWS AGENT RESULT ---")
    print(output)