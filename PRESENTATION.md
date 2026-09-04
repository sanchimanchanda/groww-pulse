# Presentation (5 minutes)

**0:00–0:30 — Problem**
"Every time an investor opens a watchlist, they see information. A row of
prices they have to re-interpret from scratch. But information isn't
attention — and re-reading the same ten stocks every day, most of which
haven't done anything notable, is how meaningful moves get lost in noise."

**0:30–1:15 — Insight**
"We asked a different question than 'what's the price right now': what has
actually changed since you last checked, and does it deserve your
attention? A 3% move on a stock that swings 5% a day is nothing. A 0.8%
move on 3x normal volume might be something. Raw percentage change doesn't
tell you which is which — so we built something that does."

**1:15–2:00 — Product demo**
Open the watchlist in "normal market" — show it's quiet, ten stocks, no
noise. Switch to "significant move" — RELIANCE surfaces immediately under
"needs attention" with a one-sentence reason. Click through to the detail
view, show the since-last-checked comparison.

**2:00–2:45 — Meaningful Change Engine**
Walk through the three signals on screen: volatility-adjusted price move,
relative performance vs. NIFTY, volume anomaly. Show the "market crash"
scenario: everything drops, but only SBIN (bucking the trend on volume)
gets flagged — proving the system distinguishes stock-specific signal from
market-wide movement.

**2:45–3:30 — Engineering**
Architecture diagram: monolith, pure-function engine, Postgres-compatible
schema, provider seam for a real market data vendor. Point at the 13 tests
covering the engine's edge cases.

**3:30–4:15 — Resilience**
Switch to "api_failure" scenario live — show the app stays open, banners
the outage, shows last-known data with a freshness tag instead of crashing
or lying about live-ness. Switch to "stale_data" — show confidence
downgrades and the verdict caps below "needs attention".

**4:15–4:45 — Trade-offs**
"We didn't build Kafka, microservices, or Kubernetes, and we didn't wire a
live feed for this demo — each of those decisions is written down in
TRADEOFFS.md with the reasoning, not left implicit. Simplicity was a
constraint we optimized for, not a corner we cut."

**4:45–5:00 — Closing**
"We didn't build another watchlist. We built a system whose only job is to
tell you what deserves your attention — and to stay quiet the rest of the
time."
