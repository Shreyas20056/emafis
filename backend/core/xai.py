from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


def generate_xai_explanation(
    ticker: str,
    action: str,
    confidence: float,
    regime: str,
    weights: dict,
    agent_results: dict
) -> str:
    """
    Generate human-readable explanation for the recommendation.
    """
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.25
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are the Explainable AI module of EMAFIS (Explainable Multi-Agent Financial Intelligence System).
Your job is to write a clear, professional, and transparent explanation for retail and serious investors.

Structure the explanation in 3-4 short paragraphs:
1. Final recommendation and confidence level.
2. Current market regime and how it affected agent weights.
3. Which agents contributed most (and least) and why.
4. Key supporting signals and any conflicting signals.

Rules:
- Be honest about uncertainty.
- Do not invent numbers.
- Keep language simple but professional.
- Maximum 180 words."""),
        ("human", """
Ticker: {ticker}
Final Action: {action}
Confidence: {confidence}%
Market Regime: {regime}
Dynamic Weights: {weights}

Agent Summaries:
- News: {news}
- Technical: {technical}
- Risk: {risk}
- Macro: {macro}
- Fundamental: {fundamental}
""")
    ])

    chain = prompt | llm

    response = chain.invoke({
        "ticker": ticker,
        "action": action,
        "confidence": confidence,
        "regime": regime,
        "weights": weights,
        "news": agent_results["news"].summary_explanation,
        "technical": agent_results["technical"].summary_explanation,
        "risk": agent_results["risk"].summary_explanation,
        "macro": agent_results["macro"].summary_explanation,
        "fundamental": agent_results["fundamental"].summary_explanation,
    })

    return response.content