# Engineering Trade-offs

**Why PostgreSQL (in production), SQLite (in this demo)?**
The schema is written in vendor-neutral SQLAlchemy Core types with no
SQLite-specific features (`backend/app/database.py`), so switching is a
one-line `DATABASE_URL` change. SQLite means a judge can clone the repo and
run it with zero external setup — no Postgres install, no connection
string, no Docker. For real multi-user traffic we'd want Postgres for
proper concurrent-write handling and because the relational model here
(foreign keys, uniqueness constraints doing real work in §11 of
`ARCHITECTURE.md`) is exactly what Postgres is for.

**Why not MongoDB?**
The data is inherently relational — a user has watchlists, a watchlist has
stocks, a stock has one current snapshot and a history of user state. The
uniqueness constraints that make our concurrency story work (§11) are a
natural fit for a relational schema and an awkward fit for a document
store. There's no unstructured or schema-flexible data here that would
justify a document database.

**Why a monolith, not microservices?**
One engineer, one 72-hour window, one bounded problem domain (watchlists +
change detection). Microservices buy you independent deployability and
failure isolation across team boundaries that don't exist here — for this
scope they'd only add network calls, serialization, and more ways to fail,
with no corresponding benefit.

**Why polling, not Kafka?**
There is no continuous high-volume event stream in this problem — market
data for a bounded set of watched symbols, refreshed on an interval, is a
pull problem, not a push problem, until refresh volume genuinely can't be
served by scheduled polling (`ARCHITECTURE.md` §8, Phase 4). Kafka would
add an operational component (brokers, topics, consumer group management)
to solve a scaling problem we don't have yet.

**Why a deterministic rule engine, not an LLM/ML model, for detection?**
Judges (and users) need to be able to ask "why was this flagged?" and get
an answer that's reproducible and falsifiable — `test_engine.py` proves the
same input always gives the same output, and every branch is traceable to
a named signal. An LLM call here would add latency, cost, and
non-determinism to the one piece of the product that most needs to be
trustworthy and explainable, in exchange for no clear product benefit — the
underlying signals (z-scores, ratios) are already well-suited to explicit
rules. A learned model could improve on hand-picked weights eventually, but
would need a labeled dataset of "was this actually meaningful to a user" we
don't have.

**Why not Redis?**
There is no cache-invalidation problem yet: at demo scale (10 stocks, 1
user), computing the score on read is ~5ms and costs nothing. Redis solves
a problem — expensive repeated computation, or an external API you can't
afford to hit per-request at scale — that only exists once there's a
background worker and real traffic (`ARCHITECTURE.md` §8, Phase 2). Adding
it now would be unjustified complexity.

**Why demo mode instead of a live market data API?**
A live feed introduces two problems for judging specifically: it only
produces interesting data during market hours, and it makes the demo's
outcome dependent on an external vendor's uptime and rate limits during the
exact window judges are watching. The `fetch_snapshot()` function is the
single seam where a real vendor integration would plug in — the engine,
schema, and API don't change. Demo data is clearly labelled `source: demo`
and never presented as live.

**Why these three meaningful-change signals, not all ten from the brief?**
See `ARCHITECTURE.md` §6 for the per-signal rationale. The short version:
volatility-adjusted price move, relative performance, and volume anomaly
are cheaply computable from a single snapshot + rolling averages, are each
independently justifiable, and their combination already prevents the two
biggest failure modes (flagging normal volatility as meaningful; flagging
market-wide moves as stock-specific). Adding more signals without more time
to validate their thresholds would risk decorating the score with inputs
we can't actually justify — quantity of signals was never the goal.

**Why this UI, not a traditional stock dashboard?**
A dashboard optimizes for "show everything"; this product's thesis is "show
what changed and protect the user's attention" (README "Key insight"). A
dashboard with 10 equal-weight stock cards and a dozen indicators per card
would directly contradict the product's own argument. The three-bucket
layout (needs attention / worth a look / quiet) is the UI expression of the
attention-prioritization decision in `ARCHITECTURE.md` — it was chosen
because ranking, not exhaustiveness, is the point.

**Why no auth?**
A single demo user (`DEMO_USER_ID = 1`) is sufficient to demonstrate every
architectural decision that matters for judging — persistence, concurrency,
resilience, the engine itself. Real auth (sessions/JWT, password handling,
multi-tenancy) is a well-understood, separate problem that doesn't change
any decision documented here; building it would spend hackathon time
proving something not being judged, at the cost of time on the actual
differentiator.

**What we deliberately left out entirely:** see `ARCHITECTURE.md` §13.
