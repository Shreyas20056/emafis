from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime, date


class AgentContribution(BaseModel):
    agent: str
    score: float
    weight: float
    weighted_score: float
    confidence: float
    key_factors: List[str]
    summary: str


class AnalysisResponse(BaseModel):
    ticker: str
    action: str
    confidence: float
    weighted_score: float
    market_regime: str
    dynamic_weights: Dict[str, float]
    agent_contributions: List[AgentContribution]
    xai_explanation: str
    timestamp: str
    price_at_recommendation: Optional[float] = None


class HoldingCreate(BaseModel):
    ticker: str
    quantity: float = Field(..., gt=0)
    avg_buy_price: float = Field(..., gt=0)
    buy_date: Optional[date] = None


class HoldingUpdate(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    avg_buy_price: Optional[float] = Field(None, gt=0)
    buy_date: Optional[date] = None


class TradeRequest(BaseModel):
    ticker: str
    action: str = Field(..., pattern="^(BUY|SELL)$")
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0)
    date: Optional[date] = None


class PortfolioActionResult(BaseModel):
    ticker: str
    portfolio_action: str
    stock_action: str
    confidence: float
    quantity: float
    avg_buy_price: float
    current_price: float
    pnl_pct: float
    unrealized_pnl: float
    xai_summary: str


class PortfolioSummary(BaseModel):
    total_invested: float
    current_value: float
    overall_pnl: float
    overall_pnl_pct: float


class PortfolioAnalysisResponse(BaseModel):
    portfolio_summary: PortfolioSummary
    holdings: List[PortfolioActionResult]