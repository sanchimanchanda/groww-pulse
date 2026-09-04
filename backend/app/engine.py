"""
Meaningful Change Engine
========================

Core product idea: a raw % price change is not, by itself, informative.
A 3% move in a stock that routinely swings 5% a day is noise. A 0.8% move
on 3x normal volume, or a stock that beats its benchmark by 4% while the
benchmark is flat, is signal. This module turns raw market snapshots into
a small, explainable, DETERMINISTIC score plus a human-readable reason.

Deliberately excluded from v1 (see TRADEOFFS.md): gap up/down, breakout/
breakdown, sector divergence as its own signal, corporate/event/news
signals (no reliable free data source in 72h), and using "time since last
viewed" as a scoring input (it selects the comparison baseline, but does
not by itself make a change more or less material — otherwise a user who
checks rarely would be shown noise as signal).

Signals used (3, chosen to be independently justifiable and cheaply
computable from a single price/volume snapshot + a rolling history):

1. Volatility-adjusted price move (z_price)
   z_price = pct_change / trailing_20d_avg_daily_move
   Normalizes price change against how much the stock *normally* moves.
   A stock with 5% typical daily volatility moving 4% is unremarkable;
   a stock with 0.5% typical volatility moving 1.5% is a 3-sigma event.

2. Relative performance vs. benchmark, volatility-adjusted (z_relative)
   relative_change = pct_change - benchmark_pct_change
   z_relative = relative_change / trailing_20d_avg_daily_move
   Captures "moved more than the market did", independent of whether the
   whole market moved. A stock at +2% while NIFTY is +3% is *relative*
   underperformance even though the raw number is positive.

3. Volume anomaly (volume_ratio)
   volume_ratio = current_volume / trailing_20d_avg_volume
   Corroborating signal, capped, so a volume spike alone can nudge a
   borderline move into "worth a look" but cannot alone produce a
   "needs attention" verdict for an otherwise unremarkable price move.

Weighted, capped combination:
   raw_score = 0.45*|z_price| + 0.35*|z_relative| + 0.20*min(volume_ratio, 4)/2

Thresholds (documented, tunable, NOT hidden inside magic branches):
   score >= HIGH_THRESHOLD (2.0)  -> "needs_attention"
   score >= WATCH_THRESHOLD (1.0) -> "watch"
   else                            -> "no_change"

Confidence is a function of data freshness and whether we have enough
history to compute volatility (min 5 trading days). It downgrades the
verdict rather than pretending precision we don't have.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Freshness(str, Enum):
    LIVE = "LIVE"
    DELAYED = "DELAYED"
    STALE = "STALE"
    UNAVAILABLE = "UNAVAILABLE"


class Verdict(str, Enum):
    NEEDS_ATTENTION = "needs_attention"
    WATCH = "watch"
    NO_CHANGE = "no_change"
    UNAVAILABLE = "unavailable"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Significance(str, Enum):
    """How unusual is the observed movement — independent of data trustworthiness."""
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    NONE = "NONE"


# Tunable weights & thresholds — centralized so they can be justified/tuned
# in one place instead of scattered through the codebase.
WEIGHT_PRICE_Z = 0.45
WEIGHT_RELATIVE_Z = 0.35
WEIGHT_VOLUME = 0.20
VOLUME_CAP = 4.0  # a 10x volume day contributes the same as a 4x day

HIGH_THRESHOLD = 2.0
WATCH_THRESHOLD = 1.0

MIN_HISTORY_DAYS = 5  # below this we don't trust the volatility estimate
SCORE_PRACTICAL_CEILING = 4.0  # for normalizing raw score to 0-100


@dataclass
class MarketSnapshot:
    """A single point-in-time reading for a stock, with provenance."""
    symbol: str
    price: Optional[float]
    prev_close: Optional[float]
    volume: Optional[int]
    avg_volume_20d: float
    avg_daily_move_20d: float  # trailing avg absolute % daily move (proxy for volatility)
    benchmark_pct_change: Optional[float]  # e.g. NIFTY 50 % change over same window
    history_days: int
    freshness: Freshness
    source_timestamp: Optional[str] = None
    received_at: Optional[str] = None

    def __post_init__(self):
        import math
        # Safely handle malformed data
        if self.price is not None and (math.isnan(self.price) or self.price < 0):
            self.price = None
        if self.prev_close is not None and (math.isnan(self.prev_close) or self.prev_close <= 0):
            self.prev_close = None
        if self.volume is not None and (math.isnan(self.volume) or self.volume < 0):
            self.volume = None
            
        if self.price is None or self.prev_close is None:
            self.freshness = Freshness.UNAVAILABLE

    @property
    def pct_change(self) -> float:
        if self.prev_close is None or self.price is None or self.prev_close <= 0:
            return 0.0
        return (self.price - self.prev_close) / self.prev_close * 100.0


@dataclass
class ChangeSignal:
    """One explainable contributor to the overall score."""
    kind: str
    value: float
    description: str


@dataclass
class Evidence:
    """Structured numeric evidence the frontend can display directly."""
    volatility_multiple: float = 0.0 # e.g. 2.7 → "2.7× average move"
    volume_multiple: float = 0.0     # e.g. 3.2 → "3.2× normal volume"
    relative_multiple: float = 0.0   # abs(z_relative), multiple of normal volatility
    relative_delta_pp: float = 0.0   # e.g. 2.0 → "+2.0 pp vs benchmark"
    pct_change: Optional[float] = 0.0          # raw % change
    benchmark_pct_change: Optional[float] = None


@dataclass
class MeaningfulChangeResult:
    symbol: str
    verdict: Verdict
    score: float
    normalized_score: float  # 0-100 scale
    significance: Significance
    confidence: Confidence
    directionality: str  # "up" | "down" | "flat"
    headline: str
    why_it_matters: str
    evidence: Evidence = field(default_factory=Evidence)
    signals: list = field(default_factory=list)
    freshness: Freshness = Freshness.LIVE
    market_context: str = "normal"  # "normal" | "tracking_market" | "outlier"


def _confidence_for(snapshot: MarketSnapshot) -> Confidence:
    if snapshot.freshness == Freshness.UNAVAILABLE:
        return Confidence.LOW
    if snapshot.history_days < MIN_HISTORY_DAYS:
        return Confidence.LOW
    if snapshot.freshness == Freshness.STALE:
        return Confidence.LOW
    if snapshot.freshness == Freshness.DELAYED:
        return Confidence.MEDIUM
    return Confidence.HIGH


def _significance_for(score: float) -> Significance:
    """How unusual is the observed movement — independent of data quality."""
    if score >= HIGH_THRESHOLD:
        return Significance.HIGH
    if score >= WATCH_THRESHOLD:
        return Significance.MODERATE
    if score >= 0.3:
        return Significance.LOW
    return Significance.NONE


def evaluate(snapshot: MarketSnapshot) -> MeaningfulChangeResult:
    """Pure, deterministic function: same input always produces same output.
    This is what makes the engine testable and explainable to judges."""

    if snapshot.freshness == Freshness.UNAVAILABLE or snapshot.price is None or snapshot.prev_close is None:
        return MeaningfulChangeResult(
            symbol=snapshot.symbol,
            verdict=Verdict.UNAVAILABLE,
            score=0.0,
            normalized_score=0.0,
            significance=Significance.NONE,
            confidence=Confidence.LOW,
            directionality="flat",
            headline="Market data temporarily unavailable",
            why_it_matters="We couldn't reach fresh data for this stock. Showing last known values.",
            freshness=Freshness.UNAVAILABLE,
        )

    pct = snapshot.pct_change
    vol_proxy = max(snapshot.avg_daily_move_20d, 0.25)  # floor to avoid div-by-~0 explosions
    z_price = pct / vol_proxy

    if snapshot.benchmark_pct_change is not None:
        relative_change = pct - snapshot.benchmark_pct_change
        z_relative = relative_change / vol_proxy
    else:
        relative_change = 0.0
        z_relative = 0.0

    volume_ratio = 0.0
    if snapshot.avg_volume_20d > 0 and snapshot.volume is not None:
        volume_ratio = snapshot.volume / snapshot.avg_volume_20d
    volume_contribution = min(volume_ratio, VOLUME_CAP) / 2.0

    score = (
        WEIGHT_PRICE_Z * abs(z_price)
        + WEIGHT_RELATIVE_Z * abs(z_relative)
        + WEIGHT_VOLUME * volume_contribution
    )

    # Significance is computed BEFORE confidence caps — it reflects how
    # unusual the movement is, regardless of data trustworthiness.
    significance = _significance_for(score)

    confidence = _confidence_for(snapshot)
    # Low confidence caps how loudly we're willing to shout.
    if confidence == Confidence.LOW and score >= HIGH_THRESHOLD:
        score = HIGH_THRESHOLD - 0.01  # demote to "watch" at most

    if score >= HIGH_THRESHOLD:
        verdict = Verdict.NEEDS_ATTENTION
    elif score >= WATCH_THRESHOLD:
        verdict = Verdict.WATCH
    else:
        verdict = Verdict.NO_CHANGE

    normalized_score = round(min(score / SCORE_PRACTICAL_CEILING * 100, 100), 1)

    directionality = "up" if pct > 0.05 else ("down" if pct < -0.05 else "flat")

    # Structured evidence for direct frontend consumption
    evidence = Evidence(
        volatility_multiple=round(abs(z_price), 2),
        volume_multiple=round(volume_ratio, 2),
        relative_multiple=round(abs(z_relative), 2),
        relative_delta_pp=round(relative_change, 2),
        pct_change=round(pct, 2),
        benchmark_pct_change=round(snapshot.benchmark_pct_change, 2) if snapshot.benchmark_pct_change is not None else None,
    )

    signals = []
    if abs(z_price) >= 1.0:
        signals.append(ChangeSignal(
            kind="VAPM",
            value=round(z_price, 2),
            description=f"Price moved {abs(pct):.1f}%, about {abs(z_price):.1f}× its normal range.",
        ))
    if abs(z_relative) >= 1.0:
        sign = "outperformed" if relative_change > 0 else "underperformed"
        signals.append(ChangeSignal(
            kind="RPM",
            value=round(z_relative, 2),
            description=f"{sign.capitalize()} the benchmark by {abs(relative_change):.1f} percentage points.",
        ))
    if volume_ratio >= 1.5:
        signals.append(ChangeSignal(
            kind="VA",
            value=round(volume_ratio, 2),
            description=f"Volume is {volume_ratio:.1f}× the 20-day average.",
        ))
    if confidence != Confidence.HIGH:
        signals.append(ChangeSignal(
            kind="DATA_QUALITY",
            value=0.0,
            description=f"Data freshness is {snapshot.freshness.value.lower()}; treating this reading cautiously.",
        ))

    headline, why = _explain(snapshot, verdict, pct, relative_change, volume_ratio)

    return MeaningfulChangeResult(
        symbol=snapshot.symbol,
        verdict=verdict,
        score=round(score, 3),
        normalized_score=normalized_score,
        significance=significance,
        confidence=confidence,
        directionality=directionality,
        headline=headline,
        why_it_matters=why,
        evidence=evidence,
        signals=signals,
        freshness=snapshot.freshness,
    )


def _explain(snapshot, verdict, pct, relative_change, volume_ratio) -> tuple[str, str]:
    """Translate the numbers into a sentence a non-technical investor can read.
    This stays rule-based/deterministic — see AI_USAGE note in README for why
    we don't hand this to an LLM."""
    symbol = snapshot.symbol
    if verdict == Verdict.NO_CHANGE:
        return (f"{symbol}: no meaningful change", "Movement was within its normal range.")

    parts = []
    if abs(pct) >= 0.5:
        parts.append(f"moved {pct:+.1f}%")
    if abs(relative_change) >= 0.5:
        rel_word = "vs" if relative_change >= 0 else "vs"
        parts.append(f"{relative_change:+.1f} pts relative to the benchmark")
    if volume_ratio >= 1.5:
        parts.append(f"on {volume_ratio:.1f}x normal volume")

    detail = ", ".join(parts) if parts else "showed an unusual pattern"
    if verdict == Verdict.NEEDS_ATTENTION:
        headline = f"{symbol}: meaningful change"
    else:
        headline = f"{symbol}: worth a look"
    why = f"{symbol} {detail} since you last checked."
    return headline, why


