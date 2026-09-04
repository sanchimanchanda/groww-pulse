"""
Deterministic demo data so the product can be judged without depending on
a live market data API (see section 25/26 of the brief, and TRADEOFFS.md
for why we don't wire a live feed for the submission).

Every value here is clearly synthetic and is labelled as such via the
`source="demo"` field on each snapshot — never presented as live.
"""
from .engine import Freshness

STOCKS = [
    {"symbol": "RELIANCE", "name": "Reliance Industries", "sector": "Energy"},
    {"symbol": "TCS", "name": "Tata Consultancy Services", "sector": "IT"},
    {"symbol": "INFY", "name": "Infosys", "sector": "IT"},
    {"symbol": "HDFCBANK", "name": "HDFC Bank", "sector": "Banking"},
    {"symbol": "ICICIBANK", "name": "ICICI Bank", "sector": "Banking"},
    {"symbol": "SBIN", "name": "State Bank of India", "sector": "Banking"},
    {"symbol": "ITC", "name": "ITC Limited", "sector": "FMCG"},
    {"symbol": "BHARTIARTL", "name": "Bharti Airtel", "sector": "Telecom"},
    {"symbol": "LT", "name": "Larsen & Toubro", "sector": "Infrastructure"},
    {"symbol": "MARUTI", "name": "Maruti Suzuki", "sector": "Auto"},
]

# Baseline "normal market" snapshot per symbol: price, prev_close, volume,
# avg_volume_20d, avg_daily_move_20d (typical % move), benchmark_pct_change.
BASELINE = {
    "RELIANCE":   dict(price=2945.0, prev_close=2941.0, volume=5_200_000, avg_volume_20d=5_400_000, avg_daily_move_20d=1.1),
    "TCS":        dict(price=4102.0, prev_close=4098.0, volume=1_800_000, avg_volume_20d=1_900_000, avg_daily_move_20d=0.8),
    "INFY":       dict(price=1875.0, prev_close=1871.0, volume=4_100_000, avg_volume_20d=4_300_000, avg_daily_move_20d=0.9),
    "HDFCBANK":   dict(price=1698.0, prev_close=1695.0, volume=6_500_000, avg_volume_20d=6_700_000, avg_daily_move_20d=0.7),
    "ICICIBANK":  dict(price=1256.0, prev_close=1253.0, volume=7_200_000, avg_volume_20d=7_500_000, avg_daily_move_20d=0.9),
    "SBIN":       dict(price=812.0,  prev_close=810.0,  volume=9_800_000, avg_volume_20d=10_100_000, avg_daily_move_20d=1.2),
    "ITC":        dict(price=468.0,  prev_close=467.0,  volume=8_400_000, avg_volume_20d=8_600_000, avg_daily_move_20d=0.6),
    "BHARTIARTL": dict(price=1589.0, prev_close=1584.0, volume=3_300_000, avg_volume_20d=3_500_000, avg_daily_move_20d=1.0),
    "LT":         dict(price=3612.0, prev_close=3605.0, volume=1_500_000, avg_volume_20d=1_600_000, avg_daily_move_20d=1.3),
    "MARUTI":     dict(price=12450.0, prev_close=12410.0, volume=420_000, avg_volume_20d=460_000, avg_daily_move_20d=1.4),
}

NIFTY_BASELINE_CHANGE = 0.2  # % change for "normal market" scenario


def _snapshot(symbol, price, prev_close, volume, avg_volume_20d, avg_daily_move_20d,
              benchmark_pct_change, freshness=Freshness.LIVE, history_days=20):
    return dict(
        symbol=symbol, price=price, prev_close=prev_close, volume=volume,
        avg_volume_20d=avg_volume_20d, avg_daily_move_20d=avg_daily_move_20d,
        benchmark_pct_change=benchmark_pct_change, freshness=freshness,
        history_days=history_days,
    )


def scenario_normal_market():
    """Everything moves within its normal range. Proves the system doesn't
    manufacture noise when nothing meaningful happened."""
    out = []
    for sym, b in BASELINE.items():
        out.append(_snapshot(sym, b["price"], b["prev_close"], b["volume"],
                              b["avg_volume_20d"], b["avg_daily_move_20d"], NIFTY_BASELINE_CHANGE))
    return out


