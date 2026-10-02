import os
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
    Generate human-readable explanation for the recommendation with fallback support.
    """
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.25,
            groq_api_key=api_key
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
            "news": getattr(agent_results["news"], "summary_explanation", ""),
            "technical": getattr(agent_results["technical"], "summary_explanation", ""),
            "risk": getattr(agent_results["risk"], "summary_explanation", ""),
            "macro": getattr(agent_results["macro"], "summary_explanation", ""),
            "fundamental": getattr(agent_results["fundamental"], "summary_explanation", ""),
        })

        return str(response.content)
    except Exception as e:
        print(f"XAI Groq generation fallback triggered ({e})")
        top_weight_agent = max(weights, key=weights.get) if weights else "technical"
        top_agent_weight = weights.get(top_weight_agent, 0.0) if weights else 0.0
        return (
            f"EMAFIS generated a final recommendation of {action} for {ticker} with {confidence}% system confidence. "
            f"Under the current '{regime.replace('_', ' ')}' regime, the highest weight was allocated to the {top_weight_agent} agent ({top_agent_weight:.0%}). "
            f"Summary insights — Technical: {getattr(agent_results.get('technical'), 'summary_explanation', 'N/A')}. "
            f"Fundamental: {getattr(agent_results.get('fundamental'), 'summary_explanation', 'N/A')}. "
            f"Risk Assessment: {getattr(agent_results.get('risk'), 'summary_explanation', 'N/A')}."
        )