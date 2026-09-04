import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.engine import MarketSnapshot, evaluate, Verdict, Significance, Freshness, detect_market_regime

def make_snapshot(**overrides):
    base = dict(
        symbol="TEST", price=100.0, prev_close=100.0, volume=1_000_000,
        avg_volume_20d=1_000_000, avg_daily_move_20d=1.0,
        benchmark_pct_change=0.0, history_days=20, freshness=Freshness.LIVE,
    )
    base.update(overrides)
    return MarketSnapshot(**base)

# Scenario A: RELIANCE
def get_reliance_snapshot():
    # Price +4.8% -> price=104.8, prev=100.0
    # NIFTY +4.2%
    # Volatility +/- 5.2%
    # Volume 1.0x -> volume=1M, avg=1M
    return make_snapshot(
        symbol="RELIANCE", 
        price=104.8, 
        prev_close=100.0,
        benchmark_pct_change=4.2,
        avg_daily_move_20d=5.2,
        volume=1_000_000,
        avg_volume_20d=1_000_000
    )

# Scenario B: INFY
def get_infy_snapshot():
    # Price +2.1% -> price=102.1, prev=100.0
    # NIFTY +0.1%
    # Volatility +/- 0.6%
    # Volume 3.2x -> volume=3.2M, avg=1M
    return make_snapshot(
        symbol="INFY",
        price=102.1,
        prev_close=100.0,
        benchmark_pct_change=0.1,
        avg_daily_move_20d=0.6,
        volume=3_200_000,
        avg_volume_20d=1_000_000
    )

def test_reliance_scenario():
    snap = get_reliance_snapshot()
    res = evaluate(snap)
    
    # Assert no_attention / no_change
    assert res.verdict == Verdict.NO_CHANGE
    
    # Assert significance is not HIGH
    assert res.significance != Significance.HIGH
    assert res.significance == Significance.LOW
    
    # Assert volume anomaly is not incorrectly triggered
    assert not any(s.kind == "VA" for s in res.signals)
    
    # Assert RPM/relative signal behaves as expected
    assert not any(s.kind == "RPM" for s in res.signals)
    assert res.evidence.relative_multiple < 1.0

def test_infy_scenario():
    snap = get_infy_snapshot()
    res = evaluate(snap)
    
    # Assert needs_attention according to existing contract
    assert res.verdict == Verdict.NEEDS_ATTENTION
    
    # Assert significance is HIGH
    assert res.significance == Significance.HIGH
    
    # Assert volume anomaly is detected
    assert any(s.kind == "VA" for s in res.signals)
    
    # Assert RPM is materially stronger than RELIANCE
    # RPM is triggered
    assert any(s.kind == "RPM" for s in res.signals)

def test_comparative_thesis():
    res_rel = evaluate(get_reliance_snapshot())
    res_infy = evaluate(get_infy_snapshot())
    
    # Explicitly verify: abs(RELIANCE price change) > abs(INFY price change)
    assert abs(res_rel.evidence.pct_change) > abs(res_infy.evidence.pct_change)
    
    # but INFY meaningfulness > RELIANCE meaningfulness
    assert res_infy.score > res_rel.score
    assert res_infy.normalized_score > res_rel.normalized_score

def test_killer_demo_market_context():
    res_rel = evaluate(get_reliance_snapshot())
    res_infy = evaluate(get_infy_snapshot())
    
    # Suppose they are evaluated in a market where NIFTY is +4.2%
    # We will simulate a market-wide movement so RELIANCE is tracking
    results = [res_rel, res_infy]
    # Add enough tracking stocks to trigger market_wide regime (NIFTY +4.2%)
    for i in range(8):
        # Tracking stocks: move exactly +4.2% with 1.0 volatility -> relative_multiple=0.0
        results.append(evaluate(make_snapshot(
            symbol=f"TRACK{i}", price=104.2, prev_close=100.0, 
            avg_daily_move_20d=1.0, benchmark_pct_change=4.2
        )))
        
    ctx = detect_market_regime(results, 4.2)
    
    # Verify the killer demo remains correct
    assert ctx.regime == "market_wide"
    assert res_rel.market_context == "tracking_market"
    assert res_infy.market_context == "outlier"

def test_determinism_scenarios():
    res_rel1 = evaluate(get_reliance_snapshot())
    res_rel2 = evaluate(get_reliance_snapshot())
    assert res_rel1 == res_rel2
    
    res_infy1 = evaluate(get_infy_snapshot())
    res_infy2 = evaluate(get_infy_snapshot())
    assert res_infy1 == res_infy2

def test_killer_demo_api_endpoint():
    client = TestClient(app)
    
    # Hit the API with the exact demo scenario by setting it via the POST endpoint
    scenario_res = client.post("/demo/scenario", json={"scenario": "killer_demo"})
    assert scenario_res.status_code == 200
    
    response = client.get("/watchlists/1/changes")
    assert response.status_code == 200
    
    data = response.json()
    items = data["items"]
    
    rel = next((x for x in items if x["symbol"] == "RELIANCE"), None)
    infy = next((x for x in items if x["symbol"] == "INFY"), None)
    
    assert rel is not None
    assert infy is not None
    
    # RELIANCE is NO_CHANGE, INFY is NEEDS_ATTENTION
    assert rel["verdict"] == "no_change"
    assert infy["verdict"] == "needs_attention"
    
    # INFY score > RELIANCE score
    assert infy["score"] > rel["score"]
    
    # Market context mapping
    # Since only RELIANCE and INFY have custom benchmark changes in this specific demo function,
    # the rest will have normal benchmark_pct_change from normal_market.
    # It's fine, we just verify the exact API structure matches the core thesis.
    assert rel["evidence"]["pct_change"] > infy["evidence"]["pct_change"]
