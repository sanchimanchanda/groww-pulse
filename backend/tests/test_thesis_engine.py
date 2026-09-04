"""
Phase 11C — Thesis Review Engine
Tests for evaluate_thesis deterministic logic.
"""
from app.thesis import evaluate_thesis


def test_growth_thesis_underperformance_triggers_review():
    evidence = {
        "relative_delta_pp": -5.1,
        "pct_change": -3.0,
        "volatility_multiple": 1.0,
    }
    result = evaluate_thesis("GROWTH", evidence)
    assert result["status"] == "REVIEW"
    assert "underperformed" in result["reason"]


def test_growth_thesis_downward_trend_triggers_review():
    evidence = {
        "relative_delta_pp": -1.0,
        "pct_change": -4.0,
        "volatility_multiple": 2.5,
    }
    result = evaluate_thesis("GROWTH", evidence)
    assert result["status"] == "REVIEW"
    assert "Persistent downward trend" in result["reason"]


def test_growth_thesis_normal_movement_no_review():
    evidence = {
        "relative_delta_pp": 2.0,
        "pct_change": 3.0,
        "volatility_multiple": 1.5,
    }
    result = evaluate_thesis("GROWTH", evidence)
    assert result["status"] == "OK"
    assert result["reason"] is None


def test_dividend_thesis_large_drop_triggers_review():
    evidence = {
        "pct_change": -10.5,
        "volatility_multiple": 1.0,
    }
    result = evaluate_thesis("DIVIDEND", evidence)
    assert result["status"] == "REVIEW"
    assert "capital loss" in result["reason"]


def test_value_thesis_high_volatility_triggers_review():
    evidence = {
        "pct_change": 1.0,
        "volatility_multiple": 3.5,
    }
    result = evaluate_thesis("VALUE", evidence)
    assert result["status"] == "REVIEW"
    assert "High volatility" in result["reason"]


def test_unknown_thesis_type_defaults_to_ok():
    evidence = {
        "relative_delta_pp": -10.0,
        "pct_change": -20.0,
        "volatility_multiple": 5.0,
    }
    result = evaluate_thesis("GENERAL", evidence)
    assert result["status"] == "OK"
    assert result["reason"] is None
