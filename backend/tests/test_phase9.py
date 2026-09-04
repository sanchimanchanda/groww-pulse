from app.engine import evaluate, MarketSnapshot, Freshness, Verdict, Significance, Confidence, detect_market_regime
import math

def test_live_data_remains_live():
    snap = MarketSnapshot(symbol="TEST", price=105, prev_close=100, volume=1000, avg_volume_20d=1000, avg_daily_move_20d=1.0, benchmark_pct_change=0.0, history_days=20, freshness=Freshness.LIVE)
    res = evaluate(snap)
    assert res.freshness == Freshness.LIVE
    assert res.confidence == Confidence.HIGH

def test_delayed_data_is_labeled_delayed():
    snap = MarketSnapshot(symbol="TEST", price=105, prev_close=100, volume=1000, avg_volume_20d=1000, avg_daily_move_20d=1.0, benchmark_pct_change=0.0, history_days=20, freshness=Freshness.DELAYED)
    res = evaluate(snap)
    assert res.freshness == Freshness.DELAYED

def test_stale_data_lowers_confidence():
    snap = MarketSnapshot(symbol="TEST", price=105, prev_close=100, volume=1000, avg_volume_20d=1000, avg_daily_move_20d=1.0, benchmark_pct_change=0.0, history_days=20, freshness=Freshness.STALE)
    res = evaluate(snap)
    assert res.freshness == Freshness.STALE
    assert res.confidence == Confidence.LOW

def test_stale_does_not_become_no_change():
    # 5% move vs 1% normal is significant
    snap = MarketSnapshot(symbol="TEST", price=105, prev_close=100, volume=1000, avg_volume_20d=1000, avg_daily_move_20d=1.0, benchmark_pct_change=0.0, history_days=20, freshness=Freshness.STALE)
    res = evaluate(snap)
    assert res.verdict != Verdict.NO_CHANGE
    assert res.significance == Significance.HIGH # Significance remains unchanged
    # It gets downgraded to watch because of LOW confidence
    assert res.verdict == Verdict.WATCH

def test_unavailable_does_not_become_no_change():
    snap = MarketSnapshot(symbol="TEST", price=105, prev_close=100, volume=1000, avg_volume_20d=1000, avg_daily_move_20d=1.0, benchmark_pct_change=0.0, history_days=20, freshness=Freshness.UNAVAILABLE)
    res = evaluate(snap)
    assert res.verdict == Verdict.UNAVAILABLE
    assert res.verdict != Verdict.NO_CHANGE

def test_invalid_numeric_values_are_safely_handled():
    snap = MarketSnapshot(symbol="TEST", price=-100, prev_close=100, volume=1000, avg_volume_20d=1000, avg_daily_move_20d=1.0, benchmark_pct_change=0.0, history_days=20, freshness=Freshness.LIVE)
    assert snap.price is None
    assert snap.freshness == Freshness.UNAVAILABLE

def test_missing_volume_does_not_crash():
    snap = MarketSnapshot(symbol="TEST", price=105, prev_close=100, volume=-10, avg_volume_20d=1000, avg_daily_move_20d=1.0, benchmark_pct_change=0.0, history_days=20, freshness=Freshness.LIVE)
    assert snap.volume is None
    res = evaluate(snap)
    # Price is valid, evaluate shouldn't crash
    assert res.verdict != Verdict.UNAVAILABLE

def test_missing_benchmark_prevents_fabricated_comparison():
    res = detect_market_regime([], None)
    assert res.benchmark_change is None
    assert res.regime == "normal"

def test_completely_unavailable_data_does_not_enter_attention():
    from app.engine import calculate_attention
    item = {"verdict": "unavailable", "score": 0.0, "market_context": "normal", "confidence": "LOW", "is_new_to_state": False}
    assert calculate_attention(item) == -1.0
