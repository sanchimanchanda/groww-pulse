"""
Phase 11H — SIP Market Pullback
Tests for SIP context endpoint and logic
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
WATCHLIST_ID = 1


def test_pullback_threshold_reached():
    # Benchmark drop is 6.0% which is <= -5.0%
    res = client.get(f"/watchlists/{WATCHLIST_ID}/sip-context?benchmark_weekly_change=-6.0")
    assert res.status_code == 200
    data = res.json()
    assert data["pullback_detected"] is True
    assert data["benchmark_change"] == -6.0
    assert data["sip"] is not None
    assert data["sip"]["instrument"] == "NIFTY 50 Index Fund"


def test_pullback_threshold_not_reached():
    # Benchmark drop is 3.0% which is > -5.0%
    res = client.get(f"/watchlists/{WATCHLIST_ID}/sip-context?benchmark_weekly_change=-3.0")
    assert res.status_code == 200
    data = res.json()
    assert data["pullback_detected"] is False
    assert data["benchmark_change"] == -3.0
    assert data["sip"] is not None


def test_positive_benchmark_does_not_trigger():
    res = client.get(f"/watchlists/{WATCHLIST_ID}/sip-context?benchmark_weekly_change=2.0")
    assert res.status_code == 200
    data = res.json()
    assert data["pullback_detected"] is False


def test_missing_benchmark_returns_gracefully():
    # Uses default 0.0
    res = client.get(f"/watchlists/{WATCHLIST_ID}/sip-context")
    assert res.status_code == 200
    data = res.json()
    assert data["pullback_detected"] is False
    assert data["benchmark_change"] == 0.0


def test_unknown_watchlist_returns_404():
    res = client.get("/watchlists/999/sip-context?benchmark_weekly_change=-6.0")
    assert res.status_code == 404
