from typing import Dict
from datetime import datetime

# In-memory performance (can later move to MongoDB)
AGENT_PERFORMANCE: Dict[str, float] = {
    "news": 0.55,
    "technical": 0.60,
    "risk": 0.52,
    "macro": 0.50,
    "fundamental": 0.58
}


def update_agent_performance(agent_correctness: Dict[str, bool]):
    """
    Update agent performance using exponential moving average.
    Called after evaluating past recommendations.
    """
    alpha = 0.15  # learning rate

    for agent, was_correct in agent_correctness.items():
        if was_correct is None:
            continue
        current = AGENT_PERFORMANCE.get(agent, 0.5)
        target = 1.0 if was_correct else 0.0
        AGENT_PERFORMANCE[agent] = round(current * (1 - alpha) + target * alpha, 4)


def get_agent_performance() -> Dict[str, float]:
    return AGENT_PERFORMANCE.copy()


def compute_adaptive_weights(regime: str, agent_performance: Dict[str, float] = None) -> Dict[str, float]:
    """
    Final Adaptive Dynamic Weighting.
    Combines regime-based weights + historical agent accuracy.
    """
    from core.weighting import compute_dynamic_weights


    if agent_performance is None:
        agent_performance = get_agent_performance()

    weights = compute_dynamic_weights(regime)

    # Reward / penalize based on recent accuracy
    for agent, accuracy in agent_performance.items():
        if accuracy >= 0.65:
            weights[agent] *= 1.18
        elif accuracy <= 0.45:
            weights[agent] *= 0.82

    # Normalize
    total = sum(weights.values())
    return {k: round(v / total, 4) for k, v in weights.items()}