# Hackathon Scorecard (self-assessment)

| Dimension | Score /10 | Why |
|---|---|---|
| Engineering Depth | 8 | Working end-to-end system, clean layering (pure engine, ORM, API), documented scaling path. Not a 9/10 because there's no real background worker or live vendor integration — those are designed for but not built (see below). |
| Product & Problem Interpretation | 9 | Explicitly reframes "watchlist" from "show information" to "show change", matches the brief's own instruction ("don't build the obvious watchlist") and Groww's public "simple is beautiful" philosophy. |
| Edge Cases & Resilience | 8 | 13 unit tests on the engine, 6 demo scenarios including API failure and stale data, concurrency handled via unique constraints + upsert. Not 9/10 because there's no load-tested behavior under real concurrent write volume. |
| Code Quality & Simplicity | 9 | No frameworks or infra added without a documented reason (`TRADEOFFS.md`); the engine is a pure, tested function; schema has no unused tables. |
| Originality & Thoughtfulness | 8 | "Since you last checked" + volatility-adjusted, benchmark-relative scoring is a genuine reframe, not a bolt-on feature. Ceiling on this score is that the core statistical techniques (movement multiples, relative performance) are well-known finance concepts, not novel ones — the originality is in applying them to attention-management for a watchlist, not in the math itself. |

## Gaps identified and what we did about them

1. **No live market data.** Deliberate, documented trade-off
   (`TRADEOFFS.md`) — a live feed would make the judged demo
   non-deterministic. Mitigated with a clean provider seam
   (`fetch_snapshot()`) so this is a swap, not a redesign.
2. **No background worker.** Fetch-on-read is fine at demo scale; the
   worker design is fully specified in `ARCHITECTURE.md` §8 Phase 2 so the
   next step is a concrete implementation task, not an open question.
3. **Single demo user, no auth.** Explicitly scoped out — see
   `TRADEOFFS.md` "Why no auth" — to spend the 72 hours on the
   differentiator rather than a solved problem.
4. **Only 3 of 10 taxonomy categories implemented.** Deliberate — see
   `ARCHITECTURE.md` §6 table for why each included signal earns its place
   and why the excluded ones would either duplicate an included signal or
   require data we don't have reliable access to in 72 hours.
