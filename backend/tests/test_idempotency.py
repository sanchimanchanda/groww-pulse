from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_acknowledge_idempotency():
    # Setup: load normal scenario to get some data
    res = client.post("/demo/scenario", json={"scenario": "normal_market"})
    assert res.status_code == 200

    # Get watchlist to find a symbol
    res = client.get("/watchlists/1/changes")
    assert res.status_code == 200
    data = res.json()
    items = data["items"]
    assert len(items) > 0
    symbol = items[0]["symbol"]

    # First acknowledge
    res1 = client.post(f"/stocks/{symbol}/acknowledge?user_id=1")
    assert res1.status_code == 200

    # Second acknowledge immediately (simulate double click)
    res2 = client.post(f"/stocks/{symbol}/acknowledge?user_id=1")
    assert res2.status_code == 200

    # Third acknowledge
    res3 = client.post(f"/stocks/{symbol}/acknowledge?user_id=1")
    assert res3.status_code == 200
