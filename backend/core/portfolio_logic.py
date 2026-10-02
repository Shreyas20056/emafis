from typing import Dict, Any


def get_portfolio_action(
    ticker: str,
    stock_action: str,
    confidence: float,
    quantity: float,
    avg_buy_price: float,
    current_price: float
) -> Dict[str, Any]:
    """
    Evaluates stock recommendation in the context of user's existing portfolio position.
    Calculates PnL and recommends portfolio action (e.g. ACCUMULATE, TAKE_PROFIT, STOP_LOSS, HOLD).
    """
    if avg_buy_price > 0:
        pnl_pct = round(((current_price - avg_buy_price) / avg_buy_price) * 100, 2)
        unrealized_pnl = round((current_price - avg_buy_price) * quantity, 2)
    else:
        pnl_pct = 0.0
        unrealized_pnl = 0.0

    action_upper = stock_action.upper()

    if action_upper == "BUY":
        if pnl_pct < -8.0:
            portfolio_action = "BUY_DIP"
        else:
            portfolio_action = "ACCUMULATE"
    elif action_upper == "SELL":
        if pnl_pct > 5.0:
            portfolio_action = "TAKE_PROFIT"
        elif pnl_pct < -12.0:
            portfolio_action = "STOP_LOSS"
        else:
            portfolio_action = "REDUCE"
    else:
        portfolio_action = "HOLD"

    return {
        "ticker": ticker,
        "portfolio_action": portfolio_action,
        "stock_action": stock_action,
        "confidence": confidence,
        "quantity": quantity,
        "avg_buy_price": avg_buy_price,
        "current_price": current_price,
        "pnl_pct": pnl_pct,
        "unrealized_pnl": unrealized_pnl,
        "xai_summary": ""
    }
