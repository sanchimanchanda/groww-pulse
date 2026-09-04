# Signal — Market Change Intelligence

**A watchlist that tells you what changed, not what everything costs right now.**

## Problem

Conventional watchlists show the same thing on every visit: a list of prices.
The user does the work of remembering what it looked like last time, deciding
whether a move is normal or unusual, and scanning every row even when nothing
happened to most of them. A 20-stock watchlist checked twice a day is 40 rows
of numbers a user has to re-interpret from scratch, every time.

## Solution

Signal compares the market now to the market as the user last saw it,
scores each stock with a deterministic **Meaningful Change Engine**, and
opens on three buckets: **needs attention**, **worth a look**, **no change**.
Most visits should be quiet. That's the point — the product's job is to
protect the user's attention, not fill it.

## Key insight

> Raw price change is not meaningful change.

A 3% move in a stock that swings 5% a day is noise. A 0.8% move on 3x normal
volume, or a stock that beats a flat benchmark by 4%, is signal. "Meaningful"
has to be relative to the stock's own normal behavior and to the market
around it — not a single global threshold like `abs(change) > 5%`.

## Features

- **Since you last checked** — every stock view is timestamped and snapshot;
  the next visit is compared against it, not against an arbitrary "today".
- **Meaningful Change Engine** — deterministic, explainable, weighted scoring
  across volatility-adjusted price move, relative performance vs. benchmark,
  and volume anomaly. See `ARCHITECTURE.md` for the formula.
- **Attention ranking** — a 50-stock watchlist doesn't render 50 equal cards;
  it renders a short "needs attention" list, a shorter "worth a look" list,
  and folds the rest into a quiet, scannable list.
- **Plain-language explanations** — every flagged stock gets one sentence on
  *why* it was flagged, generated from the same numbers the score used (no
  LLM in this path — see "AI usage" below).
- **Data freshness, always visible** — every reading carries a freshness
  state (`LIVE` / `DELAYED` / `STALE` / `UNAVAILABLE`); stale data is never
  shown as if it were live, and the app stays usable when the feed is down.
- **Demo mode** — six deterministic scenarios (normal market, significant
  move, volume spike, market crash, stale data, API failure) so the product
  can be evaluated without a live market data dependency.

## Architecture

Modular monolith: FastAPI + SQLite (schema is Postgres-compatible), served
alongside a small static frontend from the same process. No queue, no
microservices, no Kafka — see `TRADEOFFS.md` for why, and `ARCHITECTURE.md`
for the full data flow, schema, and scaling path if this needed to be real.

## Meaningful Change Engine

```
z_price    = pct_change / trailing_20d_avg_daily_move
z_relative = (pct_change - benchmark_pct_change) / trailing_20d_avg_daily_move
volume_contribution = min(volume / avg_volume_20d, 4) / 2

score = 0.45*|z_price| + 0.35*|z_relative| + 0.20*volume_contribution

score >= 2.0  -> needs attention
score >= 1.0  -> worth a look
else          -> no meaningful change
```

Confidence (HIGH/MEDIUM/LOW) is derived from data freshness and history
depth, and a LOW-confidence reading can never produce a "needs attention"
verdict — it's capped at "worth a look". Full rationale for each signal and
each excluded signal is in the docstring at the top of `backend/app/engine.py`
and in `ARCHITECTURE.md` §6.

## Reliability & data freshness

Every market reading carries `source`, `freshness`, and timestamps. If the
feed is unavailable, the UI shows a banner and last-known values rather than
crashing or silently showing stale numbers as current. See the `api_failure`
and `stale_data` demo scenarios.

## Edge cases handled

- Two tabs updating the same watchlist / acknowledging the same stock:
  unique constraints + upsert make this idempotent, last-write-wins (correct
  for a read-marker, not a ledger).
- Stock with insufficient price history: volatility estimate is untrusted,
  confidence drops to LOW.
- Zero/near-zero volatility stock: floored denominator, no divide-by-zero.
- Market-wide moves: relative-performance signal specifically prevents "the
  whole market moved" from being reported as "this stock is remarkable".
- Volume spike with a tiny price move: capped so volume alone can't produce
  a false "needs attention".

## Scalability

Phase 1 (this submission): modular monolith, synchronous fetch-on-read.
Phase 2: background worker refreshes `market_snapshots` on a schedule,
API reads become cache reads. Phase 3: partition refresh work by symbol
shard as watchlist count grows. Full detail in `ARCHITECTURE.md` §12.

## Trade-offs

See `TRADEOFFS.md` — including why SQLite over Postgres for this demo, why
no Redis, why polling over Kafka, why a rule engine over an LLM for
detection, and what we deliberately left out.

## AI usage

None in the detection path. The Meaningful Change Engine is a deterministic
rule engine so its output is testable, reproducible, and explainable to a
user in one sentence. An LLM could plausibly help *phrase* an explanation
from an already-computed set of signals, but for a 72-hour submission the
rule-based templating in `engine.py` does that job with zero hallucination
risk, so we didn't add the LLM call. See §34 discussion in `TRADEOFFS.md`.

## Setup

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# open http://127.0.0.1:8000
```

The frontend is plain HTML/CSS/JS served by the same FastAPI process — no
build step, no Node dependency, one command to run the whole product.

## API

See `ARCHITECTURE.md` §5 for the full list. Core ones:

- `GET  /watchlists/{id}/changes` — the main screen: ranked, explained changes
- `POST /stocks/{symbol}/acknowledge` — mark reviewed, resets the baseline
- `POST /demo/scenario` — switch the demo market scenario
- `GET  /health`, `GET  /metrics`

## Testing

```bash
cd backend && python3 -m pytest tests/ -v
```

13 tests on the Meaningful Change Engine covering: stable vs. volatile
stocks, market-wide moves, volume-only spikes, relative underperformance,
stale/unavailable data, missing history, zero volatility, and determinism.

## Future evolution

Sector divergence and breakout/breakdown as distinct signal categories,
a background worker replacing fetch-on-read, corporate action/news signals
once a reliable source is picked, per-user threshold personalization, and
a real auth layer. None of these were needed to prove the core idea in 72
hours — see `TRADEOFFS.md` for why each was deferred rather than rushed in.
# groww-pulse
