import time
from datetime import datetime, timezone
from threading import Lock
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from . import models, demo_data
from .database import Base, engine, get_db, SessionLocal
from .engine import MarketSnapshot, evaluate, Freshness, detect_market_regime, calculate_attention
from .models import VALID_GOALS, VALID_HORIZONS, VALID_THESIS_TYPES
from .valuation import classify_valuation
from .sip import evaluate_sip_context
from .personal_context import inject_personal_context

app = FastAPI(title="Groww Pulse API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # hackathon demo scope only — see TRADEOFFS.md
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

DEMO_USER_ID = 1

# In-memory demo controls. A real deployment replaces this module with a
# scheduled worker hitting a real market data vendor (see ARCHITECTURE.md
# "Background processing"); the API surface (get_watchlist_changes etc.)
# does not change either way.
_state_lock = Lock()
_active_scenario = "normal_market"
_metrics = {
    "requests_total": 0,
    "signal_computations_total": 0,
    "failed_data_requests_total": 0,
    "last_signal_latency_ms": 0.0,
}


def seed(db: Session):
    if not db.query(models.User).filter_by(id=DEMO_USER_ID).first():
        db.add(models.User(id=DEMO_USER_ID, email="demo@growwpulse.app"))
    for s in demo_data.STOCKS:
        if not db.query(models.Stock).filter_by(symbol=s["symbol"]).first():
            db.add(models.Stock(symbol=s["symbol"], name=s["name"], sector=s["sector"]))
    db.commit()

    wl = db.query(models.Watchlist).filter_by(user_id=DEMO_USER_ID).first()
    if not wl:
        wl = models.Watchlist(user_id=DEMO_USER_ID, name="My Watchlist")
        db.add(wl)
        db.commit()
        db.refresh(wl)
        for s in demo_data.STOCKS:
            stock = db.query(models.Stock).filter_by(symbol=s["symbol"]).first()
            db.add(models.WatchlistItem(watchlist_id=wl.id, stock_id=stock.id))
        db.commit()

    if not db.query(models.MutualFund).first():
        f1 = models.MutualFund(name="Parag Parikh Flexi Cap", category="Flexi Cap", expense_ratio=0.63)
        f2 = models.MutualFund(name="HDFC Flexi Cap", category="Flexi Cap", expense_ratio=0.85)
        db.add_all([f1, f2])
        db.commit()
        
        holdings1 = [
            models.MutualFundHolding(fund_id=f1.id, symbol="INFY", weight=8.2),
            models.MutualFundHolding(fund_id=f1.id, symbol="HDFCBANK", weight=6.7),
            models.MutualFundHolding(fund_id=f1.id, symbol="ICICIBANK", weight=5.9),
            models.MutualFundHolding(fund_id=f1.id, symbol="TCS", weight=4.8),
            models.MutualFundHolding(fund_id=f1.id, symbol="ITC", weight=3.1),
        ]
        holdings2 = [
            models.MutualFundHolding(fund_id=f2.id, symbol="HDFCBANK", weight=7.8),
            models.MutualFundHolding(fund_id=f2.id, symbol="ITC", weight=6.9),
            models.MutualFundHolding(fund_id=f2.id, symbol="INFY", weight=6.2),
            models.MutualFundHolding(fund_id=f2.id, symbol="SBIN", weight=4.8),
            models.MutualFundHolding(fund_id=f2.id, symbol="LT", weight=3.5),
        ]
        db.add_all(holdings1 + holdings2)
        db.add(models.UserMutualFund(user_id=DEMO_USER_ID, fund_id=f1.id))
        db.add(models.UserMutualFund(user_id=DEMO_USER_ID, fund_id=f2.id))
        db.commit()

    if not db.query(models.StockValuation).first():
        valuations = [
            {"symbol": "RELIANCE", "pe": 28.5, "median": 26.0, "low": 20.0, "high": 35.0},
            {"symbol": "TCS", "pe": 31.2, "median": 30.0, "low": 24.0, "high": 38.0},
            {"symbol": "HDFCBANK", "pe": 15.4, "median": 18.0, "low": 13.0, "high": 22.0},
            {"symbol": "ICICIBANK", "pe": 17.8, "median": 18.5, "low": 12.0, "high": 24.0},
            {"symbol": "INFY", "pe": 22.4, "median": 28.1, "low": 19.0, "high": 34.0},
            {"symbol": "ITC", "pe": 26.5, "median": 22.0, "low": 16.0, "high": 30.0},
            {"symbol": "SBIN", "pe": 10.2, "median": 12.0, "low": 7.0, "high": 16.0},
            {"symbol": "BHARTIARTL", "pe": 45.6, "median": 42.0, "low": 28.0, "high": 60.0},
            {"symbol": "BAJFINANCE", "pe": 32.1, "median": 40.0, "low": 25.0, "high": 55.0},
            {"symbol": "LT", "pe": 35.4, "median": 28.0, "low": 20.0, "high": 42.0},
        ]
        for v in valuations:
            stock = db.query(models.Stock).filter_by(symbol=v["symbol"]).first()
            if stock:
                db.add(models.StockValuation(
                    stock_id=stock.id,
                    current_pe=v["pe"],
                    historical_pe_median=v["median"],
                    historical_pe_low=v["low"],
                    historical_pe_high=v["high"]
                ))
        db.commit()

    if not db.query(models.StockEvent).first():
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        infy = db.query(models.Stock).filter_by(symbol="INFY").first()
        if infy:
            db.add(models.StockEvent(
                stock_id=infy.id,
                event_type="EARNINGS",
                event_date=now + timedelta(days=14),
                title="Q2 Results"
            ))
        hdfc = db.query(models.Stock).filter_by(symbol="HDFCBANK").first()
        if hdfc:
            db.add(models.StockEvent(
                stock_id=hdfc.id,
                event_type="DIVIDEND",
                event_date=now + timedelta(days=21),
                title="Interim Dividend (₹19.5/sh)"
            ))
        db.commit()

    if not db.query(models.UserSIP).filter_by(user_id=DEMO_USER_ID).first():
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        db.add(models.UserSIP(
            user_id=DEMO_USER_ID,
            instrument="NIFTY 50 Index Fund",
            sip_amount=5000.0,
            frequency="MONTHLY",
            next_sip_date=now + timedelta(days=3)
        ))
        db.commit()



@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


@app.middleware("http")
async def count_requests(request, call_next):
    _metrics["requests_total"] += 1
    return await call_next(request)


# ---------- market data provider (demo-backed) ----------

def fetch_snapshot(symbol: str) -> MarketSnapshot:
    """Simulates a market data fetch. Real implementation would call a
    vendor API here with a timeout + retry budget (see ARCHITECTURE.md
    'Data freshness & resilience'); the return contract (MarketSnapshot,
    always populated, never raises) stays identical."""
    rows = demo_data.SCENARIOS[_active_scenario]()
    row = next((r for r in rows if r["symbol"] == symbol), None)
    if row is None:
        _metrics["failed_data_requests_total"] += 1
        return MarketSnapshot(
            symbol=symbol, price=0, prev_close=0, volume=0, avg_volume_20d=0,
            avg_daily_move_20d=1, benchmark_pct_change=0, history_days=0,
            freshness=Freshness.UNAVAILABLE,
        )
    if row["freshness"] == Freshness.UNAVAILABLE:
        _metrics["failed_data_requests_total"] += 1
    return MarketSnapshot(
        symbol=row["symbol"], price=row["price"], prev_close=row["prev_close"],
        volume=row["volume"], avg_volume_20d=row["avg_volume_20d"],
        avg_daily_move_20d=row["avg_daily_move_20d"],
        benchmark_pct_change=row["benchmark_pct_change"],
        history_days=row["history_days"], freshness=row["freshness"],
        source_timestamp=datetime.now(timezone.utc).isoformat(),
        received_at=datetime.now(timezone.utc).isoformat(),
    )


def upsert_market_snapshot(db: Session, stock: models.Stock, snap: MarketSnapshot):
    row = db.query(models.MarketSnapshotRow).filter_by(stock_id=stock.id).first()
    if row is None:
        row = models.MarketSnapshotRow(stock_id=stock.id)
        db.add(row)
    if snap.freshness != Freshness.UNAVAILABLE:
        row.price = snap.price
        row.prev_close = snap.prev_close
        row.volume = snap.volume
        row.avg_volume_20d = snap.avg_volume_20d
        row.avg_daily_move_20d = snap.avg_daily_move_20d
        row.benchmark_pct_change = snap.benchmark_pct_change
        row.history_days = snap.history_days
        row.source = "demo"
        row.received_at = datetime.now(timezone.utc)
    row.freshness = snap.freshness.value
    try:
        db.commit()
    except IntegrityError:
        # Concurrent refresh already wrote this row (e.g. duplicate
        # background job) — safe to ignore, the data converges either way.
        db.rollback()
    return row


# ---------- schemas ----------

class WatchlistCreate(BaseModel):
    name: str = "My Watchlist"


class StockAdd(BaseModel):
    symbol: str


class WatchlistContextUpdate(BaseModel):
    goal: Optional[str] = None
    horizon: Optional[str] = None


class ThesisUpdate(BaseModel):
    thesis_type: str
    thesis_note: Optional[str] = None


class DemoScenario(BaseModel):
    scenario: str


# ---------- routes: watchlists ----------

@app.post("/watchlists")
def create_watchlist(payload: WatchlistCreate, db: Session = Depends(get_db)):
    wl = models.Watchlist(user_id=DEMO_USER_ID, name=payload.name)
    db.add(wl)
    db.commit()
    db.refresh(wl)
    return {"id": wl.id, "name": wl.name}


@app.get("/watchlists")
def list_watchlists(db: Session = Depends(get_db)):
    wls = db.query(models.Watchlist).filter_by(user_id=DEMO_USER_ID).all()
    return [{"id": w.id, "name": w.name} for w in wls]


@app.post("/watchlists/{watchlist_id}/stocks")
def add_stock(watchlist_id: int, payload: StockAdd, db: Session = Depends(get_db)):
    wl = db.query(models.Watchlist).filter_by(id=watchlist_id, user_id=DEMO_USER_ID).first()
    if not wl:
        raise HTTPException(404, "Watchlist not found")
    stock = db.query(models.Stock).filter_by(symbol=payload.symbol.upper()).first()
    if not stock:
        raise HTTPException(404, f"Unknown symbol {payload.symbol}")
    exists = db.query(models.WatchlistItem).filter_by(watchlist_id=wl.id, stock_id=stock.id).first()
    if exists:
        return {"status": "already_present"}
    db.add(models.WatchlistItem(watchlist_id=wl.id, stock_id=stock.id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()  # unique constraint caught a race between two tabs
        return {"status": "already_present"}
    return {"status": "added"}


@app.delete("/watchlists/{watchlist_id}/stocks/{symbol}")
def remove_stock(watchlist_id: int, symbol: str, db: Session = Depends(get_db)):
    stock = db.query(models.Stock).filter_by(symbol=symbol.upper()).first()
    if not stock:
        raise HTTPException(404, "Unknown symbol")
    item = db.query(models.WatchlistItem).filter_by(watchlist_id=watchlist_id, stock_id=stock.id).first()
    if item:
        db.delete(item)
        db.commit()
    return {"status": "removed"}


@app.put("/watchlists/{watchlist_id}/context")
def update_watchlist_context(
    watchlist_id: int,
    payload: WatchlistContextUpdate,
    db: Session = Depends(get_db),
):
    """Store optional investment goal and horizon for a watchlist.
    All values are nullable — calling this with null clears the stored value.
    Unknown enum values are rejected with 422 to prevent malformed data.
    """
    wl = db.query(models.Watchlist).filter_by(id=watchlist_id, user_id=DEMO_USER_ID).first()
    if not wl:
        raise HTTPException(404, "Watchlist not found")
    if payload.goal is not None and payload.goal not in VALID_GOALS:
        raise HTTPException(422, f"Unknown goal '{payload.goal}'. Valid values: {sorted(VALID_GOALS)}")
    if payload.horizon is not None and payload.horizon not in VALID_HORIZONS:
        raise HTTPException(422, f"Unknown horizon '{payload.horizon}'. Valid values: {sorted(VALID_HORIZONS)}")

    ctx = db.query(models.WatchlistContext).filter_by(watchlist_id=watchlist_id).first()
    if ctx is None:
        ctx = models.WatchlistContext(watchlist_id=watchlist_id)
        db.add(ctx)
    ctx.goal = payload.goal
    ctx.horizon = payload.horizon
    db.commit()
    return {"status": "ok", "goal": ctx.goal, "horizon": ctx.horizon}


@app.get("/watchlists/{watchlist_id}/context")
def get_watchlist_context(watchlist_id: int, db: Session = Depends(get_db)):
    """Returns the stored investment intent for a watchlist, or nulls if not set."""
    wl = db.query(models.Watchlist).filter_by(id=watchlist_id, user_id=DEMO_USER_ID).first()
    if not wl:
        raise HTTPException(404, "Watchlist not found")
    ctx = db.query(models.WatchlistContext).filter_by(watchlist_id=watchlist_id).first()
    return {
        "goal": ctx.goal if ctx else None,
        "horizon": ctx.horizon if ctx else None,
    }


@app.put("/watchlists/{watchlist_id}/items/{symbol}/thesis")
def update_thesis(
    watchlist_id: int,
    symbol: str,
    payload: ThesisUpdate,
    db: Session = Depends(get_db),
):
    """Upsert an investment thesis for a specific stock in a watchlist.
    thesis_type is validated against the allowed set.
    thesis_note is trimmed and capped at 500 characters.
    """
    wl = db.query(models.Watchlist).filter_by(id=watchlist_id, user_id=DEMO_USER_ID).first()
    if not wl:
        raise HTTPException(404, "Watchlist not found")
    if payload.thesis_type not in VALID_THESIS_TYPES:
        raise HTTPException(422, f"Unknown thesis_type '{payload.thesis_type}'. Valid: {sorted(VALID_THESIS_TYPES)}")
    if payload.thesis_note is not None and len(payload.thesis_note.strip()) > 500:
        raise HTTPException(422, "thesis_note must be 500 characters or fewer")

    stock = db.query(models.Stock).filter_by(symbol=symbol.upper()).first()
    if not stock:
        raise HTTPException(404, f"Unknown symbol {symbol}")

    thesis = db.query(models.StockThesis).filter_by(
        watchlist_id=watchlist_id, stock_id=stock.id
    ).first()
    if thesis is None:
        thesis = models.StockThesis(watchlist_id=watchlist_id, stock_id=stock.id)
        db.add(thesis)
    thesis.thesis_type = payload.thesis_type
    thesis.thesis_note = payload.thesis_note.strip() if payload.thesis_note else None
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(500, "Failed to save thesis")
    return {
        "status": "ok",
        "symbol": stock.symbol,
        "thesis_type": thesis.thesis_type,
        "thesis_note": thesis.thesis_note,
    }


@app.get("/watchlists/{watchlist_id}/items/{symbol}/thesis")
def get_thesis(watchlist_id: int, symbol: str, db: Session = Depends(get_db)):
    """Returns the stored thesis for a stock, or nulls if not set."""
    wl = db.query(models.Watchlist).filter_by(id=watchlist_id, user_id=DEMO_USER_ID).first()
    if not wl:
        raise HTTPException(404, "Watchlist not found")
    stock = db.query(models.Stock).filter_by(symbol=symbol.upper()).first()
    if not stock:
        raise HTTPException(404, f"Unknown symbol {symbol}")
    thesis = db.query(models.StockThesis).filter_by(
        watchlist_id=watchlist_id, stock_id=stock.id
    ).first()
    return {
        "symbol": stock.symbol,
        "thesis_type": thesis.thesis_type if thesis else None,
        "thesis_note": thesis.thesis_note if thesis else None,
    }


@app.get("/watchlists/{watchlist_id}/changes")
def get_changes(watchlist_id: int, db: Session = Depends(get_db)):
    """The core screen: 'what changed since you last checked', ranked by
    attention priority, not alphabetically or by raw magnitude alone."""
    wl = db.query(models.Watchlist).filter_by(id=watchlist_id, user_id=DEMO_USER_ID).first()
    if not wl:
        raise HTTPException(404, "Watchlist not found")

    results_json = []
    evaluated_results = []
    benchmark_change = None
    benchmark_freshness = "LIVE"
    
    t0 = time.time()
    for item in wl.items:
        stock = item.stock
        snap = fetch_snapshot(stock.symbol)
        upsert_market_snapshot(db, stock, snap)
        verdict = evaluate(snap)
        
        if snap.benchmark_pct_change is not None and benchmark_change is None:
            benchmark_change = snap.benchmark_pct_change
            benchmark_freshness = snap.freshness.value
            
        evaluated_results.append((stock, snap, verdict))
        _metrics["signal_computations_total"] += 1

    # Detect market regime
    verdicts = [v for _, _, v in evaluated_results]
    market_context = detect_market_regime(verdicts, benchmark_change, benchmark_freshness)

    for stock, snap, verdict in evaluated_results:
        state = db.query(models.UserStockState).filter_by(
            user_id=DEMO_USER_ID, stock_id=stock.id
        ).first()

        since_last = None
        if state and snap.freshness != Freshness.UNAVAILABLE:
            since_last = {
                "last_viewed_at": state.last_viewed_at.isoformat(),
                "price_then": state.last_seen_price,
                "price_now": snap.price,
                "volume_then": state.last_seen_volume,
                "volume_now": snap.volume,
            }

        results_json.append({
            "symbol": stock.symbol,
            "name": stock.name,
            "sector": stock.sector,
            "price": snap.price,
            "pct_change": round(snap.pct_change, 2),
            "freshness": snap.freshness.value,
            "verdict": verdict.verdict.value,
            "score": verdict.score,
            "normalized_score": verdict.normalized_score,
            "significance": verdict.significance.value,
            "confidence": verdict.confidence.value,
            "market_context": verdict.market_context,
            "directionality": verdict.directionality,
            "headline": verdict.headline,
            "why_it_matters": verdict.why_it_matters,
            "evidence": verdict.evidence.__dict__,
            "signals": [s.__dict__ for s in verdict.signals],
            "since_last_checked": since_last,
            "is_new_to_state": state is None,
        })

        # Persist the computed verdict for fast aggregate queries elsewhere.
        db.add(models.MeaningfulChange(
            user_id=DEMO_USER_ID, stock_id=stock.id, verdict=verdict.verdict.value,
            score=verdict.score, confidence=verdict.confidence.value,
            directionality=verdict.directionality, headline=verdict.headline,
            why_it_matters=verdict.why_it_matters, freshness=snap.freshness.value,
        ))
    db.commit()
    _metrics["last_signal_latency_ms"] = round((time.time() - t0) * 1000, 2)

    for r in results_json:
        r["_attention_score"] = calculate_attention(r)

    # Sort deterministically:
    # 1. Attention score descending
    # 2. Meaningful-change score descending
    # 3. Symbol ascending
    results_json.sort(key=lambda r: (-r["_attention_score"], -r["score"], r["symbol"]))

    attention_budget_max = 5
    current_rank = 1

    for r in results_json:
        if r["_attention_score"] > 0 and current_rank <= attention_budget_max:
            r["attention_rank"] = current_rank
            r["is_attention_budget"] = True
            current_rank += 1
        else:
            r["attention_rank"] = None
            r["is_attention_budget"] = False
        del r["_attention_score"]

    summary = {
        "needs_attention": sum(1 for r in results_json if r["verdict"] == "needs_attention"),
        "watch": sum(1 for r in results_json if r["verdict"] == "watch"),
        "no_change": sum(1 for r in results_json if r["verdict"] == "no_change"),
        "unavailable": sum(1 for r in results_json if r["verdict"] == "unavailable"),
    }

    # Inject Personal Context
    enriched_items = inject_personal_context(results_json, DEMO_USER_ID, wl.id, db)

    return {
        "watchlist_id": wl.id,
        "summary": summary,
        "market_data_available": summary["unavailable"] < len(results_json),
        "market_context": market_context.__dict__,
        "items": enriched_items,
    }


@app.post("/stocks/{symbol}/acknowledge")
def acknowledge_stock(symbol: str, db: Session = Depends(get_db)):
    """User has 'seen' this stock's current state — this becomes the new
    baseline for the next 'since you last checked' comparison. Upsert via
    the unique (user_id, stock_id) constraint makes this safe to call
    concurrently from two tabs: last write wins, which is correct for a
    read-marker (there is no meaningful 'merge' of two viewing events)."""
    stock = db.query(models.Stock).filter_by(symbol=symbol.upper()).first()
    if not stock:
        raise HTTPException(404, "Unknown symbol")
    snap = fetch_snapshot(stock.symbol)
    if snap.freshness == Freshness.UNAVAILABLE:
        raise HTTPException(503, "Cannot acknowledge while market data is unavailable")

    state = db.query(models.UserStockState).filter_by(user_id=DEMO_USER_ID, stock_id=stock.id).first()
    if state is None:
        state = models.UserStockState(user_id=DEMO_USER_ID, stock_id=stock.id)
        db.add(state)
    state.last_viewed_at = datetime.now(timezone.utc)
    state.last_seen_price = snap.price
    state.last_seen_volume = snap.volume
    state.last_seen_avg_daily_move_20d = snap.avg_daily_move_20d
    state.last_seen_benchmark_pct_change = snap.benchmark_pct_change
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return {"status": "race_resolved_by_peer"}
    return {"status": "acknowledged", "as_of": state.last_viewed_at.isoformat()}


@app.get("/stocks/{symbol}")
def stock_detail(symbol: str, db: Session = Depends(get_db)):
    stock = db.query(models.Stock).filter_by(symbol=symbol.upper()).first()
    if not stock:
        raise HTTPException(404, "Unknown symbol")
    snap = fetch_snapshot(stock.symbol)
    verdict = evaluate(snap)
    state = db.query(models.UserStockState).filter_by(user_id=DEMO_USER_ID, stock_id=stock.id).first()
    return {
        "symbol": stock.symbol,
        "name": stock.name,
        "sector": stock.sector,
        "price": snap.price,
        "pct_change": round(snap.pct_change, 2),
        "volume": snap.volume,
        "avg_volume_20d": snap.avg_volume_20d,
        "benchmark_pct_change": snap.benchmark_pct_change,
        "freshness": snap.freshness.value,
        "verdict": verdict.verdict.value,
        "score": verdict.score,
        "normalized_score": verdict.normalized_score,
        "significance": verdict.significance.value,
        "confidence": verdict.confidence.value,
        "headline": verdict.headline,
        "why_it_matters": verdict.why_it_matters,
        "evidence": verdict.evidence.__dict__,
        "signals": [s.__dict__ for s in verdict.signals],
        "last_seen": {
            "last_viewed_at": state.last_viewed_at.isoformat(),
            "price": state.last_seen_price,
            "volume": state.last_seen_volume,
        } if state else None,
    }


# ---------- market / health / demo control ----------

@app.get("/market/status")
def market_status():
    return {"active_scenario": _active_scenario, "available_scenarios": list(demo_data.SCENARIOS.keys())}


@app.get("/demo/scenario")
def get_scenario():
    return {"active_scenario": _active_scenario, "available_scenarios": list(demo_data.SCENARIOS.keys())}


@app.post("/demo/scenario")
def set_scenario(payload: DemoScenario):
    if payload.scenario not in demo_data.SCENARIOS:
        raise HTTPException(400, f"Unknown scenario. Choose from {list(demo_data.SCENARIOS.keys())}")
    with _state_lock:
        global _active_scenario
        _active_scenario = payload.scenario
    return {"status": "ok", "active_scenario": _active_scenario}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(models.User.__table__.select().limit(1))
        db_ok = True
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else "unreachable",
        "active_scenario": _active_scenario,
    }


@app.get("/funds")
def list_funds(db: Session = Depends(get_db)):
    funds = db.query(models.MutualFund).all()
    return [{"id": f.id, "name": f.name, "category": f.category, "expense_ratio": f.expense_ratio} for f in funds]


@app.get("/funds/{fund_id}/xray")
def fund_xray(fund_id: int, db: Session = Depends(get_db)):
    fund = db.query(models.MutualFund).filter_by(id=fund_id).first()
    if not fund:
        raise HTTPException(404, "Fund not found")
    holdings = db.query(models.MutualFundHolding).filter_by(fund_id=fund_id).order_by(models.MutualFundHolding.weight.desc()).limit(5).all()
    return {
        "id": fund.id,
        "name": fund.name,
        "category": fund.category,
        "expense_ratio": fund.expense_ratio,
        "top_holdings": [{"symbol": h.symbol, "weight": h.weight} for h in holdings]
    }


@app.get("/funds/{fund_id}/overlap")
def fund_overlap(fund_id: int, db: Session = Depends(get_db)):
    fund = db.query(models.MutualFund).filter_by(id=fund_id).first()
    if not fund:
        raise HTTPException(404, "Fund not found")
        
    user_funds = db.query(models.UserMutualFund).filter_by(user_id=DEMO_USER_ID).all()
    if not user_funds:
        return {"overlap": 0.0, "common_holdings": []}
        
    target_holdings = {h.symbol: h.weight for h in db.query(models.MutualFundHolding).filter_by(fund_id=fund_id).all()}
    max_overlap = 0.0
    common_symbols_max = []
    
    for uf in user_funds:
        if uf.fund_id == fund_id and len(user_funds) > 1:
            # Skip comparing with itself if the user has other funds to compare against
            continue
            
        other_holdings = {h.symbol: h.weight for h in db.query(models.MutualFundHolding).filter_by(fund_id=uf.fund_id).all()}
        overlap = 0.0
        common_symbols = []
        for sym, weight_A in target_holdings.items():
            if sym in other_holdings:
                weight_B = other_holdings[sym]
                overlap += min(weight_A, weight_B)
                common_symbols.append(sym)
                
        if overlap >= max_overlap:
            max_overlap = overlap
            common_symbols_max = common_symbols
            
    return {
        "fund_id": fund_id,
        "max_overlap": round(max_overlap / 100.0, 4),
        "common_symbols": common_symbols_max
    }


@app.post("/user/funds/{fund_id}")
def add_user_fund(fund_id: int, db: Session = Depends(get_db)):
    fund = db.query(models.MutualFund).filter_by(id=fund_id).first()
    if not fund:
        raise HTTPException(404, "Fund not found")
    uf = db.query(models.UserMutualFund).filter_by(user_id=DEMO_USER_ID, fund_id=fund_id).first()
    if not uf:
        db.add(models.UserMutualFund(user_id=DEMO_USER_ID, fund_id=fund_id))
        db.commit()
    return {"status": "added"}


@app.delete("/user/funds/{fund_id}")
def remove_user_fund(fund_id: int, db: Session = Depends(get_db)):
    uf = db.query(models.UserMutualFund).filter_by(user_id=DEMO_USER_ID, fund_id=fund_id).first()
    if uf:
        db.delete(uf)
        db.commit()
    return {"status": "removed"}


@app.get("/stocks/{symbol}/valuation")
def get_valuation(symbol: str, db: Session = Depends(get_db)):
    stock = db.query(models.Stock).filter_by(symbol=symbol.upper()).first()
    if not stock:
        raise HTTPException(404, "Stock not found")
        
    val = db.query(models.StockValuation).filter_by(stock_id=stock.id).first()
    if not val:
        return {"available": False, "reason": "VALUATION DATA UNAVAILABLE"}
        
    classification = classify_valuation(
        current_pe=val.current_pe,
        historical_pe_median=val.historical_pe_median,
        historical_pe_low=val.historical_pe_low,
        historical_pe_high=val.historical_pe_high
    )
    
    if classification["label"] == "DATA_UNAVAILABLE":
        return {"available": False, "reason": "VALUATION DATA UNAVAILABLE"}
        
    return {
        "available": True,
        "current_pe": val.current_pe,
        "historical_pe_median": val.historical_pe_median,
        "historical_pe_low": val.historical_pe_low,
        "historical_pe_high": val.historical_pe_high,
        "label": classification["label"],
        "delta_vs_median_pct": classification["delta_vs_median_pct"]
    }


@app.get("/stocks/{symbol}/events")
def get_events(symbol: str, db: Session = Depends(get_db)):
    stock = db.query(models.Stock).filter_by(symbol=symbol.upper()).first()
    if not stock:
        raise HTTPException(404, "Stock not found")
        
    events = db.query(models.StockEvent).filter_by(stock_id=stock.id).all()
    out = []
    now = datetime.utcnow()
    for e in events:
        days_until = (e.event_date - now).days
        if days_until >= 0:
            out.append({
                "event_type": e.event_type,
                "event_date": e.event_date.isoformat(),
                "title": e.title,
                "days_until": days_until
            })
    return sorted(out, key=lambda x: x["days_until"])


@app.get("/watchlists/{watchlist_id}/sip-context")
def get_sip_context(watchlist_id: int, benchmark_weekly_change: float = 0.0, db: Session = Depends(get_db)):
    wl = db.query(models.Watchlist).filter_by(id=watchlist_id, user_id=DEMO_USER_ID).first()
    if not wl:
        raise HTTPException(404, "Watchlist not found")
        
    sip = db.query(models.UserSIP).filter_by(user_id=DEMO_USER_ID).first()
    
    sip_dict = None
    if sip:
        sip_dict = {
            "instrument": sip.instrument,
            "amount": sip.sip_amount,
            "next_date": sip.next_sip_date.isoformat() if sip.next_sip_date else None,
            "frequency": sip.frequency
        }
        
    return evaluate_sip_context(benchmark_weekly_change, sip_dict)


@app.get("/metrics")
def metrics():
    return _metrics


# Serve the frontend as static files so the whole product is one process
# to run for judges (`uvicorn app.main:app`). A separate dev server is
# still how you'd iterate on the frontend day-to-day.
import os
_frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")
