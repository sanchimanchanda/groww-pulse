# Architecture

## 1. System overview

Groww Pulse is a modular monolith: one FastAPI process serves both the JSON
API and the static frontend. State lives in a single relational database
(SQLite for the demo, schema is Postgres-compatible — see `TRADEOFFS.md`).

```
Browser
   |
FastAPI app (single process)
   |-- static file serving (frontend/)
   |-- REST API
   |     |-- fetch_snapshot()  --> market data provider (demo-backed today,
   |     |                          real vendor API in production)
   |     |-- Meaningful Change Engine (pure function, no I/O)
   |     '-- SQLAlchemy ORM
   '-- SQLite / PostgreSQL
```

There is no queue and no separate worker process in this submission. The
change score is computed synchronously when `/watchlists/{id}/changes` is
called, then persisted. See §8 for how this evolves under real load.

## 2. Component diagram

```
frontend (HTML/CSS/JS)  --fetch-->  FastAPI routes
                                        |
                          +-------------+--------------+
                          |             |               |
                     Stock/Watchlist  Engine.evaluate  MarketSnapshot
                     ORM models        (pure, no I/O)   provider
                          |                                  |
                          +------------> SQLite/Postgres <---+
```

## 3. Data flow ("since you last checked")

1. User opens the watchlist -> `GET /watchlists/{id}/changes`.
2. For each stock: fetch the latest `MarketSnapshot` (from the demo
   provider today; from a vendor API + cache in production).
3. Look up `user_stock_state` for (user, stock) — what the user saw last.
4. Run `engine.evaluate(snapshot)` — a pure function, no DB access — to get
   a verdict, score, confidence, and plain-language explanation.
5. Persist the computed verdict to `meaningful_changes` (for fast aggregate
   queries later) and upsert the latest reading into `market_snapshots`.
6. Sort by verdict priority then score; return three buckets.
7. When the user opens a stock and clicks "mark as reviewed",
   `POST /stocks/{symbol}/acknowledge` overwrites `user_stock_state` with
   the current reading — that becomes the new baseline for next time.

Note step 3 is a *lookup*, not a *scoring input*: how long it's been since
the user looked does not make a move more or less meaningful on its own. It
only determines what we compare against. See `TRADEOFFS.md` for why we
deliberately excluded "time since last viewed" as a score signal.

## 4. Database schema

```
users(id, email, created_at)
watchlists(id, user_id FK, name, created_at)
stocks(id, symbol UNIQUE, name, sector)
watchlist_items(id, watchlist_id FK, stock_id FK, added_at,
                UNIQUE(watchlist_id, stock_id))
market_snapshots(id, stock_id FK UNIQUE, price, prev_close, volume,
                  avg_volume_20d, avg_daily_move_20d, benchmark_pct_change,
                  history_days, freshness, source, market_timestamp,
                  received_at)
user_stock_state(id, user_id FK, stock_id FK, last_viewed_at,
                  last_seen_price, last_seen_volume,
                  last_seen_avg_daily_move_20d, last_seen_benchmark_pct_change,
                  UNIQUE(user_id, stock_id))
meaningful_changes(id, user_id FK, stock_id FK, verdict, score, confidence,
                    directionality, headline, why_it_matters, freshness,
                    computed_at, INDEX(user_id, score))
```

Design choices:
- `market_snapshots` holds the **latest** reading per stock (unique on
  `stock_id`), not a time series. A history table (`market_snapshot_history`)
  is the natural next table if charting is added — deliberately deferred
  (`TRADEOFFS.md`).
- `user_stock_state` is a mutable "last seen" marker with a unique
  constraint on `(user_id, stock_id)`. It is designed to be overwritten,
  not appended to — the past view doesn't matter once acknowledged.
- `meaningful_changes` is append-only and indexed on `(user_id, score)` so
  "top changes for this user" is a simple indexed range query rather than a
  live recomputation, once a background worker exists (§8).

## 5. API design

```
POST   /watchlists                          create a watchlist
GET    /watchlists                          list watchlists
POST   /watchlists/{id}/stocks              add a symbol
DELETE /watchlists/{id}/stocks/{symbol}     remove a symbol
GET    /watchlists/{id}/changes             ranked, explained changes (the main screen)
GET    /stocks/{symbol}                     detail view + since-last-checked
POST   /stocks/{symbol}/acknowledge         mark reviewed, resets baseline
GET    /market/status                       active demo scenario, available scenarios
POST   /demo/scenario                       switch demo scenario
GET    /health
GET    /metrics
```

No auth layer for the hackathon (single demo user, `DEMO_USER_ID = 1`) — a
deliberate scope cut, not an oversight; see `TRADEOFFS.md` §"Why no auth".

## 6. Meaningful Change Engine

Implemented in `backend/app/engine.py` as a pure function
(`MarketSnapshot -> MeaningfulChangeResult`) with no I/O, which is what
makes it unit-testable in isolation from the database and market data
provider. Full signal rationale is in that file's module docstring; formula
is reproduced in `README.md`. Three signals were chosen deliberately out of
the ten-category taxonomy in the brief (§10):

