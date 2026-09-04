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
    
    t0 = time.time()
    for item in wl.items:
        stock = item.stock
        snap = fetch_snapshot(stock.symbol)
        upsert_market_snapshot(db, stock, snap)
        verdict = evaluate(snap)
        
        if snap.benchmark_pct_change is not None and benchmark_change is None:
            benchmark_change = snap.benchmark_pct_change
            
        evaluated_results.append((stock, snap, verdict))
        _metrics["signal_computations_total"] += 1

    # Detect market regime
    verdicts = [v for _, _, v in evaluated_results]
    market_context = detect_market_regime(verdicts, benchmark_change)

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

    return {
        "watchlist_id": wl.id,
        "summary": summary,
        "market_data_available": summary["unavailable"] < len(results_json),
        "market_context": market_context.__dict__,
        "items": results_json,
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