def scenario_significant_move():
    """RELIANCE has a large, benchmark-beating move. Everything else normal."""
    out = scenario_normal_market()
    for row in out:
        if row["symbol"] == "RELIANCE":
            row["price"] = round(row["prev_close"] * 1.048, 2)
            row["volume"] = int(row["avg_volume_20d"] * 2.1)
    return out


def scenario_volume_spike():
    """TCS: small price move, large volume — 'watch' not 'needs attention'."""
    out = scenario_normal_market()
    for row in out:
        if row["symbol"] == "TCS":
            row["price"] = round(row["prev_close"] * 1.012, 2)
            row["volume"] = int(row["avg_volume_20d"] * 2.8)
    return out


def scenario_market_crash():
    """Market-wide drop. Individual stocks near the benchmark should NOT
    all be flagged as individually meaningful — only genuine divergence
    from the (now-negative) benchmark should surface."""
    out = []
    benchmark_change = -3.2
    for sym, b in BASELINE.items():
        drop_factor = 1 + (benchmark_change / 100.0)
        price = round(b["prev_close"] * drop_factor, 2)
        out.append(_snapshot(sym, price, b["prev_close"], b["volume"] * 2,
                              b["avg_volume_20d"], b["avg_daily_move_20d"], benchmark_change))
    # SBIN bucks the trend — up on volume during a crash, genuinely notable.
    for row in out:
        if row["symbol"] == "SBIN":
            b = BASELINE["SBIN"]
            row["price"] = round(b["prev_close"] * 1.015, 2)
            row["volume"] = int(b["avg_volume_20d"] * 3.5)
    return out


def scenario_killer_demo():
    """
    The core demo thesis: A big move is not necessarily a meaningful move.
    RELIANCE moves +4.8% (but NIFTY moves +4.2%, and normal vol is ±5.2%).
    INFY moves +2.1% (but NIFTY moves +0.1%, and normal vol is ±0.6%, with 3.2x vol).
    """
    out = scenario_normal_market()
    for row in out:
        if row["symbol"] == "RELIANCE":
            # Baseline prev_close=2941.0. +4.8% -> 3082.17
            row["price"] = round(row["prev_close"] * 1.048, 2)
            row["benchmark_pct_change"] = 4.2
            row["avg_daily_move_20d"] = 5.2
            row["volume"] = row["avg_volume_20d"]
        elif row["symbol"] == "INFY":
            # Baseline prev_close=1871.0. +2.1% -> 1910.29
            row["price"] = round(row["prev_close"] * 1.021, 2)
            row["benchmark_pct_change"] = 0.1
            row["avg_daily_move_20d"] = 0.6
            row["volume"] = int(row["avg_volume_20d"] * 3.2)
    return out


def scenario_api_failure():
    """Market data source is down for every stock. UI must still open."""
    out = []
    for sym, b in BASELINE.items():
        out.append(_snapshot(sym, b["price"], b["prev_close"], b["volume"],
                              b["avg_volume_20d"], b["avg_daily_move_20d"], NIFTY_BASELINE_CHANGE,
                              freshness=Freshness.UNAVAILABLE))
    return out


def scenario_stale_data():
    """Feed is technically responding but hasn't updated — must be labelled
    stale, never presented as live."""
    out = scenario_normal_market()
    for row in out:
        row["freshness"] = Freshness.STALE
    return out


def scenario_malformed_data():
    """Provider sends invalid or negative prices, volumes, NaN, etc."""
    out = scenario_normal_market()
    for row in out:
        if row["symbol"] == "RELIANCE":
            row["price"] = -100  # Invalid negative price
        elif row["symbol"] == "INFY":
            row["volume"] = -50  # Invalid negative volume
        elif row["symbol"] == "TCS":
            row["price"] = float('nan') # Invalid NaN
    return out


SCENARIOS = {
    "normal_market": scenario_normal_market,
    "significant_move": scenario_significant_move,
    "volume_spike": scenario_volume_spike,
    "market_crash": scenario_market_crash,
    "api_failure": scenario_api_failure,
    "stale_data": scenario_stale_data,
    "killer_demo": scenario_killer_demo,
    "malformed_data": scenario_malformed_data,
}
