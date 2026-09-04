"""
Phase 11A — Goal-Anchored Watchlists
Tests for PUT/GET /watchlists/{id}/context
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

WATCHLIST_ID = 1  # seeded by startup


def _reset_context():
    """Remove any stored context between tests so each test starts clean."""
    client.put(f"/watchlists/{WATCHLIST_ID}/context", json={"goal": None, "horizon": None})


class TestCreateGoal:
    def test_create_goal_and_horizon(self):
        _reset_context()
        res = client.put(
            f"/watchlists/{WATCHLIST_ID}/context",
            json={"goal": "LONG_TERM_WEALTH", "horizon": "LONG_TERM"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["goal"] == "LONG_TERM_WEALTH"
        assert data["horizon"] == "LONG_TERM"

    def test_get_returns_stored_context(self):
        _reset_context()
        client.put(
            f"/watchlists/{WATCHLIST_ID}/context",
            json={"goal": "GROWTH", "horizon": "MEDIUM_TERM"},
        )
        res = client.get(f"/watchlists/{WATCHLIST_ID}/context")
        assert res.status_code == 200
        data = res.json()
        assert data["goal"] == "GROWTH"
        assert data["horizon"] == "MEDIUM_TERM"

    def test_update_goal_second_put_wins(self):
        _reset_context()
        client.put(
            f"/watchlists/{WATCHLIST_ID}/context",
            json={"goal": "DIVIDEND", "horizon": "LONG_TERM"},
        )
        client.put(
            f"/watchlists/{WATCHLIST_ID}/context",
            json={"goal": "VALUE", "horizon": "SHORT_TERM"},
        )
        res = client.get(f"/watchlists/{WATCHLIST_ID}/context")
        data = res.json()
        assert data["goal"] == "VALUE"
        assert data["horizon"] == "SHORT_TERM"

    def test_null_goal_clears_stored_value(self):
        client.put(
            f"/watchlists/{WATCHLIST_ID}/context",
            json={"goal": "RETIREMENT", "horizon": "LONG_TERM"},
        )
        client.put(
            f"/watchlists/{WATCHLIST_ID}/context",
            json={"goal": None, "horizon": None},
        )
        res = client.get(f"/watchlists/{WATCHLIST_ID}/context")
        data = res.json()
        assert data["goal"] is None
        assert data["horizon"] is None

    def test_all_valid_goals_accepted(self):
        valid_goals = [
            "GENERAL", "LONG_TERM_WEALTH", "RETIREMENT",
            "GROWTH", "DIVIDEND", "VALUE", "SECTOR_THEME",
        ]
        for goal in valid_goals:
            res = client.put(
                f"/watchlists/{WATCHLIST_ID}/context",
                json={"goal": goal, "horizon": "MEDIUM_TERM"},
            )
            assert res.status_code == 200, f"Expected 200 for goal={goal}, got {res.status_code}"

    def test_all_valid_horizons_accepted(self):
        for horizon in ["SHORT_TERM", "MEDIUM_TERM", "LONG_TERM"]:
            res = client.put(
                f"/watchlists/{WATCHLIST_ID}/context",
                json={"goal": "GENERAL", "horizon": horizon},
            )
            assert res.status_code == 200, f"Expected 200 for horizon={horizon}"


class TestInvalidGoal:
    def test_invalid_goal_rejected(self):
        res = client.put(
            f"/watchlists/{WATCHLIST_ID}/context",
            json={"goal": "YOLO", "horizon": "LONG_TERM"},
        )
        assert res.status_code == 422

    def test_invalid_horizon_rejected(self):
        res = client.put(
            f"/watchlists/{WATCHLIST_ID}/context",
            json={"goal": "GROWTH", "horizon": "FOREVER"},
        )
        assert res.status_code == 422

    def test_unknown_watchlist_returns_404(self):
        res = client.put(
            "/watchlists/9999/context",
            json={"goal": "GROWTH", "horizon": "LONG_TERM"},
        )
        assert res.status_code == 404


class TestWatchlistWithoutGoal:
    def test_get_changes_works_without_context(self):
        """Existing /changes endpoint must be unaffected whether context exists or not."""
        _reset_context()
        res = client.get(f"/watchlists/{WATCHLIST_ID}/changes")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert len(data["items"]) > 0

    def test_get_context_returns_nulls_when_not_set(self):
        _reset_context()
        res = client.get(f"/watchlists/{WATCHLIST_ID}/context")
        assert res.status_code == 200
        data = res.json()
        assert data["goal"] is None
        assert data["horizon"] is None