MARKET_WIDE_COVERAGE_THRESHOLD = 0.70
MARKET_TRACKING_Z_TOLERANCE = 1.0


@dataclass
class MarketContextResult:
    regime: str  # "market_wide" | "normal"
    benchmark_change: Optional[float]
    coverage: float
    outliers: list[str]
    benchmark_freshness: str = "LIVE"
    description: str = ""


def detect_market_regime(results: list[MeaningfulChangeResult], benchmark_pct_change: Optional[float], benchmark_freshness: str = "LIVE") -> MarketContextResult:
    """
    Detects if the market is moving broadly together.
    If so, flags stocks that are tracking the market vs genuine outliers.
    """
    if benchmark_pct_change is None or not results:
        return MarketContextResult(regime="normal", benchmark_change=benchmark_pct_change, coverage=0.0, outliers=[], benchmark_freshness="UNAVAILABLE")

    eligible_count = 0
    tracking_count = 0
    outliers_list = []

    for r in results:
        if r.freshness == Freshness.UNAVAILABLE or r.evidence.benchmark_pct_change is None:
            continue
            
        eligible_count += 1
        
        # A stock tracks the market if its volatility-adjusted relative move is within tolerance
        if r.evidence.relative_multiple <= MARKET_TRACKING_Z_TOLERANCE:
            tracking_count += 1
        else:
            outliers_list.append(r)

    coverage = tracking_count / eligible_count if eligible_count > 0 else 0.0
    regime = "market_wide" if coverage >= MARKET_WIDE_COVERAGE_THRESHOLD else "normal"
    
    # We only apply context tags if we are actually in a market_wide regime
    final_outliers = []
    if regime == "market_wide":
        for r in results:
            if r.freshness == Freshness.UNAVAILABLE or r.evidence.benchmark_pct_change is None:
                continue
            if r.evidence.relative_multiple <= MARKET_TRACKING_Z_TOLERANCE:
                r.market_context = "tracking_market"
            else:
                r.market_context = "outlier"
                final_outliers.append(r.symbol)

    return MarketContextResult(
        regime=regime,
        benchmark_change=benchmark_pct_change,
        coverage=round(coverage, 3),
        outliers=final_outliers,
        benchmark_freshness=benchmark_freshness,
        description="The broader market is moving strongly in this direction." if regime == "market_wide" else ""
    )

def calculate_attention(item: dict) -> float:
    """
    Deterministic attention-ranking function.
    Significance is how unusual the move is. Attention is how strongly it should be surfaced.
    Returns an attention score where higher = more important to show first.
    Returns -1.0 for items that should never enter the attention budget.
    """
    if item["verdict"] in ("no_change", "unavailable"):
        return -1.0
        
    base_score = item["score"]
    
    # 1. Market context treatment
    if item["market_context"] == "outlier":
        base_score *= 1.2
    elif item["market_context"] == "tracking_market":
        base_score *= 0.6
        
    # 2. Last-seen treatment
    if item.get("is_new_to_state", False):
        base_score *= 1.3
        
    # 3. Confidence treatment (penalty, not erasure)
    if item["confidence"] == "LOW":
        base_score *= 0.8
    elif item["confidence"] == "MEDIUM":
        base_score *= 0.95
        
    # 4. Recency treatment
    # A more rigorous implementation would compare event time vs now.
    # Since we lack precise event timestamps in the demo, we rely on is_new_to_state.
        
    return round(base_score, 4)
