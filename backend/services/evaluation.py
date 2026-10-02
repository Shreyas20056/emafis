import yfinance as yf
from datetime import datetime, timedelta
from app.database import recommendations_collection
from app.core.learning import update_agent_performance

def evaluate_pending_recommendations(days: int = 5):
    """
    Run this once per day (or manually for demo).
    Checks all recommendations older than `days` that are not yet evaluated.
    """
    cutoff = datetime.utcnow() - timedelta(days=days)

    pending = recommendations_collection.find({
        "evaluated": False,
        "created_at": {"$lte": cutoff}
    })

    for rec in pending:
        ticker = rec["ticker"]
        # Handle Indian stocks
        yf_ticker = f"{ticker}.NS" if not ticker.endswith(".NS") and ticker.isalpha() else ticker

        try:
            data = yf.Ticker(yf_ticker).history(period="15d")
            if data.empty:
                continue

            price_then = rec["price_at_recommendation"]
            price_now = data["Close"].iloc[-1]
            actual_return = ((price_now - price_then) / price_then) * 100

            # Decide outcome
            action = rec["action"]
            if action == "BUY":
                outcome = "correct" if actual_return > 1.5 else ("incorrect" if actual_return < -1.5 else "neutral")
            elif action == "SELL":
                outcome = "correct" if actual_return < -1.5 else ("incorrect" if actual_return > 1.5 else "neutral")
            else:  # HOLD
                outcome = "correct" if abs(actual_return) < 2.5 else "incorrect"

            # Agent correctness (simple directional check)
            agent_correctness = {}
            for agent, score in rec["agent_scores"].items():
                if outcome == "neutral":
                    agent_correctness[agent] = None
                elif (score > 0.15 and actual_return > 0) or (score < -0.15 and actual_return < 0):
                    agent_correctness[agent] = True
                elif abs(score) < 0.15:
                    agent_correctness[agent] = None
                else:
                    agent_correctness[agent] = False

            # Update the document
            recommendations_collection.update_one(
                {"_id": rec["_id"]},
                {"$set": {
                    "evaluated": True,
                    "price_after_5d": float(price_now),
                    "actual_return_5d": round(actual_return, 2),
                    "outcome": outcome,
                    "agent_correctness": agent_correctness
                }}
            )

            # Update live agent performance
            update_agent_performance(agent_correctness)

            print(f"Evaluated {ticker} → {outcome} ({actual_return:.2f}%)")

        except Exception as e:
            print(f"Error evaluating {ticker}: {e}")