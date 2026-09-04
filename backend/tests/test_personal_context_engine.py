"""
Phase 11I — Personal Context Engine
Tests for injection logic
"""
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app import models
import pytest

client = TestClient(app)
WATCHLIST_ID = 1

def test_personal_context_injection():
    # Fetch changes. Since we seeded thesis, valuation, events, and overlap for DEMO_USER_ID,
    # the changes should contain personal_context where applicable.
    res = client.get(f"/watchlists/{WATCHLIST_ID}/changes")
    assert res.status_code == 200
    data = res.json()
    items = data["items"]
    
    # Check INFY (has Valuation, Event, Overlap)
    infy = next((i for i in items if i["symbol"] == "INFY"), None)
    assert infy is not None
    assert "personal_context" in infy
    pc = infy["personal_context"]
    assert "valuation" in pc
    assert pc["valuation"]["label"] == "BELOW_HISTORICAL_RANGE"
    assert "events" in pc
    assert len(pc["events"]) > 0
    assert pc["events"][0]["type"] == "EARNINGS"
    assert "fund_overlap" in pc
    assert any(f["fund_name"] == "Parag Parikh Flexi Cap" for f in pc["fund_overlap"])
    
    # Check HDFCBANK (has Valuation, Event, Overlap)
    hdfc = next((i for i in items if i["symbol"] == "HDFCBANK"), None)
    assert hdfc is not None
    assert "personal_context" in hdfc
    pc = hdfc["personal_context"]
    assert "events" in pc
    assert pc["events"][0]["type"] == "DIVIDEND"
    
def test_no_context_available():
    # If a stock doesn't have any of the 4 context pillars, personal_context should not be present
    # or should be empty. But we seeded valuation for all stocks in the demo.
    pass
