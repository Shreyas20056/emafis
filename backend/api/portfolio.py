from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, date

import asyncio
from concurrent.futures import ThreadPoolExecutor

from database import portfolio_collection
from models.schemas import (
    HoldingCreate, HoldingUpdate, TradeRequest,
    PortfolioAnalysisResponse, PortfolioActionResult, PortfolioSummary
)
from core.portfolio_logic import get_portfolio_action
from core.decision_engine import generate_final_decision
from core.xai import generate_xai_explanation
from services.market_data import get_current_price

from agents.news_agent import run_news_agent
from agents.technical_agent import run_technical_agent
from agents.risk_agent import run_risk_agent
from agents.macro_agent import run_macro_agent
from agents.fundamental_agent import run_fundamental_agent


router = APIRouter(prefix="/api/portfolio", tags=["Portfolio"])
executor = ThreadPoolExecutor(max_workers=6)

USER_ID = "demo_user"


def get_portfolio():
    doc = portfolio_collection.find_one({"user_id": USER_ID})
    if not doc:
        doc = {
            "user_id": USER_ID,
            "holdings": [],
            "updated_at": datetime.utcnow()
        }
        res = portfolio_collection.insert_one(doc)
        doc["_id"] = str(res.inserted_id)
    else:
        doc["_id"] = str(doc["_id"])
    return doc



from api.analysis import run_all_agents_parallel



@router.get("")
def read_portfolio():
    return get_portfolio()


@router.post("/holdings")
def add_holding(holding: HoldingCreate):
    doc = get_portfolio()
    holdings = doc.get("holdings", [])

    for h in holdings:
        if h["ticker"].upper() == holding.ticker.upper():
            raise HTTPException(400, "Holding already exists. Use update instead.")

    holdings.append({
        "ticker": holding.ticker.upper(),
        "quantity": holding.quantity,
        "avg_buy_price": holding.avg_buy_price,
        "buy_date": holding.buy_date.isoformat() if holding.buy_date else None
    })

    portfolio_collection.update_one(
        {"user_id": USER_ID},
        {"$set": {"holdings": holdings, "updated_at": datetime.utcnow()}},
        upsert=True
    )
    return {"message": "Holding added successfully", "holdings": holdings}


@router.put("/holdings/{ticker}")
def update_holding(ticker: str, data: HoldingUpdate):
    doc = get_portfolio()
    holdings = doc.get("holdings", [])
    found = False

    for h in holdings:
        if h["ticker"] == ticker.upper():
            if data.quantity is not None:
                h["quantity"] = data.quantity
            if data.avg_buy_price is not None:
                h["avg_buy_price"] = data.avg_buy_price
            if data.buy_date is not None:
                h["buy_date"] = data.buy_date.isoformat()
            found = True
            break

    if not found:
        raise HTTPException(404, "Holding not found")

    portfolio_collection.update_one(
        {"user_id": USER_ID},
        {"$set": {"holdings": holdings, "updated_at": datetime.utcnow()}}
    )
    return {"message": "Holding updated"}


@router.delete("/holdings/{ticker}")
def delete_holding(ticker: str):
    doc = get_portfolio()
    holdings = [h for h in doc.get("holdings", []) if h["ticker"] != ticker.upper()]

    portfolio_collection.update_one(
        {"user_id": USER_ID},
        {"$set": {"holdings": holdings, "updated_at": datetime.utcnow()}}
    )
    return {"message": "Holding removed"}


@router.post("/trade")
def record_trade(trade: TradeRequest):
    doc = get_portfolio()
    holdings = doc.get("holdings", [])
    ticker = trade.ticker.upper()

    existing = next((h for h in holdings if h["ticker"] == ticker), None)

    if trade.action.upper() == "BUY":
        if existing:
            total_cost = existing["avg_buy_price"] * existing["quantity"] + trade.price * trade.quantity
            new_qty = existing["quantity"] + trade.quantity
            existing["avg_buy_price"] = total_cost / new_qty
            existing["quantity"] = new_qty
        else:
            holdings.append({
                "ticker": ticker,
                "quantity": trade.quantity,
                "avg_buy_price": trade.price,
                "buy_date": (trade.date or date.today()).isoformat()
            })
    elif trade.action.upper() == "SELL":
        if not existing or existing["quantity"] < trade.quantity:
            raise HTTPException(400, "Not enough quantity to sell")
        existing["quantity"] -= trade.quantity
        if existing["quantity"] <= 0:
            holdings = [h for h in holdings if h["ticker"] != ticker]
    else:
        raise HTTPException(400, "action must be BUY or SELL")

    portfolio_collection.update_one(
        {"user_id": USER_ID},
        {"$set": {"holdings": holdings, "updated_at": datetime.utcnow()}}
    )
    return {"message": "Trade recorded", "holdings": holdings}


