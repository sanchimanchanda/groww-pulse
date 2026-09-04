"""
Phase 11F — Valuation Context
Tests for valuation classification and API.
"""
from app.valuation import classify_valuation
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_below_median():
    res = classify_valuation(current_pe=22.0, historical_pe_median=28.0, historical_pe_low=19.0, historical_pe_high=34.0)
    assert res["label"] == "BELOW_HISTORICAL_RANGE"
    assert res["delta_vs_median_pct"] == -21.4


def test_near_median():
    res = classify_valuation(current_pe=28.5, historical_pe_median=28.0, historical_pe_low=19.0, historical_pe_high=34.0)
    assert res["label"] == "NEAR_MEDIAN"
    assert res["delta_vs_median_pct"] == 1.8


def test_above_median():
    res = classify_valuation(current_pe=38.0, historical_pe_median=28.0, historical_pe_low=19.0, historical_pe_high=34.0)
    assert res["label"] == "ABOVE_HISTORICAL_RANGE"
    assert res["delta_vs_median_pct"] == 35.7


def test_missing_pe_returns_unavailable():
    res = classify_valuation(current_pe=None, historical_pe_median=28.0, historical_pe_low=19.0, historical_pe_high=34.0)
    assert res["label"] == "DATA_UNAVAILABLE"


def test_valuation_endpoint_seeded_data():
    res = client.get("/stocks/INFY/valuation")
    assert res.status_code == 200
    data = res.json()
    assert data["available"] is True
    assert data["current_pe"] == 22.4
    assert data["label"] == "BELOW_HISTORICAL_RANGE"
    assert data["delta_vs_median_pct"] == -20.3


def test_valuation_endpoint_missing_stock():
    res = client.get("/stocks/FAKESYM/valuation")
    assert res.status_code == 404
