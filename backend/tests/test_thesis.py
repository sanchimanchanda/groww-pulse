"""
Phase 11B — Thesis Tracking
Tests for PUT/GET /watchlists/{id}/items/{symbol}/thesis
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

WATCHLIST_ID = 1
SYMBOL = "INFY"


def _reset_thesis():
    """Reset INFY thesis via a known-good value so subsequent tests start clean."""
    client.put(
        f"/watchlists/{WATCHLIST_ID}/items/{SYMBOL}/thesis",
        json={"thesis_type": "GENERAL", "thesis_note": None},
    )


class TestCreateThesis:
    def test_create_thesis_with_type_only(self):
        res = client.put(
            f"/watchlists/{WATCHLIST_ID}/items/{SYMBOL}/thesis",
            json={"thesis_type": "GROWTH"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["thesis_type"] == "GROWTH"
        assert data["symbol"] == SYMBOL

    def test_create_thesis_with_note(self):
        res = client.put(
            f"/watchlists/{WATCHLIST_ID}/items/{SYMBOL}/thesis",
            json={"thesis_type": "GROWTH", "thesis_note": "AI/cloud long-term play"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["thesis_type"] == "GROWTH"
        assert data["thesis_note"] == "AI/cloud long-term play"

    def test_get_returns_stored_thesis(self):
        client.put(
            f"/watchlists/{WATCHLIST_ID}/items/{SYMBOL}/thesis",
            json={"thesis_type": "VALUE", "thesis_note": "Undervalued vs peers"},
        )
        res = client.get(f"/watchlists/{WATCHLIST_ID}/items/{SYMBOL}/thesis")
        assert res.status_code == 200
        data = res.json()
        assert data["thesis_type"] == "VALUE"
        assert data["thesis_note"] == "Undervalued vs peers"

    def test_update_thesis_second_put_wins(self):
        client.put(
            f"/watchlists/{WATCHLIST_ID}/items/{SYMBOL}/thesis",
            json={"thesis_type": "DIVIDEND"},
        )
        client.put(
            f"/watchlists/{WATCHLIST_ID}/items/{SYMBOL}/thesis",
            json={"thesis_type": "RECOVERY", "thesis_note": "Post correction bounce"},
        )
        res = client.get(f"/watchlists/{WATCHLIST_ID}/items/{SYMBOL}/thesis")
        data = res.json()
        assert data["thesis_type"] == "RECOVERY"
        assert data["thesis_note"] == "Post correction bounce"

    def test_all_valid_thesis_types_accepted(self):
        valid_types = [
            "GENERAL", "GROWTH", "DIVIDEND", "VALUE", "RECOVERY", "SECTOR_OPPORTUNITY"
        ]
        for t in valid_types:
            res = client.put(
                f"/watchlists/{WATCHLIST_ID}/items/{SYMBOL}/thesis",
                json={"thesis_type": t},
            )
            assert res.status_code == 200, f"Expected 200 for thesis_type={t}"

    def test_thesis_note_whitespace_stripped(self):
        res = client.put(
            f"/watchlists/{WATCHLIST_ID}/items/{SYMBOL}/thesis",
            json={"thesis_type": "GROWTH", "thesis_note": "  trimmed  "},
        )
        assert res.status_code == 200
        assert res.json()["thesis_note"] == "trimmed"


class TestInvalidThesis:
    def test_invalid_thesis_type_rejected(self):
        res = client.put(
            f"/watchlists/{WATCHLIST_ID}/items/{SYMBOL}/thesis",
            json={"thesis_type": "MOONSHOT"},
        )
        assert res.status_code == 422

    def test_thesis_note_over_500_chars_rejected(self):
        long_note = "x" * 501
        res = client.put(
            f"/watchlists/{WATCHLIST_ID}/items/{SYMBOL}/thesis",
            json={"thesis_type": "GROWTH", "thesis_note": long_note},
        )
        assert res.status_code == 422

    def test_thesis_note_exactly_500_chars_accepted(self):
        ok_note = "x" * 500
        res = client.put(
            f"/watchlists/{WATCHLIST_ID}/items/{SYMBOL}/thesis",
            json={"thesis_type": "GROWTH", "thesis_note": ok_note},
        )
        assert res.status_code == 200

    def test_unknown_symbol_returns_404(self):
        res = client.put(
            f"/watchlists/{WATCHLIST_ID}/items/FAKESYM/thesis",
            json={"thesis_type": "GROWTH"},
        )
        assert res.status_code == 404

    def test_unknown_watchlist_returns_404(self):
        res = client.put(
            f"/watchlists/9999/items/{SYMBOL}/thesis",
            json={"thesis_type": "GROWTH"},
        )
        assert res.status_code == 404


class TestGetWithoutThesis:
    def test_get_returns_nulls_when_not_set(self):
        """GET returns null thesis_type when no thesis has been stored."""
        # Use a different symbol that likely has no thesis yet
        res = client.get(f"/watchlists/{WATCHLIST_ID}/items/MARUTI/thesis")
        assert res.status_code == 200
        data = res.json()
        assert data["thesis_type"] is None
