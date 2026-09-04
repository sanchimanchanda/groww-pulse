"""
Phase 11G — Earnings & Dividend Events
Tests for /stocks/{symbol}/events
"""
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app import models
from datetime import datetime, timedelta
import pytest

client = TestClient(app)


def test_upcoming_event_returned():
    res = client.get("/stocks/INFY/events")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[0]["event_type"] == "EARNINGS"
    assert data[0]["days_until"] >= 0


def test_no_event_returns_empty_list():
    res = client.get("/stocks/TCS/events")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_past_event_not_returned():
    db = SessionLocal()
    stock = db.query(models.Stock).filter_by(symbol="TCS").first()
    past_event = models.StockEvent(
        stock_id=stock.id,
        event_type="EARNINGS",
        event_date=datetime.utcnow() - timedelta(days=5),
        title="Past Event"
    )
    db.add(past_event)
    db.commit()
    
    res = client.get("/stocks/TCS/events")
    assert res.status_code == 200
    data = res.json()
    # Ensure the past event is not returned
    assert len([e for e in data if e["title"] == "Past Event"]) == 0
    
    db.delete(past_event)
    db.commit()
    db.close()


def test_unknown_stock_returns_404():
    res = client.get("/stocks/FAKESYM/events")
    assert res.status_code == 404
