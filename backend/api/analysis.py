from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from models.schemas import AnalysisResponse, AgentContribution
from core.decision_engine import generate_final_decision
from core.xai import generate_xai_explanation
from services.market_data import get_current_price, get_ohlcv
from services.evaluation import evaluate_pending_recommendations
from database import recommendations_collection

from agents.news_agent import run_news_agent
from agents.technical_agent import run_technical_agent
from agents.risk_agent import run_risk_agent
from agents.macro_agent import run_macro_agent
from agents.fundamental_agent import run_fundamental_agent


router = APIRouter(prefix="/api", tags=["Analysis"])
executor = ThreadPoolExecutor(max_workers=10)


async def run_all_agents_parallel(ticker: str) -> dict:
    """Execute all 5 specialized agents in parallel for maximum performance."""
    loop = asyncio.get_running_loop()
    news_future = loop.run_in_executor(executor, run_news_agent, ticker)
    tech_future = loop.run_in_executor(executor, run_technical_agent, ticker)
    risk_future = loop.run_in_executor(executor, run_risk_agent, ticker)
    macro_future = loop.run_in_executor(executor, run_macro_agent, ticker)
    fund_future = loop.run_in_executor(executor, run_fundamental_agent, ticker)

    news_res, tech_res, risk_res, macro_res, fund_res = await asyncio.gather(
        news_future, tech_future, risk_future, macro_future, fund_future
    )

    return {
        "news": news_res,
        "technical": tech_res,
        "risk": risk_res,
        "macro": macro_res,
        "fundamental": fund_res,
    }


@router.post("/analyze/{ticker}", response_model=AnalysisResponse)
async def analyze_stock(ticker: str):
    ticker = ticker.upper().strip()

    try:
        agent_results = await run_all_agents_parallel(ticker)

        decision = generate_final_decision(agent_results)
        current_price = get_current_price(ticker)

        contributions = []
        for name in ["news", "technical", "risk", "macro", "fundamental"]:
            result = agent_results[name]
            score = decision["scores"][name]
            weight = decision["dynamic_weights"][name]
            conf = decision["confidences"][name]

            if name == "news":
                factors = (getattr(result, "bullish_drivers", []) or []) + (getattr(result, "bearish_risks", []) or [])
                summary = getattr(result, "summary_explanation", "")
            elif name == "technical":
                factors = getattr(result, "key_signals", []) or []
                summary = getattr(result, "summary_explanation", "")
            elif name == "risk":
                factors = getattr(result, "key_risk_flags", []) or []
                summary = getattr(result, "summary_explanation", "")
            elif name == "macro":
                factors = getattr(result, "key_macro_factors", []) or []
                summary = getattr(result, "summary_explanation", "")
            else:
                factors = getattr(result, "key_fundamental_drivers", []) or []
                summary = getattr(result, "summary_explanation", "")

            contributions.append(AgentContribution(
                agent=name,
                score=round(score, 4),
                weight=weight,
                weighted_score=round(score * weight, 4),
                confidence=round(conf, 3),
                key_factors=factors[:6],
                summary=summary
            ))

        xai_text = generate_xai_explanation(
            ticker=ticker,
            action=decision["action"],
            confidence=decision["confidence"],
            regime=decision["market_regime"],
            weights=decision["dynamic_weights"],
            agent_results=agent_results
        )

        response = AnalysisResponse(
            ticker=ticker,
            action=decision["action"],
            confidence=decision["confidence"],
            weighted_score=decision["weighted_score"],
            market_regime=decision["market_regime"],
            dynamic_weights=decision["dynamic_weights"],
            agent_contributions=contributions,
            xai_explanation=xai_text,
            timestamp=datetime.utcnow().isoformat(),
            price_at_recommendation=current_price
        )

        # Save for learning + research tracking
        try:
            rec_id = recommendations_collection.insert_one({
                "ticker": ticker,
                "action": decision["action"],
                "confidence": decision["confidence"],
                "weighted_score": decision["weighted_score"],
                "market_regime": decision["market_regime"],
                "dynamic_weights": decision["dynamic_weights"],
                "agent_scores": decision["scores"],
                "price_at_recommendation": current_price,
                "xai_explanation": xai_text,
                "created_at": datetime.utcnow(),
                "evaluated": False
            }).inserted_id
            print(f"[INFO] Saved recommendation to MongoDB collection 'recommendations' (ID: {rec_id})")
        except Exception as db_err:
            print(f"[WARN] Error saving recommendation to MongoDB: {db_err}")

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/chart/{ticker}")
def get_chart_data(ticker: str, period: str = "3mo"):
    data = get_ohlcv(ticker, period=period)
    return {"ticker": ticker.upper(), "candles": data}


@router.get("/recommendations/history")
def get_recommendations_history(limit: int = 20):
    docs = list(recommendations_collection.find({}, sort=[("created_at", -1)]).limit(limit))
    for d in docs:
        d["_id"] = str(d["_id"])
        if isinstance(d.get("created_at"), datetime):
            d["created_at"] = d["created_at"].isoformat()
    return {"recommendations": docs}


@router.get("/analyze/{ticker}/latest")
def get_latest_analysis(ticker: str):
    ticker = ticker.upper().strip()
    doc = recommendations_collection.find_one(
        {"ticker": ticker},
        sort=[("created_at", -1)]
    )
    if not doc:
        raise HTTPException(status_code=404, detail="No previous analysis found")
    doc["_id"] = str(doc["_id"])
    if isinstance(doc.get("created_at"), datetime):
        doc["created_at"] = doc["created_at"].isoformat()
    return doc


@router.post("/evaluate")
@router.get("/evaluate")
def run_evaluation(days: int = Query(default=5, ge=0)):
    """Run outcome evaluation loop on past recommendations to update agent performance weights."""
    try:
        evaluate_pending_recommendations(days=days)
        return {"status": "success", "message": f"Evaluation completed for recommendations older than {days} days"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.get("/export/recommendations")
def export_recommendations(format: str = Query(default="json", pattern="^(json|csv)$")):

    """Export recommendation data for offline backtesting and research reproducibility."""
    docs = list(recommendations_collection.find({}, {"_id": 0}))
    for d in docs:
        if isinstance(d.get("created_at"), datetime):
            d["created_at"] = d["created_at"].isoformat()

    if format == "json":
        return {"count": len(docs), "data": docs}
    else:
        # CSV output
        import io
        import csv
        from fastapi.responses import Response

        output = io.StringIO()
        if docs:
            fieldnames = list(docs[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for doc in docs:
                # Stringify dict fields for CSV clean format
                clean_doc = {
                    k: (str(v) if isinstance(v, (dict, list)) else v)
                    for k, v in doc.items()
                }
                writer.writerow(clean_doc)
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=emafis_recommendations.csv"}
        )