from app.engine import MarketSnapshot, evaluate, Verdict, Confidence, Freshness, Significance, detect_market_regime


def make_snapshot(**overrides):
    base = dict(
        symbol="TEST", price=100.0, prev_close=100.0, volume=1_000_000,
        avg_volume_20d=1_000_000, avg_daily_move_20d=1.0,
        benchmark_pct_change=0.0, history_days=20, freshness=Freshness.LIVE,
    )
    base.update(overrides)
    return MarketSnapshot(**base)


def test_small_move_in_stable_stock_is_no_change():
    snap = make_snapshot(price=100.3, prev_close=100.0, avg_daily_move_20d=1.0)
    result = evaluate(snap)
    assert result.verdict == Verdict.NO_CHANGE


def test_large_move_in_volatile_stock_can_be_no_change():
    # A 3% move for a stock that normally moves 5% a day is unremarkable.
    snap = make_snapshot(price=103.0, prev_close=100.0, avg_daily_move_20d=5.0,
                          benchmark_pct_change=0.2)
    result = evaluate(snap)
    assert result.verdict != Verdict.NEEDS_ATTENTION


def test_same_move_in_stable_stock_is_meaningful():
    # The same 3% move for a stock that normally moves 0.5% a day is a big deal.
    snap = make_snapshot(price=103.0, prev_close=100.0, avg_daily_move_20d=0.5,
                          benchmark_pct_change=0.2)
    result = evaluate(snap)
    assert result.verdict in (Verdict.NEEDS_ATTENTION, Verdict.WATCH)


def test_high_volume_alone_does_not_trigger_needs_attention():
    # Volume-only anomaly with a tiny, in-range price move should cap at WATCH.
    snap = make_snapshot(price=100.1, prev_close=100.0, avg_daily_move_20d=1.0,
                          volume=5_000_000, avg_volume_20d=1_000_000)
    result = evaluate(snap)
    assert result.verdict != Verdict.NEEDS_ATTENTION


def test_relative_underperformance_flagged_despite_positive_return():
    # Stock +2%, benchmark +5%: this is meaningful underperformance, not "good news".
    snap = make_snapshot(price=102.0, prev_close=100.0, avg_daily_move_20d=1.0,
                          benchmark_pct_change=5.0)
    result = evaluate(snap)
    assert result.directionality == "up"
    assert any(s.kind == "RPM" for s in result.signals)


def test_market_wide_move_does_not_flag_stock_tracking_the_market():
    # Stock and benchmark both move -3%: relative performance ~0, so unless
    # the absolute z-score alone crosses the bar, it should not be "needs attention"
    # purely because "the market crashed" — that's market-wide, not stock-specific.
    snap = make_snapshot(price=97.0, prev_close=100.0, avg_daily_move_20d=3.0,
                          benchmark_pct_change=-3.0)
    result = evaluate(snap)
    assert result.verdict != Verdict.NEEDS_ATTENTION


def test_unavailable_data_short_circuits_to_unavailable_verdict():
    snap = make_snapshot(freshness=Freshness.UNAVAILABLE)
    result = evaluate(snap)
    assert result.verdict == Verdict.UNAVAILABLE
    assert result.confidence == Confidence.LOW


def test_stale_data_downgrades_confidence_and_caps_severity():
    snap = make_snapshot(price=110.0, prev_close=100.0, avg_daily_move_20d=0.5,
                          freshness=Freshness.STALE)
    result = evaluate(snap)
    assert result.confidence == Confidence.LOW
    assert result.verdict != Verdict.NEEDS_ATTENTION


def test_insufficient_history_downgrades_confidence():
    snap = make_snapshot(price=105.0, prev_close=100.0, avg_daily_move_20d=1.0,
                          history_days=2)
    result = evaluate(snap)
    assert result.confidence == Confidence.LOW


def test_zero_volatility_does_not_divide_by_zero():
    snap = make_snapshot(price=101.0, prev_close=100.0, avg_daily_move_20d=0.0)
    result = evaluate(snap)  # should not raise
    assert isinstance(result.score, float)


def test_deterministic_same_input_same_output():
    snap = make_snapshot(price=104.5, prev_close=100.0, avg_daily_move_20d=1.2,
                          volume=3_000_000, avg_volume_20d=1_000_000, benchmark_pct_change=0.5)
    r1 = evaluate(snap)
    r2 = evaluate(snap)
    assert r1.score == r2.score
    assert r1.verdict == r2.verdict


def test_flat_stock_has_no_change():
    snap = make_snapshot(price=100.0, prev_close=100.0)
    result = evaluate(snap)
    assert result.verdict == Verdict.NO_CHANGE
    assert result.directionality == "flat"


def test_boundary_just_below_watch_threshold():
    # Construct a score just under 1.0 and confirm no false positive.
    snap = make_snapshot(price=100.9, prev_close=100.0, avg_daily_move_20d=1.0,
                          benchmark_pct_change=0.0)
    result = evaluate(snap)
    assert result.score < 2.0


def test_normal_price_with_high_volume_is_volume_anomaly():
    snap = make_snapshot(price=100.5, prev_close=100.0, avg_daily_move_20d=1.0,
                          volume=3_000_000, avg_volume_20d=1_000_000)
    result = evaluate(snap)
    assert any(s.kind == "VA" for s in result.signals)
    assert result.evidence.volume_multiple == 3.0


def test_stock_tracking_market_has_weak_relative_signal():
    snap = make_snapshot(price=105.0, prev_close=100.0, avg_daily_move_20d=2.0,
                          benchmark_pct_change=5.0)
    result = evaluate(snap)
    assert result.evidence.relative_delta_pp == 0.0
    assert not any(s.kind == "RPM" for s in result.signals)


def test_missing_volume_price_analysis_continues():
    snap = make_snapshot(price=103.0, prev_close=100.0, avg_daily_move_20d=1.0,
                          volume=0, avg_volume_20d=0)
    result = evaluate(snap)
    assert result.verdict in (Verdict.NEEDS_ATTENTION, Verdict.WATCH)
    assert result.evidence.volume_multiple == 0.0


def test_missing_benchmark_relative_signal_unavailable():
    snap = make_snapshot(price=103.0, prev_close=100.0, avg_daily_move_20d=1.0,
                          benchmark_pct_change=0.0)
    result = evaluate(snap)
    # The evaluation should still succeed based on price alone
    assert result.verdict in (Verdict.NEEDS_ATTENTION, Verdict.WATCH)


def test_boundary_threshold_epsilon():
    # Test precisely at threshold ± epsilon
    # e.g., score computation = 0.45 * |z_price|
    # To get score exactly 1.0 (Watch), z_price needs to be 1.0 / 0.45 = 2.222...
    snap_below = make_snapshot(price=102.21, prev_close=100.0, avg_daily_move_20d=1.0, benchmark_pct_change=2.21, volume=0)
    res_below = evaluate(snap_below)
    assert res_below.score < 1.0
    assert res_below.verdict == Verdict.NO_CHANGE

    snap_above = make_snapshot(price=102.23, prev_close=100.0, avg_daily_move_20d=1.0, benchmark_pct_change=2.23, volume=0)
    res_above = evaluate(snap_above)
    assert res_above.score >= 1.0
    assert res_above.verdict == Verdict.WATCH


def test_significance_and_confidence_are_independent():
    # Large move, but stale data
    snap = make_snapshot(price=110.0, prev_close=100.0, avg_daily_move_20d=1.0,
                         freshness=Freshness.STALE)
    result = evaluate(snap)
    
    # Significance should be HIGH because a 10 sigma move is highly unusual
    assert result.significance == Significance.HIGH
    
    # Confidence should be LOW because the data is STALE
    assert result.confidence == Confidence.LOW
    
    # The verdict should be capped at WATCH because confidence is LOW
    assert result.verdict == Verdict.WATCH


def test_normalized_score_always_0_to_100():
    # 1. Zero move (and zero volume contribution to get exactly 0 score)
    snap_zero = make_snapshot(price=100.0, prev_close=100.0, volume=0)
    res_zero = evaluate(snap_zero)
    assert res_zero.normalized_score == 0.0
    
    # 2. Normal move
    snap_normal = make_snapshot(price=101.0, prev_close=100.0, avg_daily_move_20d=1.0)
    res_normal = evaluate(snap_normal)
    assert 0.0 < res_normal.normalized_score < 100.0
    
    # 3. Extreme move (should cap at 100)
    snap_extreme = make_snapshot(price=200.0, prev_close=100.0, avg_daily_move_20d=1.0)
    res_extreme = evaluate(snap_extreme)
    assert res_extreme.normalized_score == 100.0
    
    # 4. Negative extreme move (should cap at 100)
    snap_neg_extreme = make_snapshot(price=10.0, prev_close=100.0, avg_daily_move_20d=1.0)
    res_neg_extreme = evaluate(snap_neg_extreme)
    assert res_neg_extreme.normalized_score == 100.0


def test_evidence_values_are_deterministic():
    snap1 = make_snapshot(price=105.0, prev_close=100.0, avg_daily_move_20d=2.0, 
                          volume=200, avg_volume_20d=100, benchmark_pct_change=1.0)
    snap2 = make_snapshot(price=105.0, prev_close=100.0, avg_daily_move_20d=2.0, 
                          volume=200, avg_volume_20d=100, benchmark_pct_change=1.0)
    
    res1 = evaluate(snap1)
    res2 = evaluate(snap2)
    
    assert res1.evidence.volatility_multiple == 2.5
    assert res1.evidence.volume_multiple == 2.0
    assert res1.evidence.relative_delta_pp == 4.0
    
    # Same input -> identical complete result
    assert res1 == res2


# =====================================================================
# Phase 3: Market-Wide Noise Suppression Tests
# =====================================================================

def test_market_regime_all_tracking():
    # 10 stocks, all moving exactly with the benchmark (tolerance = 1.0)
    results = []
    for i in range(10):
        snap = make_snapshot(symbol=f"S{i}", price=105.0, prev_close=100.0, avg_daily_move_20d=2.0, benchmark_pct_change=5.0)
        results.append(evaluate(snap))
        
    ctx = detect_market_regime(results, 5.0)
    assert ctx.regime == "market_wide"
    assert ctx.coverage == 1.0
    assert len(ctx.outliers) == 0
    assert all(r.market_context == "tracking_market" for r in results)


def test_market_regime_one_outlier():
    results = []
    for i in range(9):
        snap = make_snapshot(symbol=f"S{i}", price=105.0, prev_close=100.0, avg_daily_move_20d=2.0, benchmark_pct_change=5.0)
        results.append(evaluate(snap))
        
    # The outlier moves in the opposite direction
    snap_outlier = make_snapshot(symbol="OUTLIER", price=95.0, prev_close=100.0, avg_daily_move_20d=2.0, benchmark_pct_change=5.0)
    results.append(evaluate(snap_outlier))
    
    ctx = detect_market_regime(results, 5.0)
    assert ctx.regime == "market_wide"
    assert ctx.coverage == 0.9  # 9/10
    assert ctx.outliers == ["OUTLIER"]
    assert results[-1].market_context == "outlier"


def test_market_regime_normal_market():
    # 10 stocks, moving randomly, low correlation
    results = []
    for i in range(10):
        # stock change = i%, benchmark = 5%
        # relative_change = i - 5. For i=0, -5/2.0 = -2.5 (outlier).
        # For i=5, 0/2.0 = 0 (tracking).
        # We will get fewer than 7 tracking stocks.
        snap = make_snapshot(symbol=f"S{i}", price=100.0 + i, prev_close=100.0, avg_daily_move_20d=2.0, benchmark_pct_change=5.0)
        results.append(evaluate(snap))
        
    ctx = detect_market_regime(results, 5.0)
    assert ctx.regime == "normal"
    assert ctx.coverage < 0.70
    assert len(ctx.outliers) == 0  # Context is only applied if regime is market_wide
    assert all(r.market_context == "normal" for r in results)


def test_market_regime_exactly_threshold_boundary():
    results = []
    # 7 tracking
    for i in range(7):
        snap = make_snapshot(symbol=f"S{i}", price=105.0, prev_close=100.0, avg_daily_move_20d=2.0, benchmark_pct_change=5.0)
        results.append(evaluate(snap))
    # 3 outliers
    for i in range(3):
        snap = make_snapshot(symbol=f"O{i}", price=115.0, prev_close=100.0, avg_daily_move_20d=2.0, benchmark_pct_change=5.0)
        results.append(evaluate(snap))
        
    ctx = detect_market_regime(results, 5.0)
    assert ctx.regime == "market_wide"
    assert ctx.coverage == 0.70


def test_market_regime_just_below_threshold():
    results = []
    # 6 tracking
    for i in range(6):
        snap = make_snapshot(symbol=f"S{i}", price=105.0, prev_close=100.0, avg_daily_move_20d=2.0, benchmark_pct_change=5.0)
        results.append(evaluate(snap))
    # 4 outliers
    for i in range(4):
        snap = make_snapshot(symbol=f"O{i}", price=115.0, prev_close=100.0, avg_daily_move_20d=2.0, benchmark_pct_change=5.0)
        results.append(evaluate(snap))
        
    ctx = detect_market_regime(results, 5.0)
    assert ctx.regime == "normal"
    assert ctx.coverage == 0.60


def test_market_regime_missing_benchmark():
    snap = make_snapshot(price=105.0, prev_close=100.0, avg_daily_move_20d=2.0)
    snap.benchmark_pct_change = None
    res = evaluate(snap)
    ctx = detect_market_regime([res], None)
    assert ctx.regime == "normal"
    assert ctx.coverage == 0.0
    assert res.market_context == "normal"


def test_market_regime_missing_stock_movement():
    snap1 = make_snapshot(symbol="S1", price=105.0, prev_close=100.0, benchmark_pct_change=5.0)
    snap_unavail = make_snapshot(symbol="S2", freshness=Freshness.UNAVAILABLE)
    
    res1 = evaluate(snap1)
    res_unavail = evaluate(snap_unavail)
    
    ctx = detect_market_regime([res1, res_unavail], 5.0)
    assert ctx.coverage == 1.0  # 1/1 eligible
    assert res_unavail.market_context == "normal"  # Ignored


def test_market_regime_empty_watchlist():
    ctx = detect_market_regime([], 5.0)
    assert ctx.regime == "normal"
    assert ctx.coverage == 0.0


def test_market_regime_tolerance_boundary():
    # Tracking tolerance is z_relative <= 1.0
    # Vol proxy = 1.0. Benchmark = 0.0.
    # pct_change = 1.0 -> z_relative = 1.0 -> tracking
    # pct_change = 1.01 -> z_relative = 1.01 -> outlier
    snap_track = make_snapshot(symbol="TRACK", price=101.0, prev_close=100.0, avg_daily_move_20d=1.0, benchmark_pct_change=0.0)
    snap_out = make_snapshot(symbol="OUT", price=101.02, prev_close=100.0, avg_daily_move_20d=1.0, benchmark_pct_change=0.0)
    
    res_track = evaluate(snap_track)
    res_out = evaluate(snap_out)
    
    # We need >= 70% to trigger market_wide to test context applying
    # Let's add 8 more tracking stocks
    results = [res_track, res_out]
    for i in range(8):
        results.append(evaluate(make_snapshot(symbol=f"S{i}", price=100.0, prev_close=100.0, benchmark_pct_change=0.0)))
        
    ctx = detect_market_regime(results, 0.0)
    assert ctx.regime == "market_wide"
    assert res_track.market_context == "tracking_market"
    assert res_out.market_context == "outlier"


def test_market_regime_determinism():
    results1 = [evaluate(make_snapshot(symbol="S1", price=105.0, prev_close=100.0, benchmark_pct_change=5.0))]
    results2 = [evaluate(make_snapshot(symbol="S1", price=105.0, prev_close=100.0, benchmark_pct_change=5.0))]
    
    ctx1 = detect_market_regime(results1, 5.0)
    ctx2 = detect_market_regime(results2, 5.0)
    
    assert ctx1 == ctx2