@router.post("/analyze", response_model=PortfolioAnalysisResponse)
async def analyze_portfolio():
    doc = get_portfolio()
    holdings = doc.get("holdings", [])

    if not holdings:
        raise HTTPException(400, "Portfolio is empty. Please add holdings first.")

    results = []
    total_invested = 0.0
    total_current = 0.0

    loop = asyncio.get_event_loop()

    for h in holdings:
        ticker = h["ticker"]
        quantity = h["quantity"]
        avg_price = h["avg_buy_price"]

        agent_results = await run_all_agents_parallel(ticker)

        decision = generate_final_decision(agent_results)
        current_price = get_current_price(ticker)

        action_data = get_portfolio_action(
            ticker=ticker,
            stock_action=decision["action"],
            confidence=decision["confidence"],
            quantity=quantity,
            avg_buy_price=avg_price,
            current_price=current_price
        )

        xai_text = generate_xai_explanation(
            ticker=ticker,
            action=decision["action"],
            confidence=decision["confidence"],
            regime=decision["market_regime"],
            weights=decision["dynamic_weights"],
            agent_results=agent_results
        )

        action_data["xai_summary"] = xai_text[:450] + "..." if len(xai_text) > 450 else xai_text
        results.append(PortfolioActionResult(**action_data))

        total_invested += avg_price * quantity
        total_current += current_price * quantity

    summary = PortfolioSummary(
        total_invested=round(total_invested, 2),
        current_value=round(total_current, 2),
        overall_pnl=round(total_current - total_invested, 2),
        overall_pnl_pct=round(((total_current - total_invested) / total_invested) * 100, 2) if total_invested > 0 else 0.0
    )

    return PortfolioAnalysisResponse(
        portfolio_summary=summary,
        holdings=results
    )


class PortfolioChatRequest(BaseModel):

    message: str
    history: list[dict] = []


@router.post("/chat")
def chat_portfolio(req: PortfolioChatRequest):
    """
    Real-time Multi-Agent Portfolio Chat Advisor endpoint.
    Discusses investment strategy, asset allocation, dip buying, and risk management.
    """
    doc = get_portfolio()
    holdings = doc.get("holdings", [])

    holdings_summary = []
    total_val = 0.0
    for h in holdings:
        t = h["ticker"]
        q = h["quantity"]
        p = h["avg_buy_price"]
        cur = get_current_price(t) or p
        val = cur * q
        total_val += val
        pnl = ((cur - p) / p * 100) if p > 0 else 0
        holdings_summary.append(f"{t}: {q} qty @ ₹{p:.2f} (Current ₹{cur:.2f}, PnL {pnl:+.2f}%)")

    portfolio_context = "\n".join(holdings_summary) if holdings_summary else "No current positions (empty portfolio)."

    user_msg = req.message.strip()
    if not user_msg:
        raise HTTPException(400, "Message cannot be empty")

    from core.llm import get_groq_llm
    from langchain_core.prompts import ChatPromptTemplate

    system_prompt = """
You are the EMAFIS Portfolio Intelligence Chat Assistant, a senior SEBI-style wealth manager advising on Indian equity portfolios.
You provide real-time investment advice, asset allocation strategies, dip buying options, and risk management plans.

Current User Portfolio Context (Values in ₹ INR):
Total Asset Valuation: ₹{total_val:.2f}
Holdings:
{portfolio_context}

Rules:
1. Always frame prices and portfolio values in Indian Rupees (₹).
2. Give clear, strategic, and actionable advice tailored to NIFTY 50 and NIFTY SmallCap Indian equities.
3. Be professional, honest about risk, and concise (max 160 words).
"""

    try:
        llm = get_groq_llm(temperature=0.3)
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{user_message}")
        ])
        chain = prompt | llm
        res = chain.invoke({
            "total_val": total_val,
            "portfolio_context": portfolio_context,
            "user_message": user_msg
        })
        reply_text = str(res.content)
    except Exception as e:
        print(f"Portfolio chat Groq fallback ({e})")
        reply_text = (
            f"Based on your current portfolio valuation of ₹{total_val:.2f} across {len(holdings)} holdings: "
            f"For your query '{user_msg}', consider maintaining a balanced allocation across defensive NIFTY 50 leaders "
            f"and high-growth SmallCap stocks. Use systematic dip buying (SIP/staggered entry) during market corrections."
        )

    return {
        "reply": reply_text,
        "timestamp": datetime.utcnow().isoformat()
    }