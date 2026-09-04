# Judge Q&A Prep

**Why is this better than a normal watchlist?**
A normal watchlist answers "what's the price now?" every time, which forces
the user to re-derive "did anything happen?" themselves. This product
answers that question directly and ranks the answer by how much it deserves
attention, so most visits require zero interpretation work.

**How do you define "meaningful"?**
A weighted combination of how large a move is relative to the stock's own
normal volatility, how it performed relative to the benchmark, and whether
volume corroborates it — not a fixed percentage threshold. Full formula in
README / `ARCHITECTURE.md` §6.

**Why did you choose these thresholds (2.0 / 1.0)?**
They're centralized constants (`engine.py`), not scattered magic numbers,
chosen so that a single-signal move needs to be roughly 2 standard
deviations from normal to alone cross "needs attention", while a
combination of a moderate price move and corroborating volume can also
cross it. They're explicitly tunable — see "what would you build next".

**What happens with volatile stocks?**
The volatility-adjustment (`z_price`) is the whole point: dividing by the
stock's own trailing average daily move means a "normal" 4% day for a
volatile stock doesn't get flagged, while the same 4% would be flagged for
a historically calm stock. Tested directly in `test_engine.py`.

**How do you handle stale data?**
Every reading carries a `freshness` field. Stale data downgrades confidence
to LOW, which caps the verdict below "needs attention" even if the raw
numbers would otherwise qualify — we'd rather under-alert than confidently
alert on data we don't trust.

**What if the market API goes down?**
The app stays open. `fetch_snapshot()` returns `freshness=UNAVAILABLE`
instead of raising; the engine short-circuits to an explicit "unavailable"
verdict; the API returns 200 with `market_data_available: false`; the UI
shows a banner and last-known values. Demonstrated live in the
`api_failure` demo scenario.

**How would this scale to millions of users?**
Move the score computation off the request path into a scheduled
background worker that refreshes shared market data once per interval
(not once per user), then have reads become simple lookups against
already-computed `meaningful_changes` rows; partition the worker's symbol
list as watched-symbol count grows. Full path in `ARCHITECTURE.md` §8 —
we did not build this because it isn't needed to prove the idea at demo
scale, and building it speculatively would be exactly the kind of
unjustified complexity the judging criteria warn against.

**Why PostgreSQL? Why not Kafka? Why not microservices?**
See `TRADEOFFS.md` — short version: the workload is relational, the event
volume is a scheduled-polling problem not a streaming one, and one team in
72 hours on one bounded domain gets nothing from splitting into services.

**How do you prevent duplicate events / signal computations?**
`market_snapshots` and `meaningful_changes` writes are upserts guarded by
unique constraints; a duplicate write (e.g. two concurrent background jobs)
converges rather than creating a duplicate row or crashing.

**How do you handle concurrent updates (two tabs, two devices)?**
Unique constraints on `(watchlist_id, stock_id)` and `(user_id, stock_id)`
make add-stock and acknowledge idempotent; the losing writer in a race gets
a caught `IntegrityError`, not a 500 or duplicate data.

**How does the system know when a user last checked?**
`user_stock_state.last_viewed_at`, updated by the explicit "mark as
reviewed" action, not by a passive page-view — an explicit acknowledgment
is a clearer signal of "I've seen this" than assuming a page load means
the user actually read that row.

**How do you prevent too many alerts?**
The scoring is deliberately conservative — three signals, capped
contributions, thresholds validated against the exact failure modes
(volume-only spikes, market-wide moves) in `test_engine.py` — plus the
UI itself only surfaces "needs attention" and "worth a look" prominently;
everything else collapses into a scannable quiet list rather than
competing for attention.

**How do you avoid this becoming investment advice?**
The product never recommends buying, selling, or holding — output is
strictly "here's what changed, here's why, review before deciding" (see
`engine.py` explanation templates and the in-app disclaimer on every
detail view). This mirrors the brief's explicit instruction and Groww's
public responsible-investing framing.

**What if the data source is wrong?**
Freshness/confidence metadata exists precisely so a bad or delayed read
degrades the verdict rather than propagating false confidence; a
production version would add a plausibility check (e.g. reject a snapshot
implying a >20% single-tick move without a corroborating volume signal) —
noted as a natural next step, not built for the 72-hour scope.

**How would you personalize meaningfulness?**
Per-user threshold overrides (some users want tighter or looser attention
filters) would sit as a multiplier on the existing score, not a redesign of
the engine — deferred because we have no data yet on what personalization
users would actually want, and guessing at it would be speculative
complexity.

**What would you build next?**
A background worker (Phase 2, `ARCHITECTURE.md` §8), a real market data
vendor integration behind the existing `fetch_snapshot()` seam, full sector
divergence based on live sector indices,
and basic auth for multi-tenancy.

**What did you intentionally leave out?**
Kafka, microservices, Kubernetes, Redis, a live feed for the judged demo,
corporate/news event signals, and AI-generated explanations — each with a
documented reason in `TRADEOFFS.md`, not an oversight.

**Why is RELIANCE +4.8% not flagged?**
RELIANCE's average daily move is ~5.2%. A 4.8% move is 0.92× its normal
movement — within its typical range. The engine treats this as noise.

**Why is INFY +2.1% flagged?**
INFY's average daily move is ~0.6%. A 2.1% move is 3.5× its normal
movement, with 3.2× average volume and +2.0 pp outperformance vs NIFTY.
All three signals point in the same direction.

**Why not a flat 5% threshold?**
A flat threshold treats all stocks identically. Our engine normalises each
stock against its own history — a 5% move means something different for
RELIANCE than for INFY.

**What happens when the whole market crashes?**
We detect market-wide movement via `detect_market_regime`. When ≥70% of
watchlist stocks move together with magnitude ≥1×, we classify the regime as
`market_wide` and suppress redundant attention signals. Genuine outliers
still surface.

**Is this z-score based?**
No. We use a movement multiple: `abs(pct_change) / avg_daily_abs_move`.
Interpretable, reproducible, and works on small datasets. A z-score requires
standard deviation over a large return history and assumes normality.

**Why no LLM?**
The significance decision must be deterministic and auditable. An LLM would
add latency, cost, and non-determinism to the component that most needs to
be trustworthy. Every flagged stock traces back to a specific calculation.

**Why no live market data?**
For a judged demo, reproducibility > real-time. A live feed only produces
interesting data during market hours and makes the demo dependent on an
external vendor's uptime. `fetch_snapshot()` in `main.py` is the single seam
where a live provider plugs in — the engine, schema, and API are unchanged.

**Why didn't you build sector context around a real sector index?**
We use a peer-group proxy: stocks in the same sector within your watchlist.
We call it exactly that — a proxy — not a live sector index. When fewer than
2 peers exist, we don't claim sector signal. Honesty about data quality is
a core product principle.
