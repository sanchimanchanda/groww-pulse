from sqlalchemy.orm import Session
from datetime import datetime
from . import models
from .thesis import evaluate_thesis
from .valuation import classify_valuation

def inject_personal_context(changes: list, user_id: int, watchlist_id: int, db: Session) -> list:
    """
    Takes a list of dictionary 'changes' (the output of the Signal engine) and
    injects personal context where available without mutating the original schema structure.
    """
    if not changes:
        return changes
        
    out = []
    now = datetime.utcnow()
    
    # Pre-fetch user funds for overlap checks
    user_funds = db.query(models.UserMutualFund).filter_by(user_id=user_id).all()
    user_fund_ids = [uf.fund_id for uf in user_funds]
    
    for c in changes:
        enriched = dict(c)
        symbol = c["symbol"]
        stock = db.query(models.Stock).filter_by(symbol=symbol).first()
        if not stock:
            out.append(enriched)
            continue
            
        personal_context = {}
        
        # 1. Thesis Context
        thesis = db.query(models.StockThesis).filter_by(watchlist_id=watchlist_id, stock_id=stock.id).first()
        if thesis:
            review = evaluate_thesis(thesis.thesis_type, c.get("evidence", {}))
            personal_context["thesis"] = {
                "type": thesis.thesis_type,
                "note": thesis.thesis_note,
                "status": review["status"],
                "action": review["reason"]
            }
            
        # 2. Valuation Context
        val = db.query(models.StockValuation).filter_by(stock_id=stock.id).first()
        if val:
            classification = classify_valuation(
                val.current_pe,
                val.historical_pe_median,
                val.historical_pe_low,
                val.historical_pe_high
            )
            personal_context["valuation"] = {
                "current_pe": val.current_pe,
                "label": classification["label"],
                "delta_pct": classification["delta_vs_median_pct"]
            }
            
        # 3. Event Context
        events = db.query(models.StockEvent).filter_by(stock_id=stock.id).all()
        upcoming_events = []
        for e in events:
            days_until = (e.event_date - now).days
            if 0 <= days_until <= 30: # Only care about near-term events for context
                upcoming_events.append({
                    "type": e.event_type,
                    "title": e.title,
                    "days_until": days_until
                })
        if upcoming_events:
            # sort by closest
            upcoming_events.sort(key=lambda x: x["days_until"])
            personal_context["events"] = upcoming_events
            
        # 4. Overlap Context
        # Find if this stock is in any of the user's mutual funds
        fund_overlaps = []
        for fund_id in user_fund_ids:
            holding = db.query(models.MutualFundHolding).filter_by(fund_id=fund_id, symbol=symbol).first()
            if holding:
                fund = db.query(models.MutualFund).filter_by(id=fund_id).first()
                fund_overlaps.append({
                    "fund_name": fund.name,
                    "weight": holding.weight
                })
        if fund_overlaps:
            personal_context["fund_overlap"] = fund_overlaps
            
        if personal_context:
            enriched["personal_context"] = personal_context
            
        out.append(enriched)
        
    return out
