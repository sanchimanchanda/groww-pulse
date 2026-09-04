"""
Phase 11D — Mutual Fund Overlap
Tests for /funds, /funds/{id}/xray, and /funds/{id}/overlap
"""
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app import models
import pytest

client = TestClient(app)

# The funds are seeded at startup. ID 1 is Parag Parikh, ID 2 is HDFC.
FUND_ID_1 = 1
FUND_ID_2 = 2


def test_fund_lookup():
    res = client.get("/funds")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 2
    names = [f["name"] for f in data]
    assert "Parag Parikh Flexi Cap" in names
    assert "HDFC Flexi Cap" in names


def test_fund_top_holdings():
    res = client.get(f"/funds/{FUND_ID_1}/xray")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Parag Parikh Flexi Cap"
    holdings = data["top_holdings"]
    assert len(holdings) <= 5
    # Should be sorted by weight desc
    assert holdings[0]["symbol"] == "INFY"
    assert holdings[0]["weight"] == 8.2


def test_overlap_calculation():
    """Overlap between Fund 1 and Fund 2 based on seed data.
    Common:
    HDFCBANK: min(6.7, 7.8) = 6.7
    ITC: min(3.1, 6.9) = 3.1
    INFY: min(8.2, 6.2) = 6.2
    Total = 6.7 + 3.1 + 6.2 = 16.0% -> 0.16
    """
    # Assuming user holds both funds (seeded at startup)
    # If we request overlap for Fund 1, it compares with Fund 2.
    res = client.get(f"/funds/{FUND_ID_1}/overlap")
    assert res.status_code == 200
    data = res.json()
    assert data["max_overlap"] == 0.16
    assert set(data["common_symbols"]) == {"INFY", "HDFCBANK", "ITC"}


def test_zero_overlap():
    # Let's create a temporary fund with no common holdings and test overlap.
    db = SessionLocal()
    f3 = models.MutualFund(name="Zero Overlap Fund")
    db.add(f3)
    db.commit()
    db.refresh(f3)
    
    db.add(models.MutualFundHolding(fund_id=f3.id, symbol="XYZ", weight=10.0))
    db.commit()
    
    res = client.get(f"/funds/{f3.id}/overlap")
    assert res.status_code == 200
    data = res.json()
    assert data["max_overlap"] == 0.0
    
    # cleanup
    db.query(models.MutualFundHolding).filter_by(fund_id=f3.id).delete()
    db.delete(f3)
    db.commit()
    db.close()


def test_100_percent_overlap():
    # To test 100% overlap, we'll create a new fund with identical holdings to Fund 1.
    db = SessionLocal()
    f3 = models.MutualFund(name="Identical Fund")
    db.add(f3)
    db.commit()
    db.refresh(f3)
    
    holdings = db.query(models.MutualFundHolding).filter_by(fund_id=FUND_ID_1).all()
    for h in holdings:
        db.add(models.MutualFundHolding(fund_id=f3.id, symbol=h.symbol, weight=h.weight))
    
    db.commit()
    
    res = client.get(f"/funds/{f3.id}/overlap")
    assert res.status_code == 200
    data = res.json()
    # It should overlap 100% with the known holdings of Fund 1 (which sum to 28.7%)
    assert data["max_overlap"] == 0.287
    
    db.query(models.MutualFundHolding).filter_by(fund_id=f3.id).delete()
    db.delete(f3)
    db.commit()
    db.close()


def test_unknown_fund_xray_returns_404():
    res = client.get("/funds/9999/xray")
    assert res.status_code == 404


def test_unknown_fund_overlap_returns_404():
    res = client.get("/funds/9999/overlap")
    assert res.status_code == 404