| Signal | Why it's in v1 | Why the others are deferred |
|---|---|---|
| Volatility-adjusted price move | Cheapest, single most informative signal; needs only price + a rolling average | Gap up/down and breakout/breakdown are largely captured by this already at the price level; adding them as separate categories would mostly duplicate this signal for a hackathon-scale dataset |
| Relative performance vs. benchmark | Distinguishes stock-specific news from market-wide moves — directly prevents false positives during a market-wide rally or crash | Sector divergence is the same idea one level down; deferred because we don't have reliable sector index data in the 72h window, and it would mostly restate relative-performance |
| Volume anomaly | Corroborates that a price move reflects real participation, not noise | Deliberately capped and weighted lowest — volume alone is a weak, easily-gamed signal and should never solely justify "needs attention" (see `test_high_volume_alone_does_not_trigger_needs_attention`) |

Excluded entirely from v1: corporate/event/news signal (no reliable free
data source in 72 hours — fabricating one would be worse than omitting it),
market-wide movement as its own category (subsumed by the relative
performance signal, which is the more precise version of the same idea).

## 7. Caching strategy

None in this submission. `/watchlists/{id}/changes` calls the market data
provider directly on each request. For a 10-stock demo watchlist this is
fast enough to not matter (~50ms end to end, measured via `/metrics`).
Real production traffic would need a cache — see §8, Phase 2 — but adding
Redis now, for a single-process demo with a handful of users, would be
complexity with no corresponding benefit (`TRADEOFFS.md`).

## 8. Background processing & scaling strategy

- **Phase 1 (this submission):** synchronous fetch-on-read, monolith,
  SQLite. Correct and simple; doesn't scale past a handful of concurrent
  users hitting a slow upstream API.
- **Phase 2:** a scheduled worker polls the market data vendor for all
  symbols across all watchlists on a fixed interval, writes to
  `market_snapshots`, and computes+persists `meaningful_changes`. API reads
  become simple `SELECT`s against already-computed data — this is the
  single highest-leverage change once there's real traffic, because it
  turns a synchronous, per-request external API call into a background
  job amortized across all users watching the same symbol.
- **Phase 3:** partition the worker's symbol list across multiple workers
  (e.g. by hash of symbol) as the union of all watched symbols grows past
  what one worker can refresh within the desired freshness window.
- **Phase 4:** only if Phase 3's polling cadence can't keep up — move to an
  event-driven ingestion path (e.g. a vendor's push/streaming API feeding a
  queue) rather than polling. We do not believe this hackathon's scope
  justifies building this speculatively; it's a real next step, not a
  Kafka cluster added to look impressive (`TRADEOFFS.md`).

## 9. Failure handling

- Market data provider failure -> `MarketSnapshot(freshness=UNAVAILABLE)`;
  the engine short-circuits to a `Verdict.UNAVAILABLE` result instead of
  attempting a score on missing data; the API still returns 200 with a
  `market_data_available: false` flag; the UI shows a banner and keeps
  running (`api_failure` demo scenario proves this).
- Stale feed (responding but not updating) -> `freshness=STALE`; the engine
  still scores it but downgrades confidence to LOW, which caps the verdict
  at "watch" even if the raw score would say "needs attention" — we would
  rather under-alert on stale data than confidently flag a false signal.
- Unknown symbol / missing watchlist -> explicit 404s, not silent empty
  results.

## 10. Data freshness

Every snapshot carries `freshness` (`LIVE` / `DELAYED` / `STALE` /
`UNAVAILABLE`), `source`, and `received_at`. The frontend always renders
freshness when it's not `LIVE` — never presents a stale or unavailable
reading as if it were current.

## 11. Concurrency

- Adding the same stock to a watchlist from two tabs: unique constraint on
  `(watchlist_id, stock_id)`; the loser of the race gets `IntegrityError`,
  caught and turned into `{"status": "already_present"}` rather than a 500.
- Two tabs acknowledging the same stock near-simultaneously: unique
  constraint on `(user_id, stock_id)` in `user_stock_state`; last write
  wins, which is correct here — there's no meaningful way to "merge" two
  viewing events, and the point of the row is "what did the user most
  recently see", not an audit log.
- Duplicate background refresh writing the same `market_snapshots` row:
  same upsert-with-catch pattern; both writers converge on the DB, and
  since the underlying data being written is the same real-world market
  reading, order doesn't matter.

## 12. Concurrency & scaling limits acknowledged

The `_active_scenario` demo-control global is intentionally
process-local, in-memory state — acceptable for a single-process hackathon
demo, and explicitly called out here rather than presented as
production-ready global config (`TRADEOFFS.md`).

## 13. What we deliberately did NOT build

- **Kafka / event bus** — polling a scheduled worker is sufficient at this
  scale and is far simpler to reason about, test, and demo. See §8, Phase 4.
- **Microservices** — one team, one 72-hour window, one bounded domain.
  Splitting into services here would add network calls and deployment
  surface without adding capability.
- **Kubernetes** — a single process comfortably serves the demo's load; the
  binary is small enough to deploy as one container.
- **Redis** — no cache-invalidation problem to solve yet at demo scale
  (§7). Adding it now would be complexity in search of a justification.
- **A real market data vendor integration** — the fetch/evaluate contract
  (`MarketSnapshot -> MeaningfulChangeResult`) is vendor-agnostic; wiring a
  real API is a swap of `fetch_snapshot()`'s implementation, not a
  redesign. Skipped for the submission because a live feed would make the
  demo non-deterministic and dependent on market hours and an external
  service's uptime during judging.
- **LLM-based explanations** — see README "AI usage".
- **Authentication** — single demo user; a real multi-tenant deployment
  would need it, but it doesn't change any of the architecture decisions
  above, so building it now would be effort spent proving something the
  judging criteria don't ask about.
