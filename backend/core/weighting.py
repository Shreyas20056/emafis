from typing import Dict

def detect_market_regime(
    technical_score: float,
    risk_score: float,
    news_score: float,
    volatility: float = 25.0
) -> str:
    """
    Detect current market regime based on agent signals.
    """
    if abs(news_score) > 0.55:
        return "news_driven"
    if volatility > 35 or risk_score < -0.40:
        return "high_volatility"
    if technical_score > 0.40:
        return "trending_bullish"
    if technical_score < -0.40:
        return "trending_bearish"
    return "neutral"


def compute_dynamic_weights(regime: str) -> Dict[str, float]:
    """
    Base Dynamic Weighting based on market regime.
    This is the core research contribution.
    """
    base = {
        "news": 0.18,
        "technical": 0.25,
        "risk": 0.20,
        "macro": 0.17,
        "fundamental": 0.20
    }

    if regime == "news_driven":
        base["news"] += 0.17
        base["technical"] -= 0.07
        base["fundamental"] -= 0.05
        base["macro"] -= 0.05

    elif regime == "high_volatility":
        base["risk"] += 0.18
        base["technical"] -= 0.08
        base["news"] -= 0.05
        base["fundamental"] -= 0.05

    elif regime == "trending_bullish":
        base["technical"] += 0.14
        base["risk"] -= 0.07
        base["news"] -= 0.04
        base["macro"] -= 0.03

    elif regime == "trending_bearish":
        base["technical"] += 0.08
        base["risk"] += 0.10
        base["news"] -= 0.05
        base["fundamental"] -= 0.05
        base["macro"] -= 0.08

    # Normalize so weights sum to 1.0
    total = sum(base.values())
    return {k: round(v / total, 4) for k, v in base.items()}