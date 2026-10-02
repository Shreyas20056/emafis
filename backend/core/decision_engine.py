from typing import Dict
from app.core.weighting import detect_market_regime
from app.core.learning import compute_adaptive_weights, get_agent_performance


def generate_final_decision(agent_results: Dict) -> dict:
    """
    Collaborative Decision Engine.
    Combines all agent scores using Adaptive Dynamic Weights.
    """
    scores = {
        "news": agent_results["news"].sentiment_score,
        "technical": agent_results["technical"].technical_score,
        "risk": agent_results["risk"].risk_score,
        "macro": agent_results["macro"].macro_score,
        "fundamental": agent_results["fundamental"].valuation_score,
    }

    confidences = {
        "news": agent_results["news"].confidence,
        "technical": agent_results["technical"].confidence,
        "risk": agent_results["risk"].confidence,
        "macro": agent_results["macro"].confidence,
        "fundamental": agent_results["fundamental"].confidence,
    }

    # Detect regime
    regime = detect_market_regime(
        technical_score=scores["technical"],
        risk_score=scores["risk"],
        news_score=scores["news"]
    )

    # Adaptive weights (regime + learning)
    weights = compute_adaptive_weights(regime, get_agent_performance())

    # Final weighted score
    weighted_score = sum(scores[agent] * weights[agent] for agent in weights)

    # Decision thresholds
    if weighted_score >= 0.28:
        action = "BUY"
    elif weighted_score <= -0.28:
        action = "SELL"
    else:
        action = "HOLD"

    # Confidence calculation (0-100)
    avg_conf = sum(confidences.values()) / len(confidences)
    strength = min(abs(weighted_score) * 1.35, 0.55)
    confidence = round((avg_conf * 0.55 + strength + 0.22) * 100, 1)
    confidence = max(38.0, min(confidence, 95.0))

    return {
        "action": action,
        "confidence": confidence,
        "weighted_score": round(weighted_score, 4),
        "market_regime": regime,
        "dynamic_weights": weights,
        "scores": scores,
        "confidences": confidences
    }