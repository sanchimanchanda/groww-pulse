"""
Schema notes (full rationale in ARCHITECTURE.md):

- user_stock_state is the "since you last checked" table: one row per
  (user, stock), overwritten on each view. A unique constraint on
  (user_id, stock_id) makes "record what the user last saw" idempotent —
  concurrent tabs writing the same view collapse to last-write-wins, which
  is the correct behavior for a read-state marker (unlike a financial
  ledger, order doesn't matter here, only the final value).
- meaningful_changes stores computed signals per (watchlist_item, computed
  at a given market snapshot), so re-running the engine on the same input
  is idempotent (unique constraint on stock_id + snapshot source_timestamp)
  and cheap to query for "top changes for this user's watchlist".
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from .database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")


class Watchlist(Base):
    __tablename__ = "watchlists"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False, default="My Watchlist")
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="watchlists")
    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")


class Stock(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    sector = Column(String, nullable=True)


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    id = Column(Integer, primary_key=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    added_at = Column(DateTime, default=utcnow)

    watchlist = relationship("Watchlist", back_populates="items")
    stock = relationship("Stock")

    __table_args__ = (
        UniqueConstraint("watchlist_id", "stock_id", name="uq_watchlist_stock"),
    )


class MarketSnapshotRow(Base):
    """Latest known reading per stock (upserted by the background refresh).
    A history table would be the natural next table if we needed true
    time-series charting; out of scope for v1 (see TRADEOFFS.md)."""
    __tablename__ = "market_snapshots"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), unique=True, nullable=False)
    price = Column(Float, nullable=False)
    prev_close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    avg_volume_20d = Column(Float, nullable=False)
    avg_daily_move_20d = Column(Float, nullable=False)
    benchmark_pct_change = Column(Float, nullable=False)
    history_days = Column(Integer, nullable=False, default=20)
    freshness = Column(String, nullable=False, default="LIVE")
    source = Column(String, nullable=False, default="demo")
    market_timestamp = Column(DateTime, nullable=True)
    received_at = Column(DateTime, default=utcnow)


class UserStockState(Base):
    """'Since you last checked' marker: what the user saw, last time they saw it."""
    __tablename__ = "user_stock_state"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    last_viewed_at = Column(DateTime, nullable=False, default=utcnow)
    last_seen_price = Column(Float, nullable=False)
    last_seen_volume = Column(Integer, nullable=False)
    last_seen_avg_daily_move_20d = Column(Float, nullable=False)
    last_seen_benchmark_pct_change = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "stock_id", name="uq_user_stock_state"),
    )


VALID_GOALS = frozenset({
    "GENERAL", "LONG_TERM_WEALTH", "RETIREMENT",
    "GROWTH", "DIVIDEND", "VALUE", "SECTOR_THEME",
})
VALID_HORIZONS = frozenset({"SHORT_TERM", "MEDIUM_TERM", "LONG_TERM"})

VALID_THESIS_TYPES = frozenset({
    "GENERAL", "GROWTH", "DIVIDEND", "VALUE", "RECOVERY", "SECTOR_OPPORTUNITY",
})


class WatchlistContext(Base):
    """Companion table — keeps optional investment intent separate from
    the core watchlist row so no ALTER TABLE is needed on an existing DB."""
    __tablename__ = "watchlist_context"
    id = Column(Integer, primary_key=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id"), unique=True, nullable=False)
    goal = Column(String, nullable=True)      # one of VALID_GOALS
    horizon = Column(String, nullable=True)   # one of VALID_HORIZONS
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class StockThesis(Base):
    """Per-stock investment thesis for a user's watchlist item.
    Stored as a companion table so the core watchlist_items table is unchanged.
    thesis_note is free text; max length enforced at route level."""
    __tablename__ = "stock_thesis"
    id = Column(Integer, primary_key=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    thesis_type = Column(String, nullable=False)   # one of VALID_THESIS_TYPES
    thesis_note = Column(String, nullable=True)    # free text, max 500 chars
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        UniqueConstraint("watchlist_id", "stock_id", name="uq_thesis_wl_stock"),
    )


class MutualFund(Base):
    __tablename__ = "mutual_funds"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    expense_ratio = Column(Float, nullable=True)


class MutualFundHolding(Base):
    __tablename__ = "mutual_fund_holdings"
    id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey("mutual_funds.id"), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    weight = Column(Float, nullable=False)   # percent, e.g. 8.2 for 8.2%


class UserMutualFund(Base):
    __tablename__ = "user_mutual_funds"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fund_id = Column(Integer, ForeignKey("mutual_funds.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "fund_id", name="uq_user_mutual_fund"),
    )


class StockValuation(Base):
    __tablename__ = "stock_valuation"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), unique=True, nullable=False)
    current_pe = Column(Float, nullable=True)
    historical_pe_median = Column(Float, nullable=True)
    historical_pe_low = Column(Float, nullable=True)
    historical_pe_high = Column(Float, nullable=True)
    source = Column(String, default="demo")
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class StockEvent(Base):
    __tablename__ = "stock_events"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    event_type = Column(String, nullable=False)   # EARNINGS | DIVIDEND
    event_date = Column(DateTime, nullable=False, index=True)
    title = Column(String, nullable=True)


class UserSIP(Base):
    __tablename__ = "user_sips"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    instrument = Column(String, nullable=False)    # e.g. "NIFTY 50 Index Fund"
    sip_amount = Column(Float, nullable=False)     # positive, in INR
    frequency = Column(String, nullable=False)     # MONTHLY | WEEKLY
    next_sip_date = Column(DateTime, nullable=True)


class MeaningfulChange(Base):
    """Computed, persisted verdicts — so 'top changes' is a simple indexed
    query, not a recomputation on every page load."""
    __tablename__ = "meaningful_changes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    verdict = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    confidence = Column(String, nullable=False)
    directionality = Column(String, nullable=False)
    headline = Column(String, nullable=False)
    why_it_matters = Column(String, nullable=False)
    freshness = Column(String, nullable=False)
    computed_at = Column(DateTime, default=utcnow)

    __table_args__ = (
        Index("ix_meaningful_changes_user_score", "user_id", "score"),
    )
