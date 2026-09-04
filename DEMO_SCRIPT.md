# Demo Script

Run once: `cd backend && uvicorn app.main:app` then open `http://127.0.0.1:8000`.

## Step 1 — Quiet market
Scenario dropdown is already on "Normal market". Point out: "Your market is
quiet" — no needs-attention section rendered, all 10 stocks in the plain
list. This is the baseline the rest of the demo contrasts against.

## Step 2 — Significant move
Switch scenario to **Significant move**. RELIANCE jumps to the top under
"Needs attention" with: `+4.8%`, and the reason: "moved 4.8%, +4.6 pts
relative to the benchmark, on 2.1x normal volume". Click the card — detail
view shows since-last-checked price comparison and the confidence tag.

## Step 3 — Prove it doesn't cry wolf
Click into HDFCBANK or another untouched stock in the quiet list — show "no
meaningful change" and that the detail view still works, just without an
alert.

## Step 4 — Volume spike, correctly downgraded
Switch to **Volume spike**. TCS appears under "Worth a look" (not "needs
attention") — small price move, high volume. Narrate: this proves volume
alone is capped and can't fake a high-severity alert
(`test_high_volume_alone_does_not_trigger_needs_attention`).

## Step 5 — Market-wide move, correctly filtered
Switch to **Market crash**. Show that most stocks stay quiet or low-severity
despite a -3.2% benchmark move, because they're moving *with* the market,
not against it — except SBIN, which bucks the trend on volume and is
correctly flagged.

## Step 6 — Resilience: API failure
Switch to **API failure**. The banner appears: "Market data temporarily
unavailable." The app does not crash; all 10 stocks show "unavailable"
rather than fabricated numbers.

## Step 7 — Resilience: stale data
Switch to **Stale data**. Banner changes to a staleness warning; any stock
that would otherwise be "needs attention" is capped to "worth a look" —
show this against the detail view's confidence tag.

## Step 8 — Recovery
Switch back to **Normal market**. Show the banner clears and the app
returns to steady state without a reload.

## Backend-only proof points (optional, for technical judges)
```bash
curl -s localhost:8000/metrics       # request/latency counters
curl -s -X POST localhost:8000/stocks/RELIANCE/acknowledge   # resets baseline
cd backend && python3 -m pytest tests/ -v   # 13 passing engine tests
```
