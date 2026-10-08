from typing import Dict
from datetime import datetime
from database import agent_performance_collection

DEFAULT_AGENT_PERFORMANCE: Dict[str, float] = {
    "news": 0.55,
    "technical": 0.60,
    "risk": 0.52,
    "macro": 0.50,
    "fundamental": 0.58
}


def init_agent_performance():
    """Ensure MongoDB agent_performance collection contains documents for all agents."""
    try:
        if agent_performance_collection.count_documents({}) == 0:
            now = datetime.utcnow()
            docs = [
                {
                    "agent": agent,
                    "accuracy": initial_acc,
                    "total_evaluations": 0,
                    "correct_predictions": 0,
                    "updated_at": now
                }
                for agent, initial_acc in DEFAULT_AGENT_PERFORMANCE.items()
            ]
            agent_performance_collection.insert_many(docs)
            print("[OK] Initialized MongoDB collection 'agent_performance' with baseline agent accuracy data")
    except Exception as e:
        print(f"[WARN] Error initializing MongoDB agent_performance collection: {e}")


def get_agent_performance() -> Dict[str, float]:
    """Retrieve live agent accuracy metrics from MongoDB, seeding initial defaults if empty."""
    init_agent_performance()
    try:
        cursor = agent_performance_collection.find({})
        perf_map = {}
        for doc in cursor:
            perf_map[doc["agent"]] = float(doc.get("accuracy", 0.50))
        if perf_map:
            # Ensure all 5 agents are present
            for agent, default_val in DEFAULT_AGENT_PERFORMANCE.items():
                if agent not in perf_map:
                    perf_map[agent] = default_val
            return perf_map
    except Exception as e:
        print(f"[WARN] Error loading agent performance from MongoDB: {e}")
    
    return DEFAULT_AGENT_PERFORMANCE.copy()


def update_agent_performance(agent_correctness: Dict[str, bool]):
    """
    Update agent performance using Exponential Moving Average (EMA) and persist directly to MongoDB.
    Called after evaluating 5-day recommendation outcomes.
    """
    init_agent_performance()
    alpha = 0.15  # learning rate

    for agent, was_correct in agent_correctness.items():
        if was_correct is None:
            continue
        
        current_perf = get_agent_performance()
        current_acc = current_perf.get(agent, 0.50)
        target = 1.0 if was_correct else 0.0
        new_acc = round(current_acc * (1 - alpha) + target * alpha, 4)

        try:
            inc_correct = 1 if was_correct else 0
            agent_performance_collection.update_one(
                {"agent": agent},
                {
                    "$set": {
                        "accuracy": new_acc,
                        "updated_at": datetime.utcnow()
                    },
                    "$inc": {
                        "total_evaluations": 1,
                        "correct_predictions": inc_correct
                    }
                },
                upsert=True
            )
            print(f"[INFO] Updated agent '{agent}' accuracy in MongoDB: {current_acc} -> {new_acc}")
        except Exception as e:
            print(f"[WARN] Error updating agent_performance collection for {agent}: {e}")



def compute_adaptive_weights(regime: str, agent_performance: Dict[str, float] = None) -> Dict[str, float]:
    """
    Adaptive Dynamic Weighting Engine.
    Combines regime-based base weights + historical agent accuracy from MongoDB.
    """
    from core.weighting import compute_dynamic_weights

    if agent_performance is None:
        agent_performance = get_agent_performance()

    weights = compute_dynamic_weights(regime)

    # Reward / penalize based on recent accuracy from MongoDB
    for agent, accuracy in agent_performance.items():
        if accuracy >= 0.65:
            weights[agent] *= 1.18
        elif accuracy <= 0.45:
            weights[agent] *= 0.82

    # Normalize so weights sum to 1.0
    total = sum(weights.values())
    return {k: round(v / total, 4) for k, v in weights.items()}