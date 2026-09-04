# GROWW CODE 2026 — Smart Market Watchlist
# Implementation Task Roadmap

> **Document version:** 1.0  
> **Date:** 4 September 2026  
> **Status:** Ready for implementation  
> **Source design:** `docs/DESIGN.md`

---

## Table of Contents

1. [Critical MVP Path](#critical-mvp-path)
2. [Recommended Execution Order](#recommended-execution-order)
3. [EPIC 1 — Project Foundation](#epic-1--project-foundation)
4. [EPIC 2 — Backend Foundation](#epic-2--backend-foundation)
5. [EPIC 3 — Database](#epic-3--database)
6. [EPIC 4 — Redis Cache Layer](#epic-4--redis-cache-layer)
7. [EPIC 5 — Watchlist Management](#epic-5--watchlist-management)
8. [EPIC 6 — Instrument Search](#epic-6--instrument-search)
9. [EPIC 7 — Market Data Abstraction](#epic-7--market-data-abstraction)
10. [EPIC 8 — Market Worker](#epic-8--market-worker)
11. [EPIC 9 — Meaningful Change Engine](#epic-9--meaningful-change-engine)
12. [EPIC 10 — Explanation Engine](#epic-10--explanation-engine)
13. [EPIC 11 — Last-Seen State](#epic-11--last-seen-state)
14. [EPIC 12 — Digest API](#epic-12--digest-api)
15. [EPIC 13 — Data Freshness & Stale Handling](#epic-13--data-freshness--stale-handling)
16. [EPIC 14 — Authentication](#epic-14--authentication)
17. [EPIC 15 — Observability](#epic-15--observability)
18. [EPIC 16 — Demo Mode](#epic-16--demo-mode)
19. [EPIC 17 — Frontend Foundation](#epic-17--frontend-foundation)
20. [EPIC 18 — Watchlist UX](#epic-18--watchlist-ux)
21. [EPIC 19 — Digest UX](#epic-19--digest-ux)
22. [EPIC 20 — Stock Detail UX](#epic-20--stock-detail-ux)
23. [EPIC 21 — Error / Loading / Empty / Stale States](#epic-21--error--loading--empty--stale-states)
24. [EPIC 22 — Frontend ↔ Backend Integration](#epic-22--frontend--backend-integration)
25. [EPIC 23 — Testing](#epic-23--testing)
26. [EPIC 24 — Security](#epic-24--security)
27. [EPIC 25 — Final QA](#epic-25--final-qa)

---

## Critical MVP Path

The minimum sequence to demonstrate the core user journey end-to-end:

```
User opens app → Creates watchlist → Adds stocks → Market data exists →
User leaves → Market changes → User returns → System detects meaningful changes →
System ranks what deserves attention → User sees why → User can inspect stock details
```

**P0 Critical Path Tasks (in order):**

```
TASK-001 → TASK-002 → TASK-003 → TASK-004 → TASK-010 → TASK-011 →
TASK-012 → TASK-020 → TASK-021 → TASK-022 → TASK-023 → TASK-024 →
TASK-025 → TASK-026 → TASK-027 → TASK-028 → TASK-029 → TASK-031 →
TASK-040 → TASK-050 → TASK-051 → TASK-052 → TASK-054 → TASK-055 →
TASK-056 → TASK-060 → TASK-061 → TASK-070 → TASK-071 → TASK-074 →
TASK-080 → TASK-081 → TASK-083 → TASK-084 → TASK-085 → TASK-090 →
TASK-091 → TASK-092 → TASK-093 → TASK-094 → TASK-095 → TASK-096 →
TASK-097 → TASK-098 → TASK-099 → TASK-100 → TASK-110 → TASK-111 →
TASK-112 → TASK-113 → TASK-114 → TASK-115 → TASK-116 → TASK-120 →
TASK-121 → TASK-122 → TASK-124 → TASK-130 → TASK-131 → TASK-132 →
TASK-133 → TASK-134 → TASK-135 → TASK-136 → TASK-137 → TASK-140 →
TASK-141 → TASK-150 → TASK-200 → TASK-201 → TASK-202 → TASK-204 →
TASK-205 → TASK-206 → TASK-210 → TASK-213 → TASK-214 → TASK-215 →
TASK-220 → TASK-221 → TASK-222 → TASK-223 → TASK-224 → TASK-240 →
TASK-241 → TASK-243 → TASK-250 → TASK-251 → TASK-252 → TASK-253 →
TASK-254 → TASK-170 → TASK-171 → TASK-172 → TASK-173 → TASK-174
```

---

## Recommended Execution Order

| Phase | Epics | Goal |
|---|---|---|
| **Phase 1: Foundation** | 1, 2, 3, 4, 14 | Runnable project with DB, auth, health check |
| **Phase 2: Watchlist Core** | 5, 6 | Users can create watchlists and add stocks |
| **Phase 3: Market Pipeline** | 7, 8 | Market data flowing into DB and cache |
| **Phase 4: Intelligence** | 9, 10, 11 | MCS computed, explanations generated, last-seen tracked |
| **Phase 5: APIs** | 12, 13 | Digest API working end-to-end |
| **Phase 6: Frontend** | 17, 18, 19, 20, 21, 22 | Frontend connected to all APIs |
| **Phase 7: Demo** | 16 | Deterministic demo scenarios ready |
| **Phase 8: Quality** | 23, 24, 15 | Testing, security, observability |
| **Phase 9: Polish** | 25 | Final QA, README, performance verify |

---

## EPIC 1 — Project Foundation

---

### TASK-001

**Title:** Initialize monorepo project structure  
**Epic:** Project Foundation  
**Priority:** P0  

**Description:**  
Create the top-level monorepo directory layout for backend, frontend, worker, and shared packages. Establish the project skeleton that all subsequent tasks build into.

**Dependencies:** None

**Files likely affected:**
```
/
├── backend/
├── worker/
├── frontend/
├── shared/
├── docker-compose.yml        (placeholder)
├── .gitignore
├── README.md
└── package.json              (root workspace)
```

**Implementation notes:**
- Use npm workspaces (or pnpm workspaces) to link `backend`, `worker`, `frontend`, `shared` as packages.
- The `shared` package will contain TypeScript types and interfaces that are used across backend and worker.
- `.gitignore` must exclude: `node_modules`, `.env`, `*.local`, `dist/`, `build/`.

**Acceptance criteria:**
- Running `npm install` at root installs all workspace packages.
- Folder structure is created and committed.
- `.gitignore` is complete.

**Testing:**
- `ls` the directory structure to verify.
- `npm install` exits 0.

---

### TASK-002

**Title:** Environment variable strategy and `.env.example`  
**Epic:** Project Foundation  
**Priority:** P0  

**Description:**  
Define the full set of environment variables required by backend, worker, and frontend. Create `.env.example` files for each package. Document how secrets are handled (never committed, loaded via `.env` locally, secrets manager in production).

**Dependencies:** TASK-001

**Files likely affected:**
```
backend/.env.example
worker/.env.example
frontend/.env.example
docs/ENV_VARS.md
```

**Implementation notes:**
- Backend variables: `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET` (RS256 private key path), `JWT_PUBLIC_KEY_PATH`, `PORT`, `NODE_ENV`, `CORS_ORIGIN`, `API_RATE_LIMIT_RPM`
- Worker variables: `DATABASE_URL`, `REDIS_URL`, `MARKET_DATA_PROVIDER`, `MARKET_DATA_API_KEY`, `DEMO_MODE`, `OUTLIER_FILTER_MAX_PCT`
- Frontend variables: `VITE_API_BASE_URL`
- Signal config (can be env or config file): `MCS_WEIGHT_VAPM`, `MCS_WEIGHT_SRM`, `MCS_WEIGHT_VA`, `VAPM_FLOOR`, `SRM_FLOOR`, `VA_FLOOR`
- Never hardcode secrets in source; use `.env.example` as documentation, `.env` as actual values (gitignored).

**Acceptance criteria:**
- Each package has a `.env.example` with all required variables and comments.
- `docs/ENV_VARS.md` explains each variable's purpose, type, and default.
- `.gitignore` excludes `.env`.

**Testing:**
- Code review of `.env.example` for completeness.

---

### TASK-003

**Title:** Docker Compose scaffold for local development  
**Epic:** Project Foundation  
**Priority:** P0  

**Description:**  
Create a `docker-compose.yml` that spins up PostgreSQL 16, Redis 7, and PgBouncer for local development. Does not yet include application containers.

**Dependencies:** TASK-002

**Files likely affected:**
```
docker-compose.yml
docker/postgres/init.sql
docker/pgbouncer/pgbouncer.ini
docker/pgbouncer/userlist.txt
```

**Implementation notes:**
- PostgreSQL: port 5432, volume-mounted for persistence, initialized with `init.sql` (creates `groww` database).
- Redis 7: port 6379, no auth for local dev.
- PgBouncer: port 6432, `pool_mode=transaction`, connects to PostgreSQL.
- Health checks on all containers.
- Use named volumes, not host bind mounts, for DB data.

**Acceptance criteria:**
- `docker-compose up -d` starts all three services without errors.
- `psql -h localhost -p 6432 -U postgres groww` connects via PgBouncer.
- `redis-cli ping` returns `PONG`.

**Testing:**
- Manual `docker-compose up` and connection verification.

---

### TASK-004

**Title:** Shared TypeScript configuration and linting  
**Epic:** Project Foundation  
**Priority:** P0  

**Description:**  
Set up a shared `tsconfig.base.json` and ESLint configuration that all packages extend. Establish consistent TypeScript strict mode settings across the codebase.

**Dependencies:** TASK-001

**Files likely affected:**
```
tsconfig.base.json
.eslintrc.base.js
.prettierrc
backend/tsconfig.json
worker/tsconfig.json
frontend/tsconfig.json
shared/tsconfig.json
```

**Implementation notes:**
- `tsconfig.base.json`: `"strict": true`, `"target": "ES2022"`, `"module": "NodeNext"`, `"moduleResolution": "NodeNext"`.
- ESLint: `@typescript-eslint/recommended`, `import` plugin for circular dependency detection.
- Prettier: 2-space indent, single quotes, trailing commas.
- Add `lint` and `typecheck` scripts to each package's `package.json`.

**Acceptance criteria:**
- `npm run typecheck` passes with zero errors in each package.
- `npm run lint` passes with zero errors in each package.

**Testing:**
- Run `npm run lint` and `npm run typecheck` from root.

---

## EPIC 2 — Backend Foundation

---

### TASK-010

**Title:** Initialize Fastify API backend project  
**Epic:** Backend Foundation  
**Priority:** P0  

**Description:**  
Bootstrap the `backend` Node.js package with Fastify, TypeScript compilation, and a minimal entry point. The server should start and respond to a root request.

**Dependencies:** TASK-004

**Files likely affected:**
```
backend/package.json
backend/src/index.ts
backend/src/app.ts
backend/tsconfig.json
```

**Implementation notes:**
- Install: `fastify`, `@fastify/sensible`, `@fastify/cors`, `@fastify/jwt`, `@fastify/rate-limit`, `fastify-plugin`, `pino`, `typescript`, `ts-node`, `tsx`.
- `app.ts` exports a Fastify instance factory; `index.ts` starts it.
- Use `tsx` for development (`npm run dev`), compile to `dist/` for production.
- `NODE_ENV=production` should not use source maps.

**Acceptance criteria:**
- `npm run dev` starts the server at `http://localhost:3000`.
- `GET /` returns `200 OK`.
- TypeScript compiles without errors.

**Testing:**
- `curl http://localhost:3000/` returns 200.

---

### TASK-011

**Title:** Fastify plugin architecture setup  
**Epic:** Backend Foundation  
**Priority:** P0  

**Description:**  
Organize the Fastify application into a plugin-based architecture. Register core plugins, and establish the route prefix structure (`/v1/`). Create the basic plugin registration order.

**Dependencies:** TASK-010

**Files likely affected:**
```
backend/src/app.ts
backend/src/plugins/
backend/src/routes/
```

**Implementation notes:**
- Plugin registration order: sensible → cors → jwt → rate-limit → logging → routes.
- All API routes mounted under `/v1/`.
- Each epic (watchlist, digest, instruments) gets its own Fastify plugin file in `src/routes/`.
- Use `fastify-plugin` to decorate the Fastify instance with shared services (DB client, Redis client).

**Acceptance criteria:**
- `GET /v1/health` returns `{"status": "ok"}`.
- Plugin registration does not throw at startup.
- Route structure is clear and extensible.

**Testing:**
- `curl /v1/health` returns `{"status": "ok"}`.

---

### TASK-012

**Title:** JWT authentication middleware  
**Epic:** Backend Foundation  
**Priority:** P0  

**Description:**  
Implement `@fastify/jwt` plugin with RS256 key pair. Create a `preHandler` hook that validates the `Authorization: Bearer <jwt>` header on all protected routes. Extract and attach `user_id` to the request context.

**Dependencies:** TASK-011

**Files likely affected:**
```
backend/src/plugins/auth.ts
backend/src/hooks/requireAuth.ts
backend/src/types/fastify.d.ts    (type augmentation)
keys/                             (gitignored, generated locally)
```

**Implementation notes:**
- Use RS256 (asymmetric) — private key for signing (worker/auth service), public key for verification (API).
- `fastify.authenticate` decorator wraps `request.jwtVerify()`.
- On failure: return RFC-7807 401 with `type: .../unauthorized`.
- `request.user.userId` typed via Fastify type augmentation.
- Generate a test RSA key pair using `openssl` for local dev.

**Acceptance criteria:**
- Requests without a valid JWT to protected routes return 401.
- Valid JWTs allow access; `request.user.userId` is correctly populated.
- Expired JWTs return 401.

**Testing:**
- Unit test: valid/invalid/expired token scenarios.
- Integration test: protected route rejects/accepts correctly.

---

### TASK-013

**Title:** Health endpoint  
**Epic:** Backend Foundation  
**Priority:** P0  

**Description:**  
Implement `GET /v1/health` returning service liveness status. The endpoint must be unauthenticated (for load balancer health checks). Optionally includes DB and Redis connectivity checks.

**Dependencies:** TASK-011

**Files likely affected:**
```
backend/src/routes/health.ts
```

**Implementation notes:**
- Basic: `{"status": "ok", "timestamp": "2026-09-04T..."}`.
- Extended (when DB/Redis are initialized): include `{"db": "ok", "redis": "ok"}`.
- Return 503 if any dependency is unhealthy (for load balancer auto-removal).
- This endpoint is NOT behind auth middleware.

**Acceptance criteria:**
- Returns 200 with `{"status": "ok"}` when healthy.
- Returns 503 if DB is unreachable.

**Testing:**
- `curl /v1/health` returns 200.
- Bring DB down: verify 503.

---

### TASK-014

**Title:** RFC-7807 error handler  
**Epic:** Backend Foundation  
**Priority:** P0  

**Description:**  
Implement a global Fastify error handler that formats all errors as RFC-7807 Problem Details JSON. Map common error types (Zod validation failure, not found, unauthorized, forbidden, internal) to their correct HTTP status codes and `type` URIs.

**Dependencies:** TASK-011

**Files likely affected:**
```
backend/src/plugins/errorHandler.ts
backend/src/errors/AppError.ts
backend/src/errors/errorTypes.ts
```

**Implementation notes:**
- `AppError` is a typed base class: `{ type, title, status, detail }`.
- Standard types: `watchlist-not-found`, `unauthorized`, `forbidden`, `duplicate-instrument`, `watchlist-limit-exceeded`, `instrument-not-found`, `validation-error`.
- All errors include `trace_id` from the request context.
- Never leak stack traces in production (`NODE_ENV=production`).

**Acceptance criteria:**
- All API errors return valid RFC-7807 JSON.
- 404s have a descriptive `detail` message.
- 500s in production do not include stack traces.

**Testing:**
- Unit: each error type returns correct status and body shape.
- Integration: trigger a 404 and verify shape.

---

### TASK-015

**Title:** API rate limiting plugin  
**Epic:** Backend Foundation  
**Priority:** P1  

**Description:**  
Configure `@fastify/rate-limit` to enforce 100 requests/minute per user on general API routes, and 20 requests/minute per user on the instrument search endpoint.

**Dependencies:** TASK-011

**Files likely affected:**
```
backend/src/plugins/rateLimiter.ts
backend/src/routes/instruments.ts  (search-specific limit)
```

**Implementation notes:**
- Key function: `user_id` from JWT for authenticated routes; IP for unauthenticated routes.
- Use Redis as the rate limit store (distributed, survives restarts).
- Return 429 with RFC-7807 body and `Retry-After` header.
- Configurable via env: `API_RATE_LIMIT_RPM` (default 100), `SEARCH_RATE_LIMIT_RPM` (default 20).

**Acceptance criteria:**
- Exceeding the rate limit returns 429 with `Retry-After` header.
- Rate limit is per-user (not per-IP) for authenticated routes.
- Limits are configurable via environment variables.

**Testing:**
- Send 101 requests in a minute; verify 101st returns 429.
- Verify `Retry-After` header is present.

---

### TASK-016

**Title:** CORS configuration  
**Epic:** Backend Foundation  
**Priority:** P0  

**Description:**  
Configure `@fastify/cors` to allow requests from the frontend origin(s). Restrict allowed methods and headers appropriately.

**Dependencies:** TASK-011

**Files likely affected:**
```
backend/src/plugins/cors.ts
```

**Implementation notes:**
- Allowed origin: `CORS_ORIGIN` env variable (e.g., `http://localhost:5173` for local dev, production domain for prod).
- Allowed methods: `GET, POST, DELETE, PATCH, OPTIONS`.
- Allowed headers: `Content-Type, Authorization`.
- Credentials: `true` (for JWT in Authorization header).

**Acceptance criteria:**
- Frontend dev server origin is allowed.
- Unknown origins are rejected (no `Access-Control-Allow-Origin` header).
- OPTIONS preflight returns 204.

**Testing:**
- `curl -H "Origin: http://evil.com" /v1/health` has no CORS header.
- `curl -H "Origin: http://localhost:5173" /v1/health` has correct CORS header.

---

### TASK-017

**Title:** Request/response logging middleware  
**Epic:** Backend Foundation  
**Priority:** P0  

**Description:**  
Configure Pino structured logging for every request and response. Each log line must include: `timestamp`, `trace_id`, `user_id` (if authenticated), `method`, `url`, `status_code`, `duration_ms`.

**Dependencies:** TASK-011

**Files likely affected:**
```
backend/src/plugins/logging.ts
backend/src/hooks/traceId.ts
```

**Implementation notes:**
- Generate a UUID `trace_id` for each request; store on `request.traceId`.
- Include `trace_id` in all error responses.
- Pino's `redact` option: mask any field named `password`, `token`, `authorization`.
- Log level: `info` in production, `debug` in development.
- Pino transports: `pino-pretty` for dev, raw JSON for prod (piped to log aggregator).

**Acceptance criteria:**
- Every request produces a structured JSON log line.
- `trace_id`, `user_id`, `duration_ms` are present in each log line.
- Sensitive fields are redacted.

**Testing:**
- Make a request; check log output includes all required fields.

---

## EPIC 3 — Database

---

### TASK-020

**Title:** PostgreSQL connection configuration and PgBouncer wiring  
**Epic:** Database  
**Priority:** P0  

**Description:**  
Configure the `pg` (or `postgres.js`) database client in the backend, connecting via PgBouncer at `DATABASE_URL`. Create a Fastify plugin that decorates the instance with `fastify.db`. Handle connection pool errors gracefully.

**Dependencies:** TASK-003, TASK-011

**Files likely affected:**
```
backend/src/plugins/database.ts
backend/src/db/client.ts
```

**Implementation notes:**
- Use `postgres` (postgres.js) or `pg` with connection string from `DATABASE_URL` env.
- Pool max connections: configurable via `DB_POOL_MAX` (default 20).
- On connection error at startup: log and exit with code 1 (don't start the server with no DB).
- The `fastify.db` decorator is typed.

**Acceptance criteria:**
- Server starts successfully when DB is reachable.
- Server exits with a clear error message if DB is unreachable at startup.
- `fastify.db.query(...)` works from route handlers.

**Testing:**
- Start server with DB up: success.
- Start server with DB down: clean exit with error log.

---

### TASK-021

**Title:** Migration tooling setup  
**Epic:** Database  
**Priority:** P0  

**Description:**  
Configure a database migration tool (`node-pg-migrate` or `Flyway`) to manage schema versions. Create the migrations directory and first baseline migration.

**Dependencies:** TASK-020

**Files likely affected:**
```
backend/migrations/
backend/package.json         (migrate scripts)
```

**Implementation notes:**
- Use `node-pg-migrate`: simple, JS-native, no JVM dependency.
- Scripts: `npm run db:migrate`, `npm run db:migrate:rollback`, `npm run db:migrate:status`.
- All migrations are timestamped and committed to source control.
- Never write raw SQL in application code for schema changes — always migrations.

**Acceptance criteria:**
- `npm run db:migrate` runs successfully with zero errors on a fresh DB.
- Running it twice is idempotent.
- `npm run db:migrate:status` shows migration history.

**Testing:**
- Run migrate from scratch; verify all migrations applied.
- Run again; verify idempotent.

---

### TASK-022

**Title:** Create users table migration  
**Epic:** Database  
**Priority:** P0  

**Description:**  
Write the migration that creates the `users` table as defined in DESIGN.md §25.

**Dependencies:** TASK-021

**Files likely affected:**
```
backend/migrations/001_create_users.ts
```

**Implementation notes:**
```sql
CREATE TABLE users (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email       TEXT NOT NULL UNIQUE,
  name        TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_users_email ON users(email);
```
- Include a `down` function for rollback.
- `password_hash` is bcrypt-hashed; never store plaintext.

**Acceptance criteria:**
- Migration runs cleanly.
- `\d users` shows correct schema.
- Rollback removes the table.

**Testing:**
- Run migration up and down; verify schema.

---

### TASK-023

**Title:** Create instruments table migration  
**Epic:** Database  
**Priority:** P0  

**Description:**  
Write the migration for the `instruments` table, which is the reference table for all tradable securities.

**Dependencies:** TASK-021

**Files likely affected:**
```
backend/migrations/002_create_instruments.ts
```

**Implementation notes:**
```sql
CREATE TABLE instruments (
  symbol      TEXT PRIMARY KEY,        -- e.g. "HDFCBANK"
  name        TEXT NOT NULL,
  exchange    TEXT NOT NULL,           -- NSE | BSE
  sector      TEXT NOT NULL,
  status      TEXT NOT NULL DEFAULT 'ACTIVE',  -- ACTIVE | SUSPENDED | DELISTED
  listed_at   TIMESTAMPTZ,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_instruments_sector ON instruments(sector);
CREATE INDEX idx_instruments_name_trgm ON instruments USING gin(name gin_trgm_ops);
```
- Enable `pg_trgm` extension for fuzzy name search.
- `status` enum: `ACTIVE`, `SUSPENDED`, `DELISTED`.

**Acceptance criteria:**
- Migration runs and is rollback-safe.
- `pg_trgm` extension is enabled.

**Testing:**
- Run migration; verify `pg_trgm` is available.

---

### TASK-024

**Title:** Create watchlists and watchlist_instruments migrations  
**Epic:** Database  
**Priority:** P0  

**Description:**  
Write the migrations for `watchlists` and `watchlist_instruments` tables as defined in DESIGN.md §25.

**Dependencies:** TASK-022, TASK-023

**Files likely affected:**
```
backend/migrations/003_create_watchlists.ts
backend/migrations/004_create_watchlist_instruments.ts
```

**Implementation notes:**
```sql
-- watchlists
CREATE TABLE watchlists (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name          TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 64),
  display_order INT NOT NULL DEFAULT 0,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_watchlists_user_id ON watchlists(user_id);

-- watchlist_instruments
CREATE TABLE watchlist_instruments (
  watchlist_id       UUID NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
  instrument_symbol  TEXT NOT NULL REFERENCES instruments(symbol),
  display_order      INT NOT NULL DEFAULT 0,
  added_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (watchlist_id, instrument_symbol)
);
CREATE INDEX idx_watchlist_instruments_watchlist_id ON watchlist_instruments(watchlist_id);
```
- Composite PK on `watchlist_instruments` naturally prevents duplicates.
- `ON DELETE CASCADE` removes instruments when watchlist is deleted.

**Acceptance criteria:**
- Both tables created with correct constraints.
- Inserting duplicate (watchlist_id, instrument_symbol) raises a constraint violation.
- Deleting a watchlist cascades to its instruments.

**Testing:**
- Duplicate insert test; cascade delete test.

---

### TASK-025

**Title:** Create user_watchlist_sessions migration  
**Epic:** Database  
**Priority:** P0  

**Description:**  
Write the migration for the `user_watchlist_sessions` table that stores the per-(user, watchlist) `last_checked_at` state.

**Dependencies:** TASK-022, TASK-024

**Files likely affected:**
```
backend/migrations/005_create_user_watchlist_sessions.ts
```

**Implementation notes:**
```sql
CREATE TABLE user_watchlist_sessions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  watchlist_id    UUID NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
  last_checked_at TIMESTAMPTZ,   -- NULL = NEVER_CHECKED
  device_id       TEXT,
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX idx_sessions_user_watchlist
  ON user_watchlist_sessions(user_id, watchlist_id);
```
- `last_checked_at` is NULL for NEVER_CHECKED state.
- UNIQUE index ensures one session row per (user, watchlist) pair.

**Acceptance criteria:**
- Attempting to insert a duplicate (user_id, watchlist_id) raises a unique constraint error.
- `last_checked_at` is nullable.

**Testing:**
- Duplicate session insert test.

---

### TASK-026

**Title:** Create price_snapshots migration with range partitioning  
**Epic:** Database  
**Priority:** P0  

**Description:**  
Write the migration for the `price_snapshots` table with PostgreSQL declarative range partitioning by `snapshot_at` (monthly partitions). Create the current month's partition.

**Dependencies:** TASK-022, TASK-023

**Files likely affected:**
```
backend/migrations/006_create_price_snapshots.ts
```

**Implementation notes:**
```sql
CREATE TABLE price_snapshots (
  id                  BIGSERIAL,
  instrument_symbol   TEXT NOT NULL REFERENCES instruments(symbol),
  cycle_id            INT NOT NULL,
  price               NUMERIC(12,4) NOT NULL,
  day_change_abs      NUMERIC(12,4),
  day_change_pct      NUMERIC(8,4),
  volume              BIGINT,
  high_52w            NUMERIC(12,4),
  low_52w             NUMERIC(12,4),
  atr_14              NUMERIC(8,4),     -- ATR(14) as % of price
  avg_volume_20d      BIGINT,
  snapshot_at         TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (id, snapshot_at)
) PARTITION BY RANGE (snapshot_at);

-- Sep 2026 partition
CREATE TABLE price_snapshots_2026_09
  PARTITION OF price_snapshots
  FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');
```
- `INSERT ... ON CONFLICT (instrument_symbol, cycle_id) DO NOTHING` requires a unique constraint.
- Add: `CREATE UNIQUE INDEX ON price_snapshots(instrument_symbol, cycle_id)`.

**Acceptance criteria:**
- Table created with partitioning.
- Current month partition exists.
- Unique constraint on (instrument_symbol, cycle_id).

**Testing:**
- Insert snapshot; verify it lands in the correct partition.
- Duplicate cycle_id insert returns DO NOTHING (no error).

---

### TASK-027

**Title:** Create sector_snapshots migration  
**Epic:** Database  
**Priority:** P0  

**Description:**  
Write the migration for the `sector_snapshots` table that stores per-sector index performance per cycle.

**Dependencies:** TASK-026

**Files likely affected:**
```
backend/migrations/007_create_sector_snapshots.ts
```

**Implementation notes:**
```sql
CREATE TABLE sector_snapshots (
  id          BIGSERIAL PRIMARY KEY,
  sector      TEXT NOT NULL,
  cycle_id    INT NOT NULL,
  change_pct  NUMERIC(8,4) NOT NULL,
  snapshot_at TIMESTAMPTZ NOT NULL,
  UNIQUE(sector, cycle_id)
);
CREATE INDEX idx_sector_snapshots_sector_cycle
  ON sector_snapshots(sector, cycle_id DESC);
```
- Track all 12 sector indices listed in DESIGN.md §17 plus Nifty 50.

**Acceptance criteria:**
- Table created with correct schema.
- UNIQUE constraint on (sector, cycle_id).

**Testing:**
- Insert duplicate (sector, cycle_id); verify constraint fires.

---

### TASK-028

**Title:** Create change_events migration with range partitioning  
**Epic:** Database  
**Priority:** P0  

**Description:**  
Write the migration for the `change_events` table, partitioned by `computed_at` (monthly).

**Dependencies:** TASK-026

**Files likely affected:**
```
backend/migrations/008_create_change_events.ts
```

**Implementation notes:**
```sql
CREATE TABLE change_events (
  id                  BIGSERIAL,
  instrument_symbol   TEXT NOT NULL REFERENCES instruments(symbol),
  cycle_id            INT NOT NULL,
  vapm                NUMERIC(8,4),
  srm                 NUMERIC(8,4),
  va                  NUMERIC(8,4),
  mcs                 NUMERIC(8,4) NOT NULL,
  explanation_template TEXT,
  explanation_params  JSONB,
  computed_at         TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (id, computed_at)
) PARTITION BY RANGE (computed_at);

CREATE TABLE change_events_2026_09
  PARTITION OF change_events
  FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');

CREATE UNIQUE INDEX ON change_events(instrument_symbol, cycle_id);
```

**Acceptance criteria:**
- Table created with partitioning.
- UNIQUE constraint on (instrument_symbol, cycle_id).
- `explanation_params` is JSONB.

**Testing:**
- Insert event; verify partition routing.

---

### TASK-029

**Title:** Create all production DB indexes  
**Epic:** Database  
**Priority:** P0  

**Description:**  
Write a migration that creates all secondary indexes defined in DESIGN.md §25. These are the indexes that make the critical read paths fast.

**Dependencies:** TASK-028

**Files likely affected:**
```
backend/migrations/009_create_indexes.ts
```

**Implementation notes:**
All indexes from DESIGN.md:
```sql
CREATE INDEX idx_price_snapshots_symbol_cycle
  ON price_snapshots(instrument_symbol, cycle_id DESC);

CREATE INDEX idx_change_events_symbol_cycle
  ON change_events(instrument_symbol, cycle_id DESC);

CREATE UNIQUE INDEX idx_sessions_user_watchlist
  ON user_watchlist_sessions(user_id, watchlist_id);
```
(Others defined in their respective table migrations.)

**Acceptance criteria:**
- All indexes created without error.
- `EXPLAIN ANALYZE` on the watchlist detail query shows index scan, not seq scan.

**Testing:**
- Run `EXPLAIN ANALYZE` on critical queries; verify index usage.

---

### TASK-030

**Title:** PostgreSQL Row-Level Security (RLS) policies  
**Epic:** Database  
**Priority:** P1  

**Description:**  
Enable RLS on `watchlists`, `watchlist_instruments`, and `user_watchlist_sessions` tables. Define policies that restrict read/write access to rows belonging to the authenticated user.

**Dependencies:** TASK-029

**Files likely affected:**
```
backend/migrations/010_rls_policies.ts
```

**Implementation notes:**
- The application connects as a DB role (not superuser).
- Set `app.current_user_id` via `SET LOCAL` before each query transaction.
- RLS policy example:
  ```sql
  ALTER TABLE watchlists ENABLE ROW LEVEL SECURITY;
  CREATE POLICY user_isolation ON watchlists
    USING (user_id = current_setting('app.current_user_id')::UUID);
  ```
- This is defence-in-depth; the API layer also enforces user isolation.

**Acceptance criteria:**
- A DB query as User A cannot see User B's watchlists even without the API layer.
- RLS policies do not break normal application queries.

**Testing:**
- Unit test: attempt to read another user's watchlist via raw DB query; verify zero rows returned.

---

### TASK-031

**Title:** Seed instruments reference data  
**Epic:** Database  
**Priority:** P0  

**Description:**  
Create a seed script that populates the `instruments` table with a representative set of NSE equities (at minimum 50 instruments covering all 12 sectors, plus sector index instruments). This is required for demo mode and local development.

**Dependencies:** TASK-023

**Files likely affected:**
```
backend/seeds/instruments.ts
backend/data/instruments.json
```

**Implementation notes:**
- Source: NSE publicly available instrument list or a curated static JSON.
- Must include at least 5 instruments per major sector (IT, Banking, FMCG, Auto, Pharma, Metal).
- Must include sector index symbols: `NIFTYBANK`, `NIFTYIT`, `NIFTYFMCG`, `NIFTYAUTO`, `NIFTYPHARMA`, `NIFTYMETAL`, `NIFTYREALTY`, `NIFTYENERGY`, `NIFTYFINSERV`, `NIFTYMEDIA`, `NIFTYCD`, `NIFTY50`.
- Script is idempotent: `INSERT ... ON CONFLICT (symbol) DO UPDATE`.

**Acceptance criteria:**
- Running the seed script twice does not error.
- At least 50 instruments are present after seeding.
- All 12 sector index symbols are present.
- Each instrument has a non-null sector.

**Testing:**
- Run seed; query `SELECT COUNT(*) FROM instruments`; verify >= 50.
- Query each sector index symbol; verify present.

---

## EPIC 4 — Redis Cache Layer

---

### TASK-040

**Title:** Redis connection and namespace conventions  
**Epic:** Redis Cache Layer  
**Priority:** P0  

**Description:**  
Configure the Redis client (`ioredis`) in both the backend and worker. Establish a Fastify plugin that decorates the instance with `fastify.redis`. Define the key namespace conventions used across the system.

**Dependencies:** TASK-003, TASK-011

**Files likely affected:**
```
backend/src/plugins/redis.ts
backend/src/db/redisClient.ts
worker/src/db/redisClient.ts
shared/src/redis/keySchema.ts
```

**Implementation notes:**
- Use `ioredis` with `REDIS_URL` env.
- Key namespaces:
  - `price:{symbol}` → latest PriceSnapshot JSON (string, TTL: 120s)
  - `mcs:{symbol}` → latest MCS + signals JSON (string, TTL: 120s)
  - `session:{userId}:{watchlistId}` → last_checked_at (string, no TTL — persisted to PG)
- Key TTL strategy: set TTL on write; if market data pipeline stops, keys naturally expire → stale detection.
- Publish key namespace to `shared/src/redis/keySchema.ts` so both backend and worker use the same strings.

**Acceptance criteria:**
- Backend connects to Redis at startup; logs success.
- `fastify.redis.get(...)` works from route handlers.
- `shared/src/redis/keySchema.ts` exports typed key builder functions.

**Testing:**
- `redis-cli ping` returns PONG.
- Write and read a test key via the plugin.

---

### TASK-041

**Title:** Redis key schema documentation  
**Epic:** Redis Cache Layer  
**Priority:** P1  

**Description:**  
Document the full Redis key schema in `docs/REDIS_SCHEMA.md`. Include key pattern, data shape, TTL, and which component writes/reads each key.

**Dependencies:** TASK-040

**Files likely affected:**
```
docs/REDIS_SCHEMA.md
```

**Implementation notes:**
| Key Pattern | Value Type | TTL | Writer | Readers |
|---|---|---|---|---|
| `price:{symbol}` | JSON string | 120s | MarketWorker | DigestService, WatchlistService |
| `mcs:{symbol}` | JSON string | 120s | ChangeEngine | DigestService |
| `session:{userId}:{watchlistId}` | ISO timestamp string | none | DigestService | DigestService |

**Acceptance criteria:**
- Document covers all Redis keys used by the system.
- Writer and reader are clearly identified for each key.

**Testing:**
- Code review / documentation review.

---

## EPIC 5 — Watchlist Management

---

### TASK-050

**Title:** Watchlist repository (DB layer)  
**Epic:** Watchlist Management  
**Priority:** P0  

**Description:**  
Implement the data access layer for watchlist operations. This is a pure DB layer — no HTTP, no business logic. Functions: `createWatchlist`, `listWatchlistsByUser`, `getWatchlistById`, `deleteWatchlist`, `addInstrument`, `removeInstrument`, `getInstrumentsForWatchlist`, `countWatchlistsForUser`, `countInstrumentsInWatchlist`.

**Dependencies:** TASK-024

**Files likely affected:**
```
backend/src/repositories/watchlistRepository.ts
backend/src/types/watchlist.ts
```

**Implementation notes:**
- All queries must include `WHERE user_id = $userId` to enforce data isolation.
- `createWatchlist`: returns the created row. Enforces max 10 watchlists per user at DB level (check before insert).
- `addInstrument`: returns the created row. Enforces max 100 instruments per watchlist.
- All functions accept a DB client parameter for transaction support.
- Use parameterized queries only — never string interpolation.

**Acceptance criteria:**
- All repository functions return typed results.
- `createWatchlist` rejects if user already has 10 watchlists.
- `addInstrument` rejects if watchlist has 100 instruments.
- All queries are parameterized.

**Testing:**
- Unit test: each function with a test DB.
- Test limit enforcement: create 11 watchlists; verify rejection at 11th.
- Test limit enforcement: add 101 instruments; verify rejection at 101st.

---

### TASK-051

**Title:** Create watchlist API handler  
**Epic:** Watchlist Management  
**Priority:** P0  

**Description:**  
Implement `POST /v1/watchlists`. Validates request body, enforces name length constraint (1–64 chars), checks user watchlist limit, creates the watchlist, creates the session row, returns 201.

**Dependencies:** TASK-050, TASK-012, TASK-014

**Files likely affected:**
```
backend/src/routes/watchlists.ts
backend/src/schemas/watchlistSchemas.ts
```

**Implementation notes:**
- JSON schema validation via Fastify's built-in validation (no Zod for route input — use JSON schema).
- Input: `{ "name": "Tech Picks" }`.
- On success: 201 with created watchlist object.
- On limit exceeded: 422 with RFC-7807 error `watchlist-limit-exceeded`.
- Create a corresponding `user_watchlist_sessions` row with `last_checked_at = NULL` on watchlist creation.

**Acceptance criteria:**
- `POST /v1/watchlists` with valid name returns 201 with watchlist object.
- Name > 64 chars returns 400.
- Empty name returns 400.
- Creating 11th watchlist returns 422 with correct error type.

**Testing:**
- Integration test: happy path, validation failures, limit exceeded.

---

### TASK-052

**Title:** List watchlists API handler  
**Epic:** Watchlist Management  
**Priority:** P0  

**Description:**  
Implement `GET /v1/watchlists`. Returns all watchlists for the authenticated user, ordered by `display_order`. Each item includes instrument_count (no market data at this level).

**Dependencies:** TASK-050, TASK-012

**Files likely affected:**
```
backend/src/routes/watchlists.ts
```

**Implementation notes:**
- Response includes `id`, `name`, `instrument_count`, `created_at`, `updated_at`.
- Empty watchlists list returns `{"watchlists": []}` (not 404).
- User isolation: `WHERE user_id = jwt.user_id` always.

**Acceptance criteria:**
- Returns only watchlists belonging to the authenticated user.
- Returns empty array (not error) for user with no watchlists.
- Ordered by `display_order`.

**Testing:**
- Create 3 watchlists; verify all 3 returned.
- User A cannot see User B's watchlists.

---

### TASK-053

**Title:** Delete watchlist API handler  
**Epic:** Watchlist Management  
**Priority:** P0  

**Description:**  
Implement `DELETE /v1/watchlists/{watchlist_id}`. Verifies ownership, deletes the watchlist (cascade removes instruments and session), returns 204.

**Dependencies:** TASK-050, TASK-012

**Files likely affected:**
```
backend/src/routes/watchlists.ts
```

**Implementation notes:**
- Verify the watchlist belongs to `jwt.user_id` before deletion.
- ON DELETE CASCADE handles cleanup of `watchlist_instruments` and `user_watchlist_sessions`.
- If watchlist not found or not owned: 404.
- Return 204 No Content.

**Acceptance criteria:**
- DELETE returns 204 on success.
- Attempting to delete a non-existent watchlist returns 404.
- User B cannot delete User A's watchlist (returns 404).

**Testing:**
- Happy path delete. Verify instrument rows also gone.
- Attempt to delete another user's watchlist; verify 404.

---

### TASK-054

**Title:** Get watchlist detail API handler (with market data)  
**Epic:** Watchlist Management  
**Priority:** P0  

**Description:**  
Implement `GET /v1/watchlists/{watchlist_id}`. Returns the watchlist's instruments with current market data from Redis (or DB fallback). Includes `data_freshness` and `data_as_of` in response.

**Dependencies:** TASK-050, TASK-040, TASK-135

**Files likely affected:**
```
backend/src/routes/watchlists.ts
backend/src/services/watchlistService.ts
```

**Implementation notes:**
- For each instrument: check Redis for `price:{symbol}`. If miss, fall back to latest DB snapshot.
- Each instrument gets a per-instrument `data_status` field: `live` | `stale` | `unavailable`.
- Aggregate `data_freshness` is the worst across all instruments.
- If an instrument is SUSPENDED: include it with `data_status: "suspended"`.
- Response matches the shape in DESIGN.md §26.

**Acceptance criteria:**
- Returns correct watchlist with instruments and market data.
- Redis miss falls back to DB gracefully.
- SUSPENDED instrument returns with `data_status: "suspended"`.
- Returns 404 for wrong owner.

**Testing:**
- Happy path with Redis hit.
- Redis miss → DB fallback.
- Include a suspended instrument; verify label.

---

### TASK-055

**Title:** Add instrument to watchlist API handler  
**Epic:** Watchlist Management  
**Priority:** P0  

**Description:**  
Implement `POST /v1/watchlists/{watchlist_id}/instruments`. Validates symbol, checks it exists in instruments table, checks for duplicates, checks watchlist limit, adds the instrument.

**Dependencies:** TASK-050, TASK-012

**Files likely affected:**
```
backend/src/routes/watchlistInstruments.ts
```

**Implementation notes:**
- Input: `{ "symbol": "RELIANCE" }`.
- Symbol must exist in `instruments` table (not just a free-text field).
- Duplicate (already in watchlist): 422 with `duplicate-instrument`.
- Watchlist full (100 instruments): 422 with `watchlist-instrument-limit-exceeded`.
- Instrument SUSPENDED: still allowed to add (user should be informed via `data_status` on detail view).
- Return 201 with the added instrument object.

**Acceptance criteria:**
- Valid symbol not in watchlist: 201.
- Symbol not in instruments table: 404 instrument-not-found.
- Duplicate: 422 duplicate-instrument.
- 101st instrument: 422 limit-exceeded.

**Testing:**
- All above scenarios as integration tests.

---

### TASK-056

**Title:** Remove instrument from watchlist API handler  
**Epic:** Watchlist Management  
**Priority:** P0  

**Description:**  
Implement `DELETE /v1/watchlists/{watchlist_id}/instruments/{symbol}`. Verifies watchlist ownership and instrument presence, removes the instrument, returns 204.

**Dependencies:** TASK-050, TASK-012

**Files likely affected:**
```
backend/src/routes/watchlistInstruments.ts
```

**Implementation notes:**
- Verify watchlist belongs to user.
- If instrument not in watchlist: 404.
- Delete row from `watchlist_instruments`.
- Return 204 No Content.
- Note: ChangeEngine may be mid-computation for this instrument. That is acceptable — the ChangeEvent already written is orphaned but harmless; next cycle it won't be computed.

**Acceptance criteria:**
- Remove an instrument: 204.
- Remove instrument not in watchlist: 404.
- Remove instrument from another user's watchlist: 404.

**Testing:**
- Happy path. Error cases.

---

### TASK-057

**Title:** Reorder instruments within watchlist  
**Epic:** Watchlist Management  
**Priority:** P2  

**Description:**  
Implement `PATCH /v1/watchlists/{watchlist_id}/instruments/order`. Accepts an ordered array of symbols and updates `display_order` values accordingly.

**Dependencies:** TASK-050, TASK-012

**Files likely affected:**
```
backend/src/routes/watchlistInstruments.ts
```

**Implementation notes:**
- Input: `{ "symbols": ["RELIANCE", "TCS", "INFY"] }`.
- All symbols must be in the watchlist; any unknown symbol → 422.
- Use a transaction to update all `display_order` values atomically.
- Response: 200 with the updated instrument list.

**Acceptance criteria:**
- Reorder returns 200 and instruments are served in new order.
- Unknown symbol in reorder payload → 422.

**Testing:**
- Reorder 3 instruments; verify new order in GET response.

---

### TASK-058

**Title:** Watchlist input validation  
**Epic:** Watchlist Management  
**Priority:** P0  

**Description:**  
Ensure all watchlist and instrument inputs are validated at the API layer before hitting the DB. This is a hardening task that reviews TASK-051 and TASK-055 to confirm all validations are in place.

**Dependencies:** TASK-051, TASK-055

**Files likely affected:**
```
backend/src/schemas/watchlistSchemas.ts
backend/src/schemas/instrumentSchemas.ts
```

**Implementation notes:**
- Watchlist name: 1–64 chars, trimmed, non-empty after trimming.
- Instrument symbol: 1–20 chars, uppercase, alphanumeric + `-` only.
- All inputs validated via Fastify JSON schema before handler runs.
- Never trust client-supplied `user_id`.

**Acceptance criteria:**
- Symbol `"'; DROP TABLE instruments; --"` returns 400.
- Name with 65+ chars returns 400.
- All edge-case inputs validated.

**Testing:**
- Fuzz test: send various malformed inputs; all should return 400.

---

### TASK-059

**Title:** Duplicate instrument prevention  
**Epic:** Watchlist Management  
**Priority:** P0  

**Description:**  
Verify and test that the composite PRIMARY KEY on `watchlist_instruments(watchlist_id, instrument_symbol)` correctly prevents duplicate adds, and that the API returns a meaningful 422 error (not a raw DB error).

**Dependencies:** TASK-055

**Files likely affected:**
```
backend/src/repositories/watchlistRepository.ts
backend/src/routes/watchlistInstruments.ts
```

**Implementation notes:**
- The repository `addInstrument` should catch the unique constraint violation (`pg` error code `23505`) and rethrow as `DuplicateInstrumentError`.
- The route handler converts `DuplicateInstrumentError` → 422 RFC-7807 response.
- Test: add the same symbol twice; verify the second gets 422 `duplicate-instrument`.

**Acceptance criteria:**
- Second add of same symbol returns 422 `duplicate-instrument` (not 500).
- Error response has correct `type`, `title`, `detail`.

**Testing:**
- Integration test: add same symbol twice.

---

## EPIC 6 — Instrument Search

---

### TASK-060

**Title:** Instrument search repository  
**Epic:** Instrument Search  
**Priority:** P0  

**Description:**  
Implement the data access layer for instrument full-text / trigram search. Returns symbol, name, exchange, sector for matched instruments.

**Dependencies:** TASK-023

**Files likely affected:**
```
backend/src/repositories/instrumentRepository.ts
```

**Implementation notes:**
- Use `pg_trgm` for partial name matching: `WHERE name % $query OR symbol ILIKE $query || '%'`.
- `LIMIT` is passed by the caller (default 10, max 20).
- Order: exact symbol match first, then by `similarity(name, $query)` descending.
- Only return `status = 'ACTIVE'` instruments in search results (exclude suspended/delisted).

**Acceptance criteria:**
- Search `"HDFC"` returns HDFCBANK, HDFCLIFE, etc.
- Search by partial name works.
- Suspended instruments do not appear in search.
- Results are ordered by relevance.

**Testing:**
- Unit test with seeded data: verify result order and filtering.

---

### TASK-061

**Title:** Instrument search API handler  
**Epic:** Instrument Search  
**Priority:** P0  

**Description:**  
Implement `GET /v1/instruments/search?q={query}&limit={N}`. Validates query, calls the search repository, returns results.

**Dependencies:** TASK-060, TASK-012

**Files likely affected:**
```
backend/src/routes/instruments.ts
```

**Implementation notes:**
- `q` is required, 1–50 chars, sanitized (parameterized query prevents injection).
- `limit` optional, integer, 1–20, default 10.
- If `q` is empty or missing: 400.
- No authentication required for search — but rate limited (see TASK-062).
- Response: `{"results": [{symbol, name, exchange, sector}]}`.

**Acceptance criteria:**
- `GET /instruments/search?q=HDFC` returns matching instruments.
- `GET /instruments/search` (no q) returns 400.
- Limit is capped at 20.

**Testing:**
- Integration: happy path, missing query, limit capping.

---

### TASK-062

**Title:** Instrument search rate limiting and input sanitization  
**Epic:** Instrument Search  
**Priority:** P1  

**Description:**  
Apply the 20 requests/minute rate limit to the search endpoint specifically. Verify that the query parameter is properly sanitized and cannot be used for SQL injection.

**Dependencies:** TASK-061, TASK-015

**Files likely affected:**
```
backend/src/routes/instruments.ts
```

**Implementation notes:**
- Override the route-level rate limit to 20 rpm (vs global 100).
- Fuzz the `q` parameter with SQL injection payloads; all should be handled safely by the parameterized query.
- Strip leading/trailing whitespace from `q` before querying.

**Acceptance criteria:**
- 21st request in a minute returns 429.
- SQL injection payloads return 0 results, not errors.

**Testing:**
- Rate limit test: 21 rapid requests.
- SQL injection payload test: `'; DROP TABLE instruments; --` → 0 results, 200 status.

---

## EPIC 7 — Market Data Abstraction

---

### TASK-070

**Title:** MarketDataProvider interface definition  
**Epic:** Market Data Abstraction  
**Priority:** P0  

**Description:**  
Define the `MarketDataProvider` interface in the shared package. This interface is the contract that both `DemoMarketDataProvider` and `LiveMarketDataProvider` must implement. Also define the `Quote` and `SectorQuote` types.

**Dependencies:** TASK-004

**Files likely affected:**
```
shared/src/marketData/MarketDataProvider.ts
shared/src/marketData/types.ts
```

**Implementation notes:**
```typescript
interface Quote {
  symbol: string;
  price: number;
  dayChangeAbs: number;
  dayChangePct: number;
  volume: number;
  high52w: number;
  low52w: number;
  atr14: number;       // ATR(14) as % of price
  avgVolume20d: number;
  fetchedAt: Date;
}

interface SectorQuote {
  sector: string;
  changePct: number;
  fetchedAt: Date;
}

interface MarketDataProvider {
  fetchQuotes(symbols: string[]): Promise<Quote[]>;
  fetchSectorQuotes(sectors: string[]): Promise<SectorQuote[]>;
  isMarketOpen(): boolean;
}
```

**Acceptance criteria:**
- Interface is exported from the shared package.
- `Quote` and `SectorQuote` types cover all fields written to `price_snapshots` and `sector_snapshots`.
- `isMarketOpen()` is part of the interface.

**Testing:**
- TypeScript compilation verifies the interface is valid.

---

### TASK-071

**Title:** DemoMarketDataProvider (deterministic)  
**Epic:** Market Data Abstraction  
**Priority:** P0  

**Description:**  
Implement `DemoMarketDataProvider` that returns deterministic, scripted market data for a set of demo instruments. Used when `DEMO_MODE=true`. Must be able to simulate all six demo scenarios.

**Dependencies:** TASK-070

**Files likely affected:**
```
worker/src/marketData/DemoMarketDataProvider.ts
worker/src/marketData/demoScenarios.ts
```

**Implementation notes:**
- Scenarios are defined in `demoScenarios.ts` as static data fixtures.
- Each scenario provides a snapshot of prices, ATR, volume, and sector returns.
- A scenario index advances on each `fetchQuotes()` call (simulating 60s cycles).
- Scenarios:
  1. `NORMAL`: all stocks within normal range.
  2. `VAPM_SPIKE`: HDFCBANK moves 2.8x ATR.
  3. `VOLUME_ANOMALY`: INFY at 3.1x avg volume.
  4. `NO_CHANGE`: all MCS = 0.
  5. `STALE_DATA`: provider returns an error (simulates pipeline failure).
  6. `RECOVERY`: provider returns data again after a STALE cycle.
- `isMarketOpen()` always returns `true` in demo mode.

**Acceptance criteria:**
- All 6 scenarios produce the expected signal values.
- Provider cycles through scenarios deterministically.
- `STALE_DATA` scenario throws an error that the circuit breaker catches.

**Testing:**
- Unit test: each scenario produces expected Quote values.
- Unit test: scenario sequencing works correctly.

---

### TASK-072

**Title:** LiveMarketDataProvider  
**Epic:** Market Data Abstraction  
**Priority:** P1  

**Description:**  
Implement `LiveMarketDataProvider` that fetches real data from a market data API (e.g., NSE unofficial API, or a paid provider like Polygon.io / Twelve Data). Used when `DEMO_MODE=false`.

**Dependencies:** TASK-070

**Files likely affected:**
```
worker/src/marketData/LiveMarketDataProvider.ts
```

**Implementation notes:**
- Reads `MARKET_DATA_API_KEY` from env.
- Fetches quotes in batches (to avoid API rate limits).
- Maps the provider's response format to `Quote[]`.
- Throws a `ProviderError` on non-200 responses or network timeouts.
- `isMarketOpen()` checks the system clock against IST market hours (09:15–15:30, Mon–Fri, non-holiday). Uses the exchange calendar from TASK-074.
- Timeout: 10 seconds per fetch call.

**Acceptance criteria:**
- Returns valid `Quote[]` for a set of NSE symbols.
- Throws `ProviderError` on API failure.
- Respects `isMarketOpen()` based on IST time.

**Testing:**
- Mock the HTTP client; unit test response mapping.
- Test `ProviderError` on HTTP 500 response.

---

### TASK-073

**Title:** Outlier filter preprocessor  
**Epic:** Market Data Abstraction  
**Priority:** P0  

**Description:**  
Implement a pure function that filters out quotes where the single-tick price move exceeds 20% (configurable via `OUTLIER_FILTER_MAX_PCT`). Takes the previous price from Redis/DB and compares to the new quote.

**Dependencies:** TASK-070

**Files likely affected:**
```
worker/src/marketData/outlierFilter.ts
```

**Implementation notes:**
```typescript
function filterOutliers(
  quotes: Quote[],
  previousPrices: Map<string, number>,
  maxSingleTickMovePct: number
): { valid: Quote[], rejected: RejectedQuote[] }
```
- Log each rejected quote with the computed tick move for observability.
- A quote with no previous price (new instrument) is always accepted.
- Rejected quotes are logged but not persisted.

**Acceptance criteria:**
- Quote with 25% single-tick move is rejected (given max = 20%).
- Quote with 15% move is accepted.
- New instrument (no previous price) is always accepted.
- Rejection is logged.

**Testing:**
- Unit: various price move scenarios against the filter threshold.

---

### TASK-074

**Title:** Market calendar and hours checker  
**Epic:** Market Data Abstraction  
**Priority:** P0  

**Description:**  
Implement a utility that determines whether NSE is currently open based on: IST time, day of week, and a static holiday calendar. Used by `LiveMarketDataProvider.isMarketOpen()` and the MarketWorker cycle loop.

**Dependencies:** TASK-004

**Files likely affected:**
```
shared/src/market/marketCalendar.ts
shared/src/market/nseHolidays2026.ts
```

**Implementation notes:**
- Market hours: 09:15–15:30 IST, Mon–Fri.
- Holiday list: static array of holiday dates for 2026 (NSE published list).
- `isMarketOpen(now: Date): boolean`.
- `getLastMarketClose(now: Date): Date` — returns the most recent market close timestamp before `now`.
- `getNextMarketOpen(now: Date): Date` — returns the next expected open after `now`.

**Acceptance criteria:**
- Returns `true` for a weekday 10:00 IST with no holiday.
- Returns `false` for a Saturday.
- Returns `false` for a NSE holiday.
- Returns `false` outside 09:15–15:30.
- `getLastMarketClose()` returns Friday's close when called on Sunday.

**Testing:**
- Unit tests for each condition: weekend, holiday, outside hours, during hours.
- Test `getLastMarketClose()` for Friday → Sunday case.

---

## EPIC 8 — Market Worker

---

### TASK-080

**Title:** MarketWorker process scaffold (separate Node.js process)  
**Epic:** Market Worker  
**Priority:** P0  

**Description:**  
Create the `worker` package entry point. The worker is a separate Node.js process (not Fastify, no HTTP) that runs the 60-second market data cycle. It has its own DB and Redis connections.

**Dependencies:** TASK-072, TASK-073, TASK-040, TASK-026

**Files likely affected:**
```
worker/src/index.ts
worker/src/worker.ts
worker/package.json
worker/tsconfig.json
```

**Implementation notes:**
- Worker starts, connects to DB and Redis, then enters the cycle loop.
- Reads `DEMO_MODE` env: if `true`, uses `DemoMarketDataProvider`; otherwise `LiveMarketDataProvider`.
- On startup: log worker start, provider mode, DB connection status.
- Graceful shutdown: handle `SIGTERM` and `SIGINT` (see TASK-086).

**Acceptance criteria:**
- `npm run dev` in the worker package starts the worker process.
- Worker logs its provider mode on startup.
- Worker connects to DB and Redis without errors.

**Testing:**
- Start worker in demo mode; verify startup logs.

---

### TASK-081

**Title:** MarketWorker 60-second cycle loop  
**Epic:** Market Worker  
**Priority:** P0  

**Description:**  
Implement the main fetch cycle: check if market is open → fetch quotes → filter outliers → write to DB/Redis → trigger ChangeEngine. The loop runs every 60 seconds.

**Dependencies:** TASK-080

**Files likely affected:**
```
worker/src/worker.ts
worker/src/cycle.ts
```

**Implementation notes:**
- Use `setInterval` or a self-scheduling async loop (prefer the latter for accurate timing).
- Cycle structure:
  1. Check `isMarketOpen()`. If not, log and skip.
  2. Increment global `cycle_id` (monotonic counter, stored in Redis or in-memory).
  3. Fetch all tracked instrument symbols from DB (`UNION` across all watchlists).
  4. Call `provider.fetchQuotes(symbols)`.
  5. Run outlier filter.
  6. Write valid quotes to `price_snapshots` (TASK-083).
  7. Write to Redis cache (TASK-084).
  8. Fetch sector quotes (TASK-085).
  9. Trigger ChangeEngine (TASK-090).
- If a cycle takes longer than 60 seconds: log a warning, do not start overlapping cycles.
- Track cycle start/end timestamps for observability.

**Acceptance criteria:**
- Cycle runs every ~60 seconds.
- Market closed: cycle is skipped with a log entry.
- Slow cycle does not overlap with the next one.
- `cycle_id` increments on each successful cycle.

**Testing:**
- Unit: mock provider and verify cycle steps are called in order.
- Integration: run 2 cycles in demo mode; verify 2 rows in price_snapshots per instrument.

---

### TASK-082

**Title:** Circuit breaker for upstream market data provider  
**Epic:** Market Worker  
**Priority:** P0  

**Description:**  
Implement a circuit breaker wrapping the provider's `fetchQuotes()` call. After 3 consecutive failures within a 60-second window, open the circuit and skip fetch cycles. After 30 seconds, probe once (half-open state). On success, close.

**Dependencies:** TASK-081

**Files likely affected:**
```
worker/src/circuitBreaker.ts
```

**Implementation notes:**
- States: `CLOSED` → `OPEN` → `HALF_OPEN` → `CLOSED`.
- Failure threshold: 3 (configurable).
- Open duration: 30 seconds.
- When open: log `[CircuitBreaker] OPEN — skipping fetch cycle` and continue to serve stale data.
- When half-open probe fails: return to `OPEN`.
- Emit metrics (see TASK-162): `market_worker_fetch_failures_total`, `circuit_breaker_state`.

**Acceptance criteria:**
- 3 consecutive provider failures open the circuit.
- After 30s, half-open probe is attempted.
- Success from half-open closes the circuit.
- Circuit state is logged at each transition.

**Testing:**
- Unit: simulate 3 failures → verify OPEN state.
- Unit: simulate half-open probe success → verify CLOSED.
- Unit: simulate half-open probe failure → verify OPEN again.

---

### TASK-083

**Title:** Write PriceSnapshots to DB (idempotent)  
**Epic:** Market Worker  
**Priority:** P0  

**Description:**  
Implement the function that writes `Quote[]` to the `price_snapshots` table. Uses `INSERT ... ON CONFLICT (instrument_symbol, cycle_id) DO NOTHING` for idempotency.

**Dependencies:** TASK-081, TASK-026

**Files likely affected:**
```
worker/src/repositories/priceSnapshotRepository.ts
```

**Implementation notes:**
- Batch insert all quotes for a cycle in a single SQL statement (values list).
- Set `snapshot_at = fetchStartTime` (not `NOW()` — use the time the fetch was initiated).
- On conflict: `DO NOTHING` (a slow previous cycle writing duplicate data is silently ignored).
- Log count of rows written vs rejected.

**Acceptance criteria:**
- All valid quotes for a cycle are written in one DB call.
- Calling twice with the same `cycle_id` does not error and does not create duplicates.
- `snapshot_at` matches the cycle fetch start time.

**Testing:**
- Insert a full cycle; verify row count.
- Insert same cycle twice; verify row count is unchanged.

---

### TASK-084

**Title:** Write latest prices to Redis cache  
**Epic:** Market Worker  
**Priority:** P0  

**Description:**  
After a successful DB write, update the Redis cache with the latest quote for each instrument (`price:{symbol}`). Set TTL to 120 seconds.

**Dependencies:** TASK-083, TASK-040

**Files likely affected:**
```
worker/src/cache/priceCache.ts
```

**Implementation notes:**
- Use Redis `MSET` or a pipeline to write all instruments at once (avoid N individual writes).
- Each value is a JSON-serialized `Quote` object.
- TTL: 120 seconds (set with `PSETEX` or pipeline `SET ... EX 120`).
- If Redis write fails: log error but do not fail the cycle (DB is the authoritative store).

**Acceptance criteria:**
- After a cycle, `redis-cli GET price:HDFCBANK` returns valid JSON.
- TTL is set.
- Redis write failure does not crash the worker.

**Testing:**
- Run a cycle; verify Redis keys are set with correct values.
- Simulate Redis failure; verify cycle continues.

---

### TASK-085

**Title:** Fetch and store SectorSnapshots  
**Epic:** Market Worker  
**Priority:** P0  

**Description:**  
On each cycle, fetch the 12 sector index returns (and Nifty 50) from the provider. Store them in `sector_snapshots` table and in Redis (`price:{NIFTY50}`, `price:{NIFTYBANK}`, etc.).

**Dependencies:** TASK-081, TASK-027

**Files likely affected:**
```
worker/src/repositories/sectorSnapshotRepository.ts
```

**Implementation notes:**
- Sector symbols are defined in `shared/src/market/sectorSymbols.ts`: `NIFTYBANK`, `NIFTYIT`, etc.
- Write to `sector_snapshots` with the same `cycle_id` as the instrument quotes.
- Also write sector returns to Redis for fast access by DigestService.

**Acceptance criteria:**
- After a cycle, `sector_snapshots` has one row per sector per cycle.
- Redis has the latest sector return for each sector symbol.

**Testing:**
- Run a cycle; verify 13 sector snapshot rows (12 sectors + Nifty50).

---

### TASK-086

**Title:** MarketWorker graceful shutdown  
**Epic:** Market Worker  
**Priority:** P1  

**Description:**  
Handle `SIGTERM` and `SIGINT` in the worker process. On shutdown signal: wait for the current cycle to complete (or abort if running > 10s), close DB connections, close Redis, exit cleanly.

**Dependencies:** TASK-081

**Files likely affected:**
```
worker/src/index.ts
worker/src/worker.ts
```

**Implementation notes:**
- Set a `shuttingDown` flag on signal receipt.
- If a cycle is in progress: let it finish (wait max 10 seconds).
- Close `pg` pool and `ioredis` connections.
- Exit with code 0.
- In Docker: the default `STOPSIGNAL` is `SIGTERM`; this ensures clean shutdown.

**Acceptance criteria:**
- `kill -SIGTERM <pid>` causes a clean shutdown with exit code 0.
- Shutdown log message confirms clean exit.

**Testing:**
- Start worker, send SIGTERM, verify clean exit.

---

## EPIC 9 — Meaningful Change Engine

---

### TASK-090

**Title:** ChangeEngine scaffold and entry point  
**Epic:** Meaningful Change Engine  
**Priority:** P0  

**Description:**  
Create the ChangeEngine module that is called by the MarketWorker after each successful cycle. The ChangeEngine reads the previous completed cycle's snapshots, computes signals and MCS for all instruments in any watchlist, and writes ChangeEvents.

**Dependencies:** TASK-083, TASK-084, TASK-027

**Files likely affected:**
```
worker/src/changeEngine/changeEngine.ts
worker/src/changeEngine/index.ts
```

**Implementation notes:**
- Entry: `runChangeEngine(cycleId: number): Promise<void>`.
- Reads snapshots from `price_snapshots` WHERE `cycle_id = cycleId - 1` (previous completed cycle).
- Determines "instruments to compute": all symbols currently in any watchlist (joins `watchlist_instruments` and `instruments`).
- Runs signal computation for each instrument.
- Writes ChangeEvents to DB and updates Redis.
- Logs: start, instrument count, computation time, event count written.

**Acceptance criteria:**
- Called with `cycleId = N`; reads cycle `N-1` snapshots.
- Computes MCS for all instruments in any watchlist.
- Logs total computation time.

**Testing:**
- Integration: seed snapshots for cycle 5; call `runChangeEngine(6)`; verify ChangeEvents written.

---

### TASK-091

**Title:** Signal data model (types and interfaces)  
**Epic:** Meaningful Change Engine  
**Priority:** P0  

**Description:**  
Define TypeScript types for the signal computation inputs and outputs. These types flow through the entire ChangeEngine and are used in ChangeEvent persistence.

**Dependencies:** TASK-090

**Files likely affected:**
```
shared/src/changeEngine/types.ts
```

**Implementation notes:**
```typescript
interface SignalInputs {
  symbol: string;
  currentPrice: number;
  baselinePrice: number;
  atr14Pct: number | null;       // null = ATR unavailable
  sectorChangePct: number;
  currentVolume: number;
  avgVolume20d: number;
}

interface SignalOutputs {
  vapm: number | null;           // null = ATR unavailable
  srm: number;
  va: number;
  vapmSignal: number;
  srmSignal: number;
  vaSignal: number;
  mcs: number;
}

interface ChangeEvent {
  symbol: string;
  cycleId: number;
  signals: SignalOutputs;
  explanationTemplate: string;
  explanationParams: Record<string, unknown>;
  computedAt: Date;
}
```

**Acceptance criteria:**
- Types cover all fields in the `change_events` DB table.
- `atr14Pct: null` models the "ATR unavailable" case correctly.

**Testing:**
- TypeScript compilation verifies types.

---

### TASK-092

**Title:** Compute VAPM signal  
**Epic:** Meaningful Change Engine  
**Priority:** P0  

**Description:**  
Implement the `computeVAPM(inputs: SignalInputs): number | null` function. Returns null if ATR is unavailable.

**Formula:** `VAPM = |price_delta_pct| / ATR14_pct`

**Dependencies:** TASK-091

**Files likely affected:**
```
worker/src/changeEngine/signals/vapm.ts
```

**Implementation notes:**
```typescript
function computeVAPM(inputs: SignalInputs): number | null {
  if (inputs.atr14Pct === null || inputs.atr14Pct === 0) return null;
  const priceDeltaPct = Math.abs(
    (inputs.currentPrice - inputs.baselinePrice) / inputs.baselinePrice * 100
  );
  return priceDeltaPct / inputs.atr14Pct;
}
```
- If `atr14Pct = 0`: return null (division by zero guard).
- `baselinePrice = 0`: guard and log error, return null.

**Acceptance criteria:**
- Stock at 2x ATR returns VAPM = 2.0.
- ATR unavailable returns null.
- ATR = 0 returns null.

**Testing:**
- Unit: normal case, ATR null, ATR zero, baselinePrice zero, large move, small move.

---

### TASK-093

**Title:** Compute SRM signal  
**Epic:** Meaningful Change Engine  
**Priority:** P0  

**Description:**  
Implement `computeSRM(inputs: SignalInputs): number`.

**Formula:** `SRM = |stock_delta_pct - sector_delta_pct|`

**Dependencies:** TASK-091

**Files likely affected:**
```
worker/src/changeEngine/signals/srm.ts
```

**Implementation notes:**
```typescript
function computeSRM(inputs: SignalInputs): number {
  const stockDeltaPct =
    (inputs.currentPrice - inputs.baselinePrice) / inputs.baselinePrice * 100;
  return Math.abs(stockDeltaPct - inputs.sectorChangePct);
}
```
- Always returns a non-negative number.
- `sectorChangePct` is the sector return over the same window.

**Acceptance criteria:**
- Stock +3%, sector +3% → SRM = 0.
- Stock +4%, sector +1% → SRM = 3.0.
- Stock -2%, sector +1% → SRM = 3.0.

**Testing:**
- Unit: all above cases plus baselinePrice zero guard.

---

### TASK-094

**Title:** Compute VA signal  
**Epic:** Meaningful Change Engine  
**Priority:** P0  

**Description:**  
Implement `computeVA(inputs: SignalInputs): number`.

**Formula:** `VA = current_volume / avg_daily_volume_20d`

**Dependencies:** TASK-091

**Files likely affected:**
```
worker/src/changeEngine/signals/va.ts
```

**Implementation notes:**
```typescript
function computeVA(inputs: SignalInputs): number {
  if (inputs.avgVolume20d === 0) return 0; // guard: no historical average
  return inputs.currentVolume / inputs.avgVolume20d;
}
```
- If `avgVolume20d = 0` (new listing, no 20-day history): return 0 (no VA contribution).
- If `currentVolume = 0` (circuit-breaker halt, no trades): return 0.

**Acceptance criteria:**
- 2.5x normal volume → VA = 2.5.
- No average available (0) → VA = 0.
- Zero volume → VA = 0.

**Testing:**
- Unit: normal, zero avg, zero volume, very high volume.

---

### TASK-095

**Title:** Apply signal floors  
**Epic:** Meaningful Change Engine  
**Priority:** P0  

**Description:**  
Implement `applySignalFloors(vapm, srm, va, config): SignalFloorOutputs`. Applies `max(0, signal - floor)` to each signal. Reads floors from config.

**Dependencies:** TASK-091, TASK-092, TASK-093, TASK-094

**Files likely affected:**
```
worker/src/changeEngine/signals/floors.ts
worker/src/changeEngine/config.ts
```

**Implementation notes:**
```typescript
const VAPM_FLOOR = parseFloat(process.env.VAPM_FLOOR ?? '1.5');
const SRM_FLOOR  = parseFloat(process.env.SRM_FLOOR  ?? '1.5');
const VA_FLOOR   = parseFloat(process.env.VA_FLOOR   ?? '2.0');

function applyFloors(vapm: number | null, srm: number, va: number) {
  return {
    vapmSignal: vapm !== null ? Math.max(0, vapm - VAPM_FLOOR) : 0,
    srmSignal:  Math.max(0, srm - SRM_FLOOR),
    vaSignal:   Math.max(0, va  - VA_FLOOR),
  };
}
```
- VAPM null → vapmSignal = 0 (not a negative number).
- Floors are read from environment (configurable without code deploy).

**Acceptance criteria:**
- VAPM 2.8 with floor 1.5 → vapmSignal = 1.3.
- VAPM 1.2 with floor 1.5 → vapmSignal = 0.0.
- VAPM null → vapmSignal = 0.0.

**Testing:**
- Unit: above-floor, below-floor, at-floor, null cases for each signal.

---

### TASK-096

**Title:** Compute weighted MCS  
**Epic:** Meaningful Change Engine  
**Priority:** P0  

**Description:**  
Implement `computeMCS(floorOutputs, weights): number`. Combines the three signal contributions using configurable weights. Returns the Meaningful Change Score.

**Formula:** `MCS = w1 * VAPM_signal + w2 * SRM_signal + w3 * VA_signal`

**Dependencies:** TASK-095

**Files likely affected:**
```
worker/src/changeEngine/signals/mcs.ts
worker/src/changeEngine/config.ts
```

**Implementation notes:**
```typescript
const W1 = parseFloat(process.env.MCS_WEIGHT_VAPM ?? '0.50');
const W2 = parseFloat(process.env.MCS_WEIGHT_SRM  ?? '0.35');
const W3 = parseFloat(process.env.MCS_WEIGHT_VA   ?? '0.15');

function computeMCS(floors: SignalFloorOutputs): number {
  return W1 * floors.vapmSignal + W2 * floors.srmSignal + W3 * floors.vaSignal;
}
```
- Weights are read from env; sum to 1.0 by convention (not enforced — they are weights, not probabilities).
- MCS >= 0 always (guaranteed by signal floor application).

**Acceptance criteria:**
- VAPM_signal=1.3, SRM_signal=1.7, VA_signal=0 → MCS = 0.5*1.3 + 0.35*1.7 + 0.15*0 = 1.245.
- All signals at floor → MCS = 0.
- MCS is never negative.

**Testing:**
- Unit: verify examples from DESIGN.md §13 scoring table.
  - HDFC Bank: VAPM=2.8, SRM=3.2, VA=1.1 → MCS=1.25 ✓
  - Infosys: VAPM=1.3, SRM=0.4, VA=1.4 → MCS=0.0 ✓
  - Zomato: VAPM=1.6, SRM=0.8, VA=3.1 → MCS=0.19 ✓

---

### TASK-097

**Title:** Handle ATR unavailable (new listing, < 14 days of data)  
**Epic:** Meaningful Change Engine  
**Priority:** P0  

**Description:**  
When a stock has fewer than 14 days of trading history, `atr_14` in the price snapshot will be null. Handle this case: disable VAPM signal, still compute SRM and VA.

**Dependencies:** TASK-092, TASK-095, TASK-096

**Files likely affected:**
```
worker/src/changeEngine/changeEngine.ts
```

**Implementation notes:**
- When `snapshot.atr_14` is null: pass `atr14Pct: null` to `computeVAPM`, which returns null.
- `applyFloors(null, ...)` → `vapmSignal = 0`.
- SRM and VA computed normally.
- Log the instrument symbol when ATR is unavailable (observable).
- The `ChangeEvent` record stores `vapm = null` in this case.

**Acceptance criteria:**
- New listing with null ATR: MCS computed from SRM and VA only.
- No error thrown; system continues computing.
- `change_events.vapm` is null for this instrument.

**Testing:**
- Integration: insert a snapshot with null ATR; run ChangeEngine; verify ChangeEvent has null vapm but valid MCS from SRM/VA.

---

### TASK-098

**Title:** Handle missing or stale snapshot data  
**Epic:** Meaningful Change Engine  
**Priority:** P0  

**Description:**  
When a snapshot is missing for an instrument in the previous cycle (e.g., provider returned partial data), the ChangeEngine should skip computation for that instrument and log the skip.

**Dependencies:** TASK-090

**Files likely affected:**
```
worker/src/changeEngine/changeEngine.ts
```

**Implementation notes:**
- `fetchPreviousCycleSnapshots(cycleId - 1)` returns a Map<symbol, Snapshot>.
- If a symbol is in the watchlist but not in the Map: log `[ChangeEngine] Missing snapshot for {symbol} in cycle {cycleId-1} — skipping`.
- Do NOT write a ChangeEvent for missing instruments (they retain their previous MCS in Redis, which will age out).
- Partial data is acceptable; the system degrades gracefully per instrument.

**Acceptance criteria:**
- Missing instrument snapshot: skipped with log, no error, no ChangeEvent.
- Other instruments computed normally.

**Testing:**
- Integration: omit one instrument from cycle snapshots; run ChangeEngine; verify ChangeEvents for others are written and the missing one is logged.

---

### TASK-099

**Title:** Write ChangeEvents to DB  
**Epic:** Meaningful Change Engine  
**Priority:** P0  

**Description:**  
Batch-insert the computed `ChangeEvent` records into `change_events` table. Use `ON CONFLICT (instrument_symbol, cycle_id) DO NOTHING` for idempotency.

**Dependencies:** TASK-096, TASK-028

**Files likely affected:**
```
worker/src/repositories/changeEventRepository.ts
```

**Implementation notes:**
- Batch insert all events for a cycle in one SQL call.
- Store: `instrument_symbol`, `cycle_id`, `vapm`, `srm`, `va`, `mcs`, `explanation_template`, `explanation_params` (JSONB), `computed_at`.
- `explanation_template` and `explanation_params` are generated by the Explanation Engine (TASK-116) before this write.

**Acceptance criteria:**
- All computed events written in one DB call.
- Idempotent: calling twice with same cycle_id does not error.
- `explanation_params` is stored as JSONB.

**Testing:**
- Insert events; verify row count matches.
- Insert same events again; verify idempotent.

---

### TASK-100

**Title:** Update MCS in Redis cache  
**Epic:** Meaningful Change Engine  
**Priority:** P0  

**Description:**  
After writing ChangeEvents to DB, update Redis with the latest MCS and signal values for each instrument (`mcs:{symbol}`). TTL: 120 seconds.

**Dependencies:** TASK-099, TASK-040

**Files likely affected:**
```
worker/src/cache/mcsCache.ts
```

**Implementation notes:**
- Key: `mcs:{symbol}`.
- Value: JSON `{mcs, vapm, srm, va, vapmSignal, srmSignal, vaSignal, computedAt, cycleId}`.
- Write all instrument MCS values in a Redis pipeline (single roundtrip).
- TTL: 120s. If ChangeEngine stops running (e.g., crash), keys expire and DigestService falls back to DB.

**Acceptance criteria:**
- `redis-cli GET mcs:HDFCBANK` returns valid JSON after a cycle.
- TTL is 120 seconds.
- Pipeline write for all instruments in one roundtrip.

**Testing:**
- Run a cycle; verify Redis MCS values for seeded instruments.

---

### TASK-101

**Title:** ChangeEngine reads cycle_id - 1 (consistent read window)  
**Epic:** Meaningful Change Engine  
**Priority:** P0  

**Description:**  
Verify and test the concurrency design: the ChangeEngine reads `cycle_id - 1` (the previous completed cycle), not the currently-writing `cycle_id`. This guarantees a consistent read window even if the current cycle's DB writes are not yet complete.

**Dependencies:** TASK-082, TASK-100

**Files likely affected:**
```
worker/src/changeEngine/changeEngine.ts
```

**Implementation notes:**
- `runChangeEngine(currentCycleId: number)` reads snapshots where `cycle_id = currentCycleId - 1`.
- This is a ~60s lag in MCS updates: acceptable per the trade-off in DESIGN.md §31.
- Test: write cycle 5 snapshots, trigger ChangeEngine with cycleId=6 → reads cycle 5.
- Test: trigger ChangeEngine with cycleId=1 → no snapshots (cycle 0 doesn't exist) → no events written, no error.

**Acceptance criteria:**
- ChangeEngine always reads cycle N-1, never cycle N.
- First cycle (cycleId=1) reads cycle 0 gracefully (no rows → no computation).

**Testing:**
- Integration: write cycle 5, trigger engine with 6, verify events reference cycle 5 data.
- Edge: trigger engine with cycleId=1; verify no error.

---

## EPIC 10 — Explanation Engine

---

### TASK-110

**Title:** Explanation template library  
**Epic:** Explanation Engine  
**Priority:** P0  

**Description:**  
Define all explanation templates from DESIGN.md §14 as a typed template registry. Each template has an ID, parameter schema, and a render function.

**Dependencies:** TASK-091

**Files likely affected:**
```
worker/src/explanations/templates.ts
```

**Implementation notes:**
Template IDs:
- `VAPM_ROSE`: `{name} rose {delta_pct}% — larger than its typical daily move of +/-{atr_pct}%.`
- `VAPM_FELL`: `{name} fell {delta_pct}% — larger than its typical daily move of +/-{atr_pct}%.`
- `SRM_OUTPERFORMED`: `{name} rose {delta_pct}% while {sector} moved {sector_pct}% — a {srm}pp divergence.`
- `SRM_UNDERPERFORMED`: `{name} fell {delta_pct}% while {sector} moved {sector_pct}% — a {srm}pp divergence.`
- `VA_PRICE_ROSE`: `{name} rose {delta_pct}% on volume {va_x}x higher than its 20-day average.`
- `VA_PRICE_FELL`: `{name} fell {delta_pct}% on volume {va_x}x higher than its 20-day average.`
- `VA_FLAT`: `{name} saw {va_x}x its typical volume with little price change — unusual for this stock.`
- `COMBINED`: `{name} {rose/fell} {delta_pct}% on {va_x}x typical volume — sector {sector} moved only {sector_pct}%.`

Each template's render function accepts params and returns a formatted string.

**Acceptance criteria:**
- All 8 template IDs are defined.
- Each template renders correctly with given params.
- Template render functions are pure (no side effects).

**Testing:**
- Unit: render each template with sample params; verify output string.

---

### TASK-111

**Title:** Primary signal selector  
**Epic:** Explanation Engine  
**Priority:** P0  

**Description:**  
Implement the logic that selects which signal is the "primary" driver of the explanation (the one with the highest weighted contribution), and whether a second signal should be appended as context.

**Dependencies:** TASK-110

**Files likely affected:**
```
worker/src/explanations/signalSelector.ts
```

**Implementation notes:**
Rules from DESIGN.md §14:
1. Primary signal = the signal with the highest weighted contribution (`w * signal_value`).
2. If a second signal also exceeds its floor (signal value > 0): eligible for context.
3. Never append more than one context signal.
4. If only one signal fires: no context appended.
```typescript
function selectSignals(signals: SignalOutputs): {
  primary: 'VAPM' | 'SRM' | 'VA';
  secondary: 'VAPM' | 'SRM' | 'VA' | null;
}
```

**Acceptance criteria:**
- VAPM_signal=1.3 (w=0.5 → 0.65), SRM_signal=1.7 (w=0.35 → 0.595) → primary=VAPM.
- Only VAPM fires → secondary=null.
- Two signals fire → secondary is the second-highest.

**Testing:**
- Unit: all combinations of firing/non-firing signals.

---

### TASK-112

**Title:** VAPM-primary explanation builder  
**Epic:** Explanation Engine  
**Priority:** P0  

**Description:**  
Implement the explanation builder function for cases where VAPM is the primary signal.

**Dependencies:** TASK-111

**Files likely affected:**
```
worker/src/explanations/builders/vapmBuilder.ts
```

**Implementation notes:**
- Select `VAPM_ROSE` or `VAPM_FELL` based on direction of price change.
- Params: `name`, `delta_pct` (2dp), `atr_pct` (2dp).
- Returns `{templateId, params}` (not the rendered string — rendering happens at API time from stored params).

**Acceptance criteria:**
- Stock rose: template = `VAPM_ROSE` with correct params.
- Stock fell: template = `VAPM_FELL` with correct params.
- Params match the rendered template variables.

**Testing:**
- Unit: rose and fell cases.

---

### TASK-113

**Title:** SRM-primary explanation builder  
**Epic:** Explanation Engine  
**Priority:** P0  

**Description:**  
Implement the explanation builder for SRM-primary cases.

**Dependencies:** TASK-111

**Files likely affected:**
```
worker/src/explanations/builders/srmBuilder.ts
```

**Implementation notes:**
- Select `SRM_OUTPERFORMED` (stock rose more / fell less than sector) or `SRM_UNDERPERFORMED` (stock fell more / rose less than sector).
- Params: `name`, `delta_pct`, `sector` (sector name), `sector_pct`, `srm` (2dp).

**Acceptance criteria:**
- Stock +4%, sector +1% → `SRM_OUTPERFORMED`.
- Stock -4%, sector -1% → `SRM_UNDERPERFORMED`.

**Testing:**
- Unit: outperform and underperform cases.

---

### TASK-114

**Title:** VA-primary explanation builder  
**Epic:** Explanation Engine  
**Priority:** P0  

**Description:**  
Implement the explanation builder for VA-primary cases. Handles three sub-cases: volume spike with price rise, volume spike with price fall, volume spike with flat price.

**Dependencies:** TASK-111

**Files likely affected:**
```
worker/src/explanations/builders/vaBuilder.ts
```

**Implementation notes:**
- "Flat" price: `|delta_pct| < 0.5%` (configurable threshold).
- Params: `name`, `delta_pct`, `va_x` (1dp, e.g., "3.1x").

**Acceptance criteria:**
- Volume spike + price rise → `VA_PRICE_ROSE`.
- Volume spike + price fall → `VA_PRICE_FELL`.
- Volume spike + flat price → `VA_FLAT`.

**Testing:**
- Unit: all three sub-cases.

---

### TASK-115

**Title:** Combined-signal explanation builder  
**Epic:** Explanation Engine  
**Priority:** P0  

**Description:**  
Implement the combined explanation builder for cases where two signals fire. Combines the primary explanation with a secondary context clause.

**Dependencies:** TASK-112, TASK-113, TASK-114

**Files likely affected:**
```
worker/src/explanations/builders/combinedBuilder.ts
```

**Implementation notes:**
- Uses the `COMBINED` template or appends context to the primary template's output.
- The design (DESIGN.md §14) specifies: "If a second signal also exceeds its floor, append it as context."
- The combined template: `{name} {rose/fell} {delta_pct}% on {va_x}x typical volume — sector {sector} moved only {sector_pct}%.`
- Only used when VA and SRM are both firing (the most common multi-signal case).
- VAPM + VA combination: use VAPM as lead, append volume context.

**Acceptance criteria:**
- Two signals firing → explanation uses combined template.
- Three signals firing → use the two highest contributors; ignore the third.

**Testing:**
- Unit: VAPM+SRM, VAPM+VA, SRM+VA combinations.

---

### TASK-116

**Title:** Explanation guard rules  
**Epic:** Explanation Engine  
**Priority:** P0  

**Description:**  
Implement a validation layer that checks every generated explanation against the rules from DESIGN.md §14: no forward-looking language, no investment language. This is a defence-in-depth check.

**Dependencies:** TASK-112, TASK-113, TASK-114, TASK-115

**Files likely affected:**
```
worker/src/explanations/guards.ts
```

**Implementation notes:**
Banned words/phrases (case-insensitive):
- Forward-looking: `may`, `could`, `expected to`, `will`, `might`, `likely to`
- Investment: `buy`, `sell`, `opportunity`, `risk`, `invest`, `recommend`

If an explanation contains a banned phrase: log an error and substitute a safe fallback:
`"{name} moved {delta_pct}% since you last checked."`

Note: Since templates are deterministic and pre-audited, this guard should never trigger in practice. It is a safety net for future template additions.

**Acceptance criteria:**
- Generated explanations pass the guard without substitution.
- A test explanation containing "may rise" triggers substitution and logs an error.

**Testing:**
- Unit: pass in each template rendered; verify no guard triggered.
- Unit: inject a banned phrase; verify fallback is substituted.

---

## EPIC 11 — Last-Seen State

---

### TASK-120

**Title:** UserWatchlistSession repository  
**Epic:** Last-Seen State  
**Priority:** P0  

**Description:**  
Implement the data access layer for `user_watchlist_sessions`. Functions: `getSession`, `createSession`, `updateLastCheckedAt`, `upsertSession`.

**Dependencies:** TASK-025

**Files likely affected:**
```
backend/src/repositories/sessionRepository.ts
```

**Implementation notes:**
- `getSession(userId, watchlistId)`: returns session or null.
- `upsertSession(userId, watchlistId)`: creates session with null `last_checked_at` if not exists; returns existing if present.
- `updateLastCheckedAt(userId, watchlistId, newTime)`: uses the advance-only SQL guard (TASK-122).

**Acceptance criteria:**
- `upsertSession` is idempotent.
- `updateLastCheckedAt` with an older timestamp than current: no-op.

**Testing:**
- Unit: each function with test DB.

---

### TASK-121

**Title:** Baseline snapshot anchor lookup  
**Epic:** Last-Seen State  
**Priority:** P0  

**Description:**  
Implement the function that resolves a user's `last_checked_at` timestamp to a specific PriceSnapshot (the "baseline"). Returns the latest snapshot at or before the timestamp.

**Dependencies:** TASK-026, TASK-120

**Files likely affected:**
```
backend/src/services/baselineService.ts
```

**Implementation notes:**
```sql
SELECT * FROM price_snapshots
WHERE instrument_symbol = $symbol
  AND snapshot_at <= $lastCheckedAt
ORDER BY snapshot_at DESC
LIMIT 1;
```
- If no snapshot exists before `lastCheckedAt` (first ever visit): fall back to the snapshot closest to the previous market close (via `getLastMarketClose()`).
- If `last_checked_at` is null (NEVER_CHECKED): baseline = market open of current day (or last close if pre-market).
- 30-day cap: if `last_checked_at` is > 30 days ago, cap to 30 days ago.

**Acceptance criteria:**
- Returns the correct snapshot for a given timestamp.
- Returns the last-close snapshot if no snapshot exists before the timestamp.
- Handles null `last_checked_at` (NEVER_CHECKED) correctly.

**Testing:**
- Unit: timestamp between two snapshots → returns the earlier one.
- Unit: timestamp before any snapshot → falls back to last close.
- Unit: null last_checked_at → returns market-open baseline.

---

### TASK-122

**Title:** Optimistic last_checked_at update (advance-only SQL)  
**Epic:** Last-Seen State  
**Priority:** P0  

**Description:**  
Implement the SQL update that advances `last_checked_at` without ever rewinding it. Uses the `AND last_checked_at < $new_time` guard from DESIGN.md §21.

**Dependencies:** TASK-120

**Files likely affected:**
```
backend/src/repositories/sessionRepository.ts
```

**Implementation notes:**
```sql
UPDATE user_watchlist_sessions
SET last_checked_at = $newTime,
    updated_at = NOW()
WHERE user_id = $userId
  AND watchlist_id = $watchlistId
  AND (last_checked_at IS NULL OR last_checked_at < $newTime)
RETURNING last_checked_at;
```
- If 0 rows updated (the new timestamp was not newer): return the existing `last_checked_at`.
- This is safe for concurrent multi-device access without locks.

**Acceptance criteria:**
- Advancing the timestamp: 1 row updated.
- Sending an older timestamp: 0 rows updated; existing timestamp preserved.
- Concurrent updates: both may succeed, but the result is always the largest value.

**Testing:**
- Unit: advance case, rewind case.
- Concurrent test: two threads update simultaneously; verify final value is the max.

---

### TASK-123

**Title:** Dwell-time update logic (30-second threshold)  
**Epic:** Last-Seen State  
**Priority:** P0  

**Description:**  
Implement the dwell-time checkpoint update. The API must NOT update `last_checked_at` on the instant the user opens the watchlist. Instead, the frontend sends a dwell-time heartbeat after 30 seconds. This task defines the API endpoint and handler for that heartbeat.

**Dependencies:** TASK-122

**Files likely affected:**
```
backend/src/routes/digest.ts
```

**Implementation notes:**
- The frontend timer (TASK-226) fires after 30s and calls `GET /v1/watchlists/{id}/digest?acknowledge=true`.
- The `acknowledge=true` query parameter triggers `updateLastCheckedAt(userId, watchlistId, NOW())`.
- This is the same endpoint used for explicit dismiss (TASK-134). Both use acknowledge=true.
- Server-side: no special 30s logic; the dwell timer is entirely a frontend concern.

**Acceptance criteria:**
- `GET /digest?acknowledge=true` updates `last_checked_at` to NOW().
- `GET /digest` (no acknowledge) does NOT update `last_checked_at`.

**Testing:**
- Integration: two requests — without and with acknowledge; verify state changes only for the latter.

---

### TASK-124

**Title:** NEVER_CHECKED first-visit state handling  
**Epic:** Last-Seen State  
**Priority:** P0  

**Description:**  
Handle the case where a user has never checked their watchlist (`last_checked_at = NULL`). Set the baseline to "market open today" (or "last close" if pre-market).

**Dependencies:** TASK-121, TASK-074

**Files likely affected:**
```
backend/src/services/baselineService.ts
```

**Implementation notes:**
- If `last_checked_at IS NULL`:
  - If market is currently open: baseline = snapshot closest to today's market open (09:15 IST).
  - If market is closed / pre-market: baseline = last close snapshot.
- The digest window label for this state: `"Since market open today"` or `"Since market close"`.
- Surface instruments that changed since the baseline — giving a useful first-visit digest.

**Acceptance criteria:**
- NEVER_CHECKED user gets a meaningful digest from market open (not an empty digest).
- Correct window label in digest response.

**Testing:**
- Integration: create watchlist, immediately request digest; verify `last_checked_at` was null, baseline is market open.

---

### TASK-125

**Title:** 30-day cap on baseline lookup  
**Epic:** Last-Seen State  
**Priority:** P0  

**Description:**  
If the user's `last_checked_at` is more than 30 days ago, cap it to 30 days ago (data retention limit). Include a notice in the digest: `"Showing changes over the past 30 days."`.

**Dependencies:** TASK-121

**Files likely affected:**
```
backend/src/services/baselineService.ts
backend/src/routes/digest.ts
```

**Implementation notes:**
- Computed before baseline snapshot lookup: `effectiveLast = max(lastCheckedAt, NOW() - 30d)`.
- If capped: set `digest.window_capped = true` and `digest.window_notice = "Showing changes over the past 30 days."`.

**Acceptance criteria:**
- User with `last_checked_at = 60 days ago`: baseline = 30 days ago.
- Digest response includes `window_notice`.

**Testing:**
- Integration: set `last_checked_at` to 60 days ago; verify effective baseline is 30 days ago.

---

### TASK-126

**Title:** Market-hours boundary baseline normalization  
**Epic:** Last-Seen State  
**Priority:** P0  

**Description:**  
Handle the boundary case where a user checked during market hours on Friday and returns on Monday. The baseline must be Friday's closing snapshot — not a snapshot from between market sessions.

**Dependencies:** TASK-121, TASK-074

**Files likely affected:**
```
backend/src/services/baselineService.ts
```

**Implementation notes:**
- After computing `effectiveLast`, check: is `effectiveLast` between two market sessions (post-close Friday / pre-open Monday)?
- If so: snap the baseline to the last market close snapshot before `effectiveLast`.
- This prevents spurious signals from after-hours or pre-market data that users already saw.
- Use `getLastMarketClose(effectiveLast)` from TASK-074.

**Acceptance criteria:**
- User checked Friday 15:00 IST (market open), returns Monday 09:30 IST: baseline = Friday 15:30 (close).
- User checked Friday 17:00 IST (post-close), returns Monday 09:30 IST: baseline = Friday 15:30 (close).

**Testing:**
- Unit: Friday 15:00 input → Friday 15:30 close snapshot.
- Unit: Friday 17:00 input → Friday 15:30 close snapshot.
- Unit: Monday 10:00 input (same session) → Monday 10:00 snapshot (no change).

---

### TASK-127

**Title:** Cross-session last_checked_at reconciliation  
**Epic:** Last-Seen State  
**Priority:** P0  

**Description:**  
Ensure the server-authoritative `last_checked_at` is correctly read and used regardless of which device the user last dismissed from. Verify the advance-only semantics handle multi-device scenarios correctly.

**Dependencies:** TASK-122

**Files likely affected:**
```
backend/src/routes/digest.ts
```

**Implementation notes:**
- The server always reads `last_checked_at` from `user_watchlist_sessions` (not from a client-supplied value).
- On dismiss from Mobile: UPDATE with NOW(). 
- Web session opens next: reads the server's `last_checked_at` (which is now the mobile dismiss time).
- Two devices dismiss simultaneously: advance-only SQL ensures the larger timestamp wins.

**Acceptance criteria:**
- After mobile dismiss, web session correctly uses mobile's `last_checked_at` as baseline.
- Simultaneous dismisses from two devices do not cause errors.

**Testing:**
- Concurrent dismiss test: two parallel `acknowledge=true` requests; verify final timestamp is the later of the two.

---

## EPIC 12 — Digest API

---

### TASK-130

**Title:** DigestService scaffold  
**Epic:** Digest API  
**Priority:** P0  

**Description:**  
Create the `DigestService` class that orchestrates digest assembly: reads session state, fetches MCS from Redis, ranks instruments, generates explanations, and builds the final response.

**Dependencies:** TASK-100, TASK-120, TASK-116

**Files likely affected:**
```
backend/src/services/digestService.ts
backend/src/routes/digest.ts
```

**Implementation notes:**
- `DigestService.buildDigest(userId, watchlistId): Promise<DigestResponse>`.
- Injected dependencies: `sessionRepository`, `redis`, `db`.
- This service does NOT recompute signals (those are pre-computed by ChangeEngine). It reads Redis/DB.
- Separates business logic from HTTP routing.

**Acceptance criteria:**
- `buildDigest()` returns a typed `DigestResponse`.
- Service is instantiated once and injected into the route handler.

**Testing:**
- Unit: mock Redis and DB; verify correct digest assembly.

---

### TASK-131

**Title:** Build ranked digest from Redis MCS and prices  
**Epic:** Digest API  
**Priority:** P0  

**Description:**  
Implement the core digest assembly: for each instrument in the watchlist, read `mcs:{symbol}` and `price:{symbol}` from Redis. Fall back to DB if Redis misses.

**Dependencies:** TASK-130

**Files likely affected:**
```
backend/src/services/digestService.ts
```

**Implementation notes:**
- Fetch all instrument symbols for the watchlist (DB).
- Batch read from Redis using `MGET` (single roundtrip).
- For each symbol: if Redis hit → use cached value; if miss → query DB for latest ChangeEvent and PriceSnapshot.
- Aggregate per-instrument data: `{symbol, price, delta_pct, mcs, signals, explanation}`.

**Acceptance criteria:**
- Digest assembled for a 10-instrument watchlist in a single Redis MGET call.
- DB fallback works when Redis is empty.

**Testing:**
- Unit: Redis hit scenario.
- Unit: Redis miss → DB fallback scenario.

---

### TASK-132

**Title:** Filter and rank instruments by MCS  
**Epic:** Digest API  
**Priority:** P0  

**Description:**  
After assembling per-instrument data, split into `items` (MCS > 0, ranked descending) and count of no-change instruments. Implement tie-breaking by absolute price change.

**Dependencies:** TASK-131

**Files likely affected:**
```
backend/src/services/digestService.ts
```

**Implementation notes:**
- Filter: `MCS > 0` → digest items; `MCS = 0` → counted as `no_change_items_count`.
- Sort: descending MCS. Ties: by `|delta_pct|` descending.
- No cap on digest size (per DESIGN.md §20: extreme market events should surface all stocks that moved).

**Acceptance criteria:**
- Only instruments with MCS > 0 appear in `items`.
- Items are sorted by MCS descending.
- `no_change_items_count` is accurate.

**Testing:**
- Unit: 5 instruments with various MCS values; verify ranking and filtering.

---

### TASK-133

**Title:** Attach benchmark (Nifty 50) to digest response  
**Epic:** Digest API  
**Priority:** P0  

**Description:**  
Include the Nifty 50 return over the same window (since `last_checked_at`) in every digest response. Read from Redis or `sector_snapshots` table.

**Dependencies:** TASK-132, TASK-085

**Files likely affected:**
```
backend/src/services/digestService.ts
```

**Implementation notes:**
- Read `price:NIFTY50` from Redis (the sector snapshot written by MarketWorker).
- Compute delta vs the baseline snapshot of `NIFTY50` at `last_checked_at`.
- Include in response:
  ```json
  "benchmark": {
    "symbol": "NIFTY50",
    "change_pct": 0.42,
    "label": "Nifty 50 +0.42%"
  }
  ```
- If NIFTY50 data unavailable: include `null` benchmark (do not fail the digest).

**Acceptance criteria:**
- Benchmark is included in every digest response.
- Unavailable benchmark → `null` benchmark, no error.
- Change_pct is computed over the correct window (since last_checked_at).

**Testing:**
- Unit: verify benchmark computation from fixture data.
- Unit: missing NIFTY50 data → null benchmark.

---

### TASK-134

**Title:** Digest acknowledge endpoint  
**Epic:** Digest API  
**Priority:** P0  

**Description:**  
Implement `GET /v1/watchlists/{watchlist_id}/digest?acknowledge=true`. When `acknowledge=true`, update `last_checked_at` to NOW() using the advance-only update. Return the updated `last_checked_at` in the response.

**Dependencies:** TASK-130, TASK-122

**Files likely affected:**
```
backend/src/routes/digest.ts
```

**Implementation notes:**
- Read `acknowledge` from query params.
- If `acknowledge=true`: call `updateLastCheckedAt(userId, watchlistId, NOW())`.
- Always build and return the full digest (the acknowledge is a side-effect, not a different response shape).
- The updated `last_checked_at` is reflected in the returned `digest.last_checked_at` field.

**Acceptance criteria:**
- `GET /digest?acknowledge=true`: updates `last_checked_at` AND returns the digest.
- `GET /digest` (no acknowledge): does NOT update `last_checked_at`.

**Testing:**
- Integration: call without acknowledge, verify no DB change. Call with acknowledge, verify DB updated.

---

### TASK-135

**Title:** Data freshness label computation  
**Epic:** Digest API  
**Priority:** P0  

**Description:**  
Implement the function that computes the data freshness label based on the age of the most recent snapshot. Returns the label string and `data_as_of` timestamp.

**Dependencies:** TASK-131

**Files likely affected:**
```
backend/src/services/freshnessService.ts
```

**Implementation notes:**
From DESIGN.md §18:
```
snapshot_age < 90s          → "live"
snapshot_age 90s – 5 min    → "~{N} min delayed"
snapshot_age > 5 min,       → "delayed — last updated HH:MM"
  market open
market closed               → "market closed — last updated HH:MM IST"
no data available           → "data unavailable — showing cached prices from HH:MM"
```
- `snapshot_age = NOW() - max(snapshot_at across all instruments)`.
- Use `getLastMarketClose()` from TASK-074 to determine if market is closed.

**Acceptance criteria:**
- Snapshot 30s old → `"live"`.
- Snapshot 3 min old → `"~3 min delayed"`.
- Snapshot 10 min old, market open → `"delayed — last updated HH:MM"`.
- Market closed → `"market closed — last updated HH:MM IST"`.

**Testing:**
- Unit: each freshness condition with mocked clock.

---

### TASK-136

**Title:** Graceful degradation: serve stale digest with banner  
**Epic:** Digest API  
**Priority:** P0  

**Description:**  
When all market data is stale (provider down), serve the last cached prices with a `data_freshness: "unavailable"` label. Do NOT surface new ChangeEvents (since they would be computed from stale data). Surface the previously computed digest with a staleness notice.

**Dependencies:** TASK-135, TASK-131

**Files likely affected:**
```
backend/src/services/digestService.ts
backend/src/services/freshnessService.ts
```

**Implementation notes:**
- If all price cache keys are expired from Redis AND the latest DB snapshot is > 5 minutes old: set `data_freshness = "stale"`.
- When stale: use the most recent DB snapshot (cached price from `data_as_of`).
- Include in response: `"data_freshness": "unavailable", "data_as_of": "<last_snapshot_at>"`.
- Do NOT recompute or filter by new MCS — serve the previously stored `ChangeEvents`.

**Acceptance criteria:**
- Provider down for 10 minutes: response includes `data_freshness: "unavailable"` and cached prices.
- No new items appear in digest during provider outage.
- Frontend can detect stale state and show banner.

**Testing:**
- Integration: bring down mock provider; verify stale response shape.

---

### TASK-137

**Title:** No-change digest response (empty digest state)  
**Epic:** Digest API  
**Priority:** P0  

**Description:**  
When all instruments in the watchlist have MCS = 0 (no meaningful changes), return a digest with empty `items` array and `no_change_items_count = N`. The `digest_window_label` and `benchmark` are still included.

**Dependencies:** TASK-132

**Files likely affected:**
```
backend/src/services/digestService.ts
```

**Implementation notes:**
- This is a valid successful response (200 OK), not an error.
- Response shape: `"items": [], "no_change_items_count": 15`.
- The frontend (TASK-224) renders the calm "Nothing significant changed since X" state.

**Acceptance criteria:**
- All instruments MCS=0: `items` is empty array.
- `no_change_items_count` reflects the correct count.
- Response is 200 OK (not 204).

**Testing:**
- Integration: seed instruments with all-zero MCS; verify digest response.

---

### TASK-138

**Title:** Instrument added after last_checked_at — skip note  
**Epic:** Digest API  
**Priority:** P0  

**Description:**  
If a stock was added to the watchlist after the user's `last_checked_at`, there is no baseline snapshot for it. Include it in the digest with a special `status: "added_since_last_check"` note; do not compute MCS for it.

**Dependencies:** TASK-131

**Files likely affected:**
```
backend/src/services/digestService.ts
```

**Implementation notes:**
- Check: `watchlist_instruments.added_at > user.last_checked_at` for each instrument.
- If true: include in the digest items with:
  - `mcs: null`
  - `explanation: "Added to your watchlist since your last visit."`
  - `status: "added_since_last_check"`
- These appear at the bottom of the digest (below MCS-ranked items) or in a separate section.

**Acceptance criteria:**
- Instrument added after last_checked_at: appears in digest with correct status and note.
- Its MCS is null (not zero).
- It does not interfere with ranking of other items.

**Testing:**
- Integration: add an instrument after setting last_checked_at; verify digest note.

---

## EPIC 13 — Data Freshness & Stale Handling

---

### TASK-140

**Title:** Data freshness label rules (full rule set)  
**Epic:** Data Freshness & Stale Handling  
**Priority:** P0  

**Description:**  
Consolidate and verify all freshness label rules are correctly implemented in `freshnessService.ts`. This is a review/test task for TASK-135.

**Dependencies:** TASK-135

**Files likely affected:**
```
backend/src/services/freshnessService.ts
```

**Implementation notes:**
- All five conditions from DESIGN.md §18 are covered.
- "Live" label: age < 90s.
- Edge: age exactly 90s → "~1 min delayed".
- Edge: market closed but recent (e.g., 5 min after close) → "market closed" label, not "delayed".

**Acceptance criteria:**
- All five label conditions produce the correct string.
- Edge cases at boundary values are correct.

**Testing:**
- Parametrized unit tests: age=89s, 90s, 150s, 300s, 301s, market-closed scenarios.

---

### TASK-141

**Title:** Stale data detection in API response envelope  
**Epic:** Data Freshness & Stale Handling  
**Priority:** P0  

**Description:**  
Every API response that includes market data must include `data_freshness` and `data_as_of` fields. Implement this as a shared utility that the WatchlistService and DigestService both use.

**Dependencies:** TASK-140

**Files likely affected:**
```
backend/src/services/freshnessService.ts
backend/src/services/watchlistService.ts
backend/src/services/digestService.ts
```

**Acceptance criteria:**
- `GET /watchlists/{id}` response includes `data_freshness` and `data_as_of`.
- `GET /watchlists/{id}/digest` response includes `data_freshness` and `data_as_of`.

**Testing:**
- Integration: both endpoints return freshness fields.

---

### TASK-142

**Title:** Partial data handling (some symbols missing from provider response)  
**Epic:** Data Freshness & Stale Handling  
**Priority:** P1  

**Description:**  
When the market data provider returns quotes for only a subset of tracked instruments (partial response), handle each instrument individually: missing instruments retain their last cached price with `data_status: "stale"`.

**Dependencies:** TASK-141, TASK-083

**Files likely affected:**
```
worker/src/worker.ts
backend/src/services/watchlistService.ts
```

**Implementation notes:**
- Worker: instruments not in the provider response are not written to DB for this cycle. Their Redis keys age out.
- API: for each instrument, if Redis key expired and DB has no recent snapshot: mark `data_status: "stale"`.
- Individual `data_status` per instrument (not a global flag).

**Acceptance criteria:**
- Missing instrument: `data_status: "stale"` in watchlist response.
- Present instruments: `data_status: "live"`.
- Partial response does not cause errors.

**Testing:**
- Integration: mock provider returns only half the symbols; verify watchlist response has mixed data_status.

---

### TASK-143

**Title:** Suspended/delisted instrument label  
**Epic:** Data Freshness & Stale Handling  
**Priority:** P1  

**Description:**  
When an instrument in a watchlist has `status = 'SUSPENDED'` or `'DELISTED'` in the instruments table, include it in the watchlist response with `data_status: "suspended"` or `"delisted"` and exclude it from change detection.

**Dependencies:** TASK-054

**Files likely affected:**
```
backend/src/services/watchlistService.ts
backend/src/services/digestService.ts
```

**Implementation notes:**
- Watchlist detail: include suspended/delisted instruments with their status label.
- Digest: exclude them from MCS ranking and digest items entirely.
- Show a label: "Trading suspended — last price: ₹X".

**Acceptance criteria:**
- Suspended instrument appears in watchlist detail with `data_status: "suspended"`.
- Suspended instrument does not appear in digest items.

**Testing:**
- Seed a suspended instrument; verify it appears in watchlist but not digest.

---

## EPIC 14 — Authentication

---

### TASK-150

**Title:** JWT issuance — login endpoint (RS256)  
**Epic:** Authentication  
**Priority:** P0  

**Description:**  
Implement `POST /v1/auth/login`. Accepts email + password, verifies against `users` table (bcrypt), issues a short-lived JWT (15 minutes) and a long-lived refresh token (7 days).

**Dependencies:** TASK-012, TASK-022

**Files likely affected:**
```
backend/src/routes/auth.ts
backend/src/services/authService.ts
```

**Implementation notes:**
- Verify bcrypt hash. On success: issue JWT with claims `{userId, sessionId, exp}` signed with RS256 private key.
- Refresh token: UUID, stored in `refresh_tokens` table (or a simple in-memory store for hackathon) with expiry.
- On failure: 401 with `invalid-credentials` error type. Same error for both bad email and bad password (do not distinguish — prevents enumeration).
- Rate limit the login endpoint: 5 attempts/minute per IP.

**Acceptance criteria:**
- Valid credentials → 200 with `{accessToken, refreshToken, expiresIn}`.
- Invalid password → 401 `invalid-credentials`.
- Non-existent email → 401 `invalid-credentials` (same message).

**Testing:**
- Unit: valid, invalid password, non-existent user.
- Integration: JWT can be used to call a protected endpoint.

---

### TASK-151

**Title:** Refresh token rotation  
**Epic:** Authentication  
**Priority:** P1  

**Description:**  
Implement `POST /v1/auth/refresh`. Accepts a refresh token, validates it (single-use, not expired), issues a new access token + new refresh token, invalidates the old refresh token.

**Dependencies:** TASK-150

**Files likely affected:**
```
backend/src/routes/auth.ts
backend/src/services/authService.ts
```

**Implementation notes:**
- Refresh token is single-use: on use, mark as consumed and issue a new one.
- Storing refresh tokens: a `refresh_tokens` table or Redis set (Redis is simpler for hackathon).
- Reuse of a consumed refresh token → 401 + revoke all tokens for that user (suspected theft).

**Acceptance criteria:**
- Valid refresh token → new access token + new refresh token.
- Reused refresh token → 401 and all tokens revoked.
- Expired refresh token → 401.

**Testing:**
- Unit: valid use, double use (reuse), expired.

---

### TASK-152

**Title:** User registration endpoint  
**Epic:** Authentication  
**Priority:** P0  

**Description:**  
Implement `POST /v1/auth/register`. Accepts email, name, password. Validates input, checks for duplicate email, bcrypt-hashes the password, creates the user record, returns the user object (without password hash).

**Dependencies:** TASK-022, TASK-012

**Files likely affected:**
```
backend/src/routes/auth.ts
backend/src/services/authService.ts
```

**Implementation notes:**
- Password: min 8 chars, at least one letter and one digit (configurable rules).
- Email: valid email format.
- Duplicate email: 422 `email-already-registered`.
- Bcrypt rounds: 12.
- On success: create user, create session, return 201 with `{id, email, name, createdAt}`.
- Do NOT auto-login (no JWT issued on registration; user must call `/login` next).

**Acceptance criteria:**
- Valid input → 201 user object.
- Duplicate email → 422.
- Weak password → 400.

**Testing:**
- Integration: happy path, duplicate email, weak password.

---

## EPIC 15 — Observability

---

### TASK-160

**Title:** Prometheus metrics setup (prom-client)  
**Epic:** Observability  
**Priority:** P1  

**Description:**  
Install and configure `prom-client` in the backend. Expose `GET /metrics` for Prometheus scraping (on a separate port or with IP allowlist). Set up default Node.js metrics.

**Dependencies:** TASK-011

**Files likely affected:**
```
backend/src/plugins/metrics.ts
backend/src/routes/metrics.ts
```

**Implementation notes:**
- `prom-client` with default metrics (`collectDefaultMetrics()`).
- Expose on `GET /metrics` (unauthenticated, but restricted to internal network in production).
- For hackathon: expose on same port as API; use `METRICS_ENABLED=true` env gate.
- Register the metrics registry globally so other modules can add metrics.

**Acceptance criteria:**
- `GET /metrics` returns Prometheus text format.
- Default Node.js metrics (event loop, memory, GC) are included.

**Testing:**
- `curl /metrics` returns valid Prometheus format.

---

### TASK-161

**Title:** api_request_duration_seconds histogram  
**Epic:** Observability  
**Priority:** P1  

**Description:**  
Add an `api_request_duration_seconds` histogram that tracks every API request with labels: `endpoint` (route pattern), `method`, `status_code`.

**Dependencies:** TASK-160, TASK-017

**Files likely affected:**
```
backend/src/plugins/metrics.ts
backend/src/hooks/metricsHook.ts
```

**Implementation notes:**
- Use Fastify's `onResponse` hook to record latency.
- Buckets: `[0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5]` seconds.
- Route pattern from `request.routeOptions.url` (not the full URL — avoids high cardinality).

**Acceptance criteria:**
- After 10 requests: `api_request_duration_seconds_bucket` has entries.
- Labels are correct (route pattern, not raw URL).

**Testing:**
- Make requests; check Prometheus output for histogram.

---

### TASK-162

**Title:** MarketWorker metrics (cycle duration, fetch failures)  
**Epic:** Observability  
**Priority:** P1  

**Description:**  
Add metrics in the worker: `market_worker_cycle_duration_seconds` histogram, `market_worker_instruments_fetched_total` counter, `market_worker_fetch_failures_total` counter (with labels: `provider`, `error_type`).

**Dependencies:** TASK-160, TASK-081

**Files likely affected:**
```
worker/src/metrics/workerMetrics.ts
worker/src/worker.ts
```

**Implementation notes:**
- Share the same `prom-client` registry between backend and worker processes by exporting it via a Prometheus push gateway or by running a metrics HTTP server in the worker.
- For hackathon: worker exposes `GET /worker-metrics` on its own port.

**Acceptance criteria:**
- After one cycle: `market_worker_cycle_duration_seconds` has an observation.
- After a provider failure: `market_worker_fetch_failures_total` increments.

**Testing:**
- Run one cycle; check worker metrics endpoint.

---

### TASK-163

**Title:** ChangeEngine metrics (events computed)  
**Epic:** Observability  
**Priority:** P1  

**Description:**  
Add `change_engine_events_computed_total` counter and `watchlist_digest_items_total` histogram (items per digest surfaced).

**Dependencies:** TASK-160, TASK-099

**Files likely affected:**
```
worker/src/metrics/changeEngineMetrics.ts
backend/src/metrics/digestMetrics.ts
```

**Implementation notes:**
- `change_engine_events_computed_total`: incremented by the number of ChangeEvents written per cycle.
- `watchlist_digest_items_total`: histogram in the API, recording item count for each digest request that returns items.

**Acceptance criteria:**
- After a ChangeEngine run: counter increments.
- After a digest request with items: histogram has an observation.

**Testing:**
- Run one cycle; check metrics.

---

### TASK-164

**Title:** price_snapshot_age_seconds gauge  
**Epic:** Observability  
**Priority:** P1  

**Description:**  
Add a `price_snapshot_age_seconds` gauge in the backend that tracks the age of the most recent price snapshot. This triggers alerting if it exceeds 300 seconds during market hours.

**Dependencies:** TASK-160, TASK-084

**Files likely affected:**
```
backend/src/metrics/dataFreshnessMetric.ts
```

**Implementation notes:**
- Updated on every API request that reads price data (or via a background ticker in the backend).
- Value: `NOW() - max(snapshot_at)` across all instruments.
- If market is closed: gauge is still valid but alerts should be suppressed during off-hours.

**Acceptance criteria:**
- `price_snapshot_age_seconds` gauge is present in `/metrics`.
- Value updates as new snapshots arrive.

**Testing:**
- Check gauge before and after a worker cycle; verify value decreases.

---

### TASK-165

**Title:** OpenTelemetry trace propagation  
**Epic:** Observability  
**Priority:** P2  

**Description:**  
Configure OpenTelemetry tracing on the backend. Propagate `trace_id` from API Gateway to WatchlistService → DigestService → DB calls. Include `trace_id` in all error responses and log lines.

**Dependencies:** TASK-017

**Files likely affected:**
```
backend/src/plugins/tracing.ts
backend/src/index.ts           (import tracing before app start)
```

**Implementation notes:**
- `@opentelemetry/sdk-node` with OTLP exporter.
- For hackathon: use console exporter or Jaeger (if available in Docker Compose).
- Propagate W3C `traceparent` header if present in incoming request.
- `trace_id` from OTEL span context must match the one in log lines and error responses.

**Acceptance criteria:**
- Each API request has a `trace_id` in the response error body.
- Log lines for a request share the same `trace_id`.

**Testing:**
- Make a failing request; verify error body has `trace_id`; verify same ID in logs.

---

### TASK-166

**Title:** Structured JSON logging (all components)  
**Epic:** Observability  
**Priority:** P0  

**Description:**  
Verify all log lines across backend and worker use structured JSON with the required fields: `timestamp`, `trace_id`, `user_id` (where applicable), `level`, `message`, `duration_ms`.

**Dependencies:** TASK-017

**Files likely affected:**
```
backend/src/plugins/logging.ts
worker/src/logger.ts
```

**Implementation notes:**
- Worker uses `pino` with the same JSON structure as the backend.
- Key log events (per DESIGN.md §23):
  - Market worker cycle start/complete/failure.
  - ChangeEngine computation start/complete.
  - User opens watchlist.
  - Digest surfaced (with `item_count`, `top_mcs`).
  - Data freshness warning.
- All log lines in production are single-line JSON (no pretty printing).

**Acceptance criteria:**
- Every log line is valid JSON.
- All required fields are present.
- Sensitive fields (passwords, tokens) are redacted.

**Testing:**
- Parse log output as JSON; verify schema.

---

### TASK-167

**Title:** Alert rule definitions  
**Epic:** Observability  
**Priority:** P2  

**Description:**  
Define the Prometheus Alertmanager rules for the five alerts in DESIGN.md §23. For hackathon, these can be YAML config files even if Alertmanager is not running.

**Dependencies:** TASK-160

**Files likely affected:**
```
docker/prometheus/alerts.yml
docs/ALERTS.md
```

**Implementation notes:**
Alert rules:
- `MarketWorkerFailed`: 2+ consecutive cycle failures → P1.
- `PriceDataStale`: `price_snapshot_age_seconds > 300` during market hours → P1.
- `APILatencyHigh`: p99 > 1.5s over 5-min window → P2.
- `ChangeEngineLag`: ChangeEngine not updated in > 5 min during market hours → P1.
- `ErrorRateHigh`: API 5xx rate > 1% over 1-min window → P2.

**Acceptance criteria:**
- Alert YAML is valid Prometheus syntax.
- All 5 alerts from DESIGN.md are defined.

**Testing:**
- `promtool check rules alerts.yml` passes.

---

## EPIC 16 — Demo Mode

---

### TASK-170

**Title:** Demo mode flag and environment switch  
**Epic:** Demo Mode  
**Priority:** P0  

**Description:**  
Implement the `DEMO_MODE=true` environment switch that makes the MarketWorker use `DemoMarketDataProvider` instead of `LiveMarketDataProvider`. Add a `GET /v1/demo/status` endpoint that shows current demo mode and active scenario.

**Dependencies:** TASK-071, TASK-080

**Files likely affected:**
```
worker/src/worker.ts
backend/src/routes/demo.ts
```

**Implementation notes:**
- `DEMO_MODE` env: `"true"` → use DemoMarketDataProvider.
- `GET /v1/demo/status` (unauthenticated for hackathon demo): returns `{demoMode: true, currentScenario: "VAPM_SPIKE"}`.
- Add `POST /v1/demo/advance` to manually advance to the next scenario (for live demo presentations).

**Acceptance criteria:**
- `DEMO_MODE=true` → DemoMarketDataProvider used.
- `GET /v1/demo/status` returns correct scenario info.
- `POST /v1/demo/advance` advances to next scenario.

**Testing:**
- Start in demo mode; verify scenario cycling.

---

### TASK-171

**Title:** Demo scenario: Normal market  
**Epic:** Demo Mode  
**Priority:** P0  

**Description:**  
Implement the NORMAL market scenario data fixture. All instruments have VAPM < 1.5, SRM < 1.5, VA < 2.0. Digest returns `items: []`.

**Dependencies:** TASK-070, TASK-071, TASK-177

**Files likely affected:**
```
worker/src/marketData/demoScenarios.ts
```

**Implementation notes:**
- Instrument quotes: all within 1 ATR, sector returns close to stock returns, volumes at ~1.0x average.
- Expected result: MCS = 0 for all instruments, digest is empty.

**Acceptance criteria:**
- Digest request during NORMAL scenario: `items: []`, `no_change_items_count > 0`.
- Frontend shows "Nothing significant changed" state.

**Testing:**
- Integration: run NORMAL scenario; verify empty digest.

---

### TASK-172

**Title:** Demo scenario: VAPM meaningful price movement  
**Epic:** Demo Mode  
**Priority:** P0  

**Description:**  
Implement the VAPM_SPIKE scenario: one instrument (HDFCBANK) moves 2.8x its ATR. Expect MCS > 0 and VAPM-primary explanation.

**Dependencies:** TASK-071

**Files likely affected:**
```
worker/src/marketData/demoScenarios.ts
```

**Implementation notes:**
- HDFCBANK: current price 3.1% below baseline, ATR14 = 1.1%, so VAPM = 3.1/1.1 = 2.82.
- SRM: HDFCBANK sector (NIFTYBANK) moved -0.4%, stock moved -3.1%, SRM = 2.7.
- Expected MCS = 0.5*(2.82-1.5) + 0.35*(2.7-1.5) = 0.66 + 0.42 = 1.08.
- Explanation: VAPM-primary (since VAPM weighted contribution > SRM weighted contribution).

**Acceptance criteria:**
- Digest shows HDFCBANK with MCS ≈ 1.08.
- Explanation references "larger than its typical daily move".

**Testing:**
- Integration: VAPM_SPIKE scenario; verify digest item and explanation.

---

### TASK-173

**Title:** Demo scenario: Volume anomaly  
**Epic:** Demo Mode  
**Priority:** P0  

**Description:**  
Implement the VOLUME_ANOMALY scenario: INFY shows 3.1x average volume with a modest price change. VA is the primary signal.

**Dependencies:** TASK-071

**Files likely affected:**
```
worker/src/marketData/demoScenarios.ts
```

**Implementation notes:**
- INFY: current volume = 3.1x avg_volume_20d. Price change = +0.8% (below VAPM floor). SRM = 0.4 (below floor).
- VA signal = 3.1 - 2.0 = 1.1. MCS = 0.15 * 1.1 = 0.165.
- Explanation: VA-primary, e.g., "Infosys saw 3.1x its typical volume with a small price change."

**Acceptance criteria:**
- Digest shows INFY with MCS ≈ 0.165 and VA-primary explanation.

**Testing:**
- Integration: VOLUME_ANOMALY scenario; verify explanation references volume.

---

### TASK-174

**Title:** Demo scenario: No meaningful change  
**Epic:** Demo Mode  
**Priority:** P0  

**Description:**  
Implement the NO_CHANGE scenario: all instruments are within normal ranges. Verify the frontend shows the calm "nothing changed" state.

**Dependencies:** TASK-071, TASK-137

**Files likely affected:**
```
worker/src/marketData/demoScenarios.ts
```

**Acceptance criteria:**
- Digest returns `items: []`.
- `no_change_items_count > 0`.
- Frontend shows "Nothing significant changed since X" message.

**Testing:**
- Integration: NO_CHANGE scenario; verify empty digest and correct UI state.

---

### TASK-175

**Title:** Demo scenario: Stale data (provider failure)  
**Epic:** Demo Mode  
**Priority:** P0  

**Description:**  
Implement the STALE_DATA scenario: the provider throws an error. After 3 consecutive failures, the circuit breaker opens. Verify stale-data label appears in API response and frontend.

**Dependencies:** TASK-082, TASK-136

**Files likely affected:**
```
worker/src/marketData/demoScenarios.ts
```

**Acceptance criteria:**
- Provider error → circuit breaker opens after 3rd failure.
- API response includes `data_freshness: "unavailable"`.
- Frontend shows stale data banner.

**Testing:**
- Integration: STALE_DATA scenario × 3 cycles; verify circuit breaker opens and API response.

---

### TASK-176

**Title:** Demo scenario: Market data API failure and recovery  
**Epic:** Demo Mode  
**Priority:** P0  

**Description:**  
Implement the RECOVERY scenario (follows STALE_DATA): provider starts responding again. Circuit breaker transitions HALF_OPEN → CLOSED. Fresh data flows; stale banner disappears.

**Dependencies:** TASK-082, TASK-175

**Files likely affected:**
```
worker/src/marketData/demoScenarios.ts
```

**Acceptance criteria:**
- After STALE_DATA (circuit open), RECOVERY scenario: circuit closes, fresh data flows.
- API response `data_freshness: "live"`.
- Frontend stale banner disappears.

**Testing:**
- Integration: STALE_DATA ×3 then RECOVERY; verify circuit state transitions and API response.

---

### TASK-177

**Title:** Demo seeded user accounts and watchlists  
**Epic:** Demo Mode  
**Priority:** P0  

**Description:**  
Create a seed script for demo mode that creates: one demo user account (email/password), one watchlist ("Tech + Banking"), and adds 8 instruments covering IT and Banking sectors.

**Dependencies:** TASK-031, TASK-022

**Files likely affected:**
```
backend/seeds/demo.ts
```

**Implementation notes:**
- Demo user: `demo@groww.example.com` / `Demo@2026`.
- Watchlist: "Smart Watchlist" with instruments: HDFCBANK, INFY, TCS, RELIANCE, ICICIBANK, WIPRO, AXISBANK, LTIM.
- Script is idempotent: upsert user and watchlist.
- Run with `npm run db:seed:demo`.

**Acceptance criteria:**
- After running seed: demo user exists and can log in.
- Watchlist has 8 instruments.
- Seed is idempotent.

**Testing:**
- Run seed twice; verify no duplicates, user can log in.

---

## EPIC 17 — Frontend Foundation

---

### TASK-200

**Title:** Initialize React + TypeScript frontend (Vite)  
**Epic:** Frontend Foundation  
**Priority:** P0  

**Description:**  
Bootstrap the `frontend` package using Vite + React + TypeScript. Configure build, dev server, and environment variable handling.

**Dependencies:** TASK-001

**Files likely affected:**
```
frontend/
├── index.html
├── vite.config.ts
├── tsconfig.json
├── src/main.tsx
├── src/App.tsx
└── package.json
```

**Implementation notes:**
- `npm create vite@latest frontend -- --template react-ts`.
- `VITE_API_BASE_URL` from `.env` is the API URL.
- Proxy setup in Vite for local dev (API calls to `/api/*` proxied to `http://localhost:3000`).
- `npm run dev` starts at `http://localhost:5173`.

**Acceptance criteria:**
- `npm run dev` starts the dev server.
- `curl http://localhost:5173` returns the React app HTML.

**Testing:**
- Start dev server; open browser; verify app loads.

---

### TASK-201

**Title:** Global design system (tokens, typography, color palette)  
**Epic:** Frontend Foundation  
**Priority:** P0  

**Description:**  
Create the global CSS/design token system. Define: color palette (dark mode, Groww green accent), typography (Google Fonts: Inter), spacing scale, border radii, shadows, and animation curves.

**Dependencies:** TASK-200

**Files likely affected:**
```
frontend/src/styles/globals.css
frontend/src/styles/tokens.css
frontend/src/styles/typography.css
```

**Implementation notes:**
- Dark mode by default (target user is mobile-first, Indian app aesthetic).
- Accent: Groww green `#00D09C` or similar.
- Background: `#0B0E11` (near-black).
- Surface: `#161B22`.
- Text: `#E6EDF3` (primary), `#8B949E` (secondary).
- Positive: `#3FB950`, Negative: `#F85149`.
- Typography: `Inter` from Google Fonts, font sizes from a modular scale.
- Spacing: 4px base unit.
- Animations: `200ms ease-out` for transitions.
- Use CSS custom properties (variables) for all tokens.

**Acceptance criteria:**
- All tokens defined as CSS variables.
- Font loaded from Google Fonts.
- Dark background renders correctly.

**Testing:**
- Visual inspection of the app shell with applied tokens.

---

### TASK-202

**Title:** API client wrapper (Axios/Fetch with JWT injection)  
**Epic:** Frontend Foundation  
**Priority:** P0  

**Description:**  
Create a typed API client that: reads `VITE_API_BASE_URL`, injects the JWT `Authorization` header on every request, handles 401 by triggering refresh token flow, handles RFC-7807 errors with typed error objects.

**Dependencies:** TASK-200

**Files likely affected:**
```
frontend/src/api/client.ts
frontend/src/api/auth.ts
frontend/src/api/watchlists.ts
frontend/src/api/digest.ts
frontend/src/api/instruments.ts
```

**Implementation notes:**
- Use `axios` with interceptors.
- Store JWT in memory (not localStorage — XSS concern for access token). Refresh token in httpOnly cookie (ideal) or localStorage (simpler for hackathon).
- On 401: call refresh token endpoint; on refresh failure: redirect to login.
- Each API module (`watchlists.ts`, `digest.ts`, etc.) exports typed async functions.

**Acceptance criteria:**
- All API calls include `Authorization: Bearer <jwt>`.
- 401 triggers refresh; if refresh fails, redirects to login.
- RFC-7807 errors are returned as typed `ApiError` objects.

**Testing:**
- Unit: axios interceptor with mock 401 → verifies refresh is triggered.

---

### TASK-203

**Title:** Global error boundary  
**Epic:** Frontend Foundation  
**Priority:** P0  

**Description:**  
Implement a React error boundary that catches unhandled React render errors and shows a graceful fallback UI instead of a blank screen.

**Dependencies:** TASK-200

**Files likely affected:**
```
frontend/src/components/ErrorBoundary.tsx
frontend/src/App.tsx
```

**Implementation notes:**
- Wraps the entire app in `<ErrorBoundary>`.
- Fallback: a simple page with "Something went wrong. Please refresh." and a reload button.
- Logs the error to `console.error` (in production, would send to error reporting).

**Acceptance criteria:**
- A component that throws an error during render shows the fallback UI (not a blank screen).

**Testing:**
- Introduce a test throw in a component; verify fallback renders.

---

### TASK-204

**Title:** Authentication flow (login/register screens)  
**Epic:** Frontend Foundation  
**Priority:** P0  

**Description:**  
Implement the login and registration screens. On successful login: store JWT in memory and redirect to the watchlist list. Persist auth state across page refreshes using the refresh token.

**Dependencies:** TASK-202

**Files likely affected:**
```
frontend/src/pages/LoginPage.tsx
frontend/src/pages/RegisterPage.tsx
frontend/src/store/authStore.ts
```

**Implementation notes:**
- Login form: email, password, submit button.
- Register form: name, email, password, confirm password.
- On submit: call `/auth/login` or `/auth/register`.
- Auth state: stored in Zustand or React Context.
- On page load: attempt to refresh token (if refresh token exists); if success, auto-login.
- Protected routes: redirect to login if not authenticated.

**Acceptance criteria:**
- Login with correct credentials → redirect to watchlist list.
- Login with wrong credentials → show error message.
- Page refresh → user remains logged in (via refresh token).

**Testing:**
- Manual: login, refresh, verify session persists.

---

### TASK-205

**Title:** App router and navigation structure  
**Epic:** Frontend Foundation  
**Priority:** P0  

**Description:**  
Set up React Router v6 with routes for: `/login`, `/register`, `/watchlists`, `/watchlists/:id`, `/stocks/:symbol`. Implement a protected route wrapper.

**Dependencies:** TASK-204

**Files likely affected:**
```
frontend/src/router.tsx
frontend/src/components/ProtectedRoute.tsx
frontend/src/App.tsx
```

**Implementation notes:**
- Routes:
  - `/` → redirect to `/watchlists`
  - `/login` → LoginPage
  - `/register` → RegisterPage
  - `/watchlists` → WatchlistListPage (protected)
  - `/watchlists/:id` → WatchlistDetailPage (protected)
  - `/stocks/:symbol` → StockDetailPage (protected)
- `ProtectedRoute`: checks auth state; if not authed, redirect to `/login`.

**Acceptance criteria:**
- Unauthenticated user visiting `/watchlists` is redirected to `/login`.
- After login, navigating to `/watchlists` works.
- Browser back/forward navigation works correctly.

**Testing:**
- Manual: navigate to protected route while logged out; verify redirect.

---

### TASK-206

**Title:** Responsive layout shell  
**Epic:** Frontend Foundation  
**Priority:** P0  

**Description:**  
Create the main app layout shell: top navigation bar, main content area, and mobile-responsive layout. The shell is used by all protected pages.

**Dependencies:** TASK-205, TASK-201

**Files likely affected:**
```
frontend/src/layouts/AppLayout.tsx
frontend/src/components/TopNav.tsx
frontend/src/styles/layout.css
```

**Implementation notes:**
- Top nav: Groww logo (text mark for hackathon), user email/avatar, logout button.
- Content area: centered, max-width 960px, responsive padding.
- Mobile: < 768px — nav collapses to hamburger (or simplified).
- Uses CSS Grid or Flexbox (no Tailwind).

**Acceptance criteria:**
- App renders correctly at 375px (mobile), 768px (tablet), 1280px (desktop).
- Top nav is present on all protected pages.
- Logout clears auth state and redirects to login.

**Testing:**
- Visual inspection at 3 breakpoints.

---

## EPIC 18 — Watchlist UX

---

### TASK-210

**Title:** Watchlist list page  
**Epic:** Watchlist UX  
**Priority:** P0  

**Description:**  
Build the `/watchlists` page showing all user watchlists as cards. Each card shows: watchlist name, instrument count, and a "last updated" indicator.

**Dependencies:** TASK-206

**Files likely affected:**
```
frontend/src/pages/WatchlistListPage.tsx
frontend/src/components/WatchlistCard.tsx
```

**Implementation notes:**
- Loads watchlists from `GET /v1/watchlists`.
- Each card links to `/watchlists/:id`.
- "Create Watchlist" button → opens TASK-211 modal.
- Empty state: "You have no watchlists yet. Create one to get started." (see TASK-217).
- Loading skeleton (TASK-240) shown while fetching.

**Acceptance criteria:**
- All watchlists are displayed as cards.
- Clicking a card navigates to watchlist detail.
- Empty state shows correctly.

**Testing:**
- With 0, 1, 3 watchlists: verify correct rendering.

---

### TASK-211

**Title:** Create watchlist modal  
**Epic:** Watchlist UX  
**Priority:** P0  

**Description:**  
Build the "Create Watchlist" modal with a name input field and submit button. Calls `POST /v1/watchlists` and refreshes the list on success.

**Dependencies:** TASK-210

**Files likely affected:**
```
frontend/src/components/CreateWatchlistModal.tsx
```

**Implementation notes:**
- Name input: max 64 chars, required, real-time character counter.
- Submit: show loading spinner; on success: close modal, show toast notification, update list.
- Error: show inline error message.
- Accessible: focus trap in modal, close on Escape key and overlay click.

**Acceptance criteria:**
- Valid name → watchlist created and appears in list.
- Name > 64 chars → character counter turns red (input is still blocked at 64 via maxLength).
- Empty name submit → validation error shown.

**Testing:**
- Happy path. Empty name. Name exactly 64 chars. Server error response.

---

### TASK-212

**Title:** Delete watchlist confirmation  
**Epic:** Watchlist UX  
**Priority:** P0  

**Description:**  
Implement a confirmation dialog for watchlist deletion. "Delete" button on the watchlist card (or in the detail page header). Shows: "Are you sure? This will remove all stocks from this watchlist."

**Dependencies:** TASK-210

**Files likely affected:**
```
frontend/src/components/DeleteWatchlistDialog.tsx
```

**Implementation notes:**
- Uses a confirmation modal, not a native `confirm()`.
- Delete button: loads while API call is in progress.
- On success: navigate back to `/watchlists`, show toast "Watchlist deleted".
- On error: show error in modal.

**Acceptance criteria:**
- Delete button shows confirmation dialog.
- Confirm → watchlist deleted and removed from list.
- Cancel → no action.

**Testing:**
- Happy path. Cancellation.

---

### TASK-213

**Title:** Watchlist detail page shell  
**Epic:** Watchlist UX  
**Priority:** P0  

**Description:**  
Build the `/watchlists/:id` page shell. This is the primary view: it contains the digest section (above fold) and the instrument list (below fold). Does not yet wire to the API (that's TASK-251).

**Dependencies:** TASK-206

**Files likely affected:**
```
frontend/src/pages/WatchlistDetailPage.tsx
```

**Implementation notes:**
- Layout: watchlist name as heading, digest section (placeholder), instrument list section.
- Header: watchlist name, data freshness indicator (TASK-243), delete button, "Add Stock" button.
- The digest section and instrument list are separate React components.

**Acceptance criteria:**
- Page renders with correct layout structure.
- Header shows watchlist name.
- "Add Stock" button is present.

**Testing:**
- Visual inspection of the page shell.

---

### TASK-214

**Title:** Stock row component (price, change, volume)  
**Epic:** Watchlist UX  
**Priority:** P0  

**Description:**  
Build the `StockRow` component for the instrument list. Displays: symbol, name, price, day change (amount and %), volume. Colour-coded (green for positive, red for negative change).

**Dependencies:** TASK-213, TASK-201

**Files likely affected:**
```
frontend/src/components/StockRow.tsx
frontend/src/styles/stockRow.css
```

**Implementation notes:**
- Positive change: text color from `--color-positive`.
- Negative change: text color from `--color-negative`.
- Click navigates to `/stocks/:symbol` (TASK-230).
- Shows the `data_status` indicator (stale, suspended) if applicable (TASK-244).
- Handles missing price data gracefully (show dash instead of null/undefined).

**Acceptance criteria:**
- Positive change shows in green, negative in red.
- Clicking row navigates to stock detail.
- Missing data shown as "—" not as "undefined".

**Testing:**
- Storybook or visual test with positive, negative, zero change data.

---

### TASK-215

**Title:** Add stock flow (search and add to watchlist)  
**Epic:** Watchlist UX  
**Priority:** P0  

**Description:**  
Build the "Add Stock" UX: a search input that calls the instrument search API as the user types, shows results in a dropdown, and adds the selected instrument to the current watchlist.

**Dependencies:** TASK-213, TASK-202

**Files likely affected:**
```
frontend/src/components/AddStockModal.tsx
frontend/src/components/InstrumentSearchInput.tsx
```

**Implementation notes:**
- Debounce search input: 300ms (avoid spamming the API on every keystroke).
- Show loading indicator while searching.
- Dropdown: show symbol, name, sector for each result.
- On select: call `POST /v1/watchlists/:id/instruments`; show success toast.
- Error cases: duplicate (show "Already in watchlist"), limit exceeded (show "Watchlist is full").

**Acceptance criteria:**
- Typing triggers search after 300ms debounce.
- Selecting an instrument adds it to the watchlist.
- Duplicate → shows "Already in watchlist" message.
- Instrument appears in the watchlist list after adding.

**Testing:**
- Happy path. Duplicate. Limit exceeded.

---

### TASK-216

**Title:** Remove stock from watchlist  
**Epic:** Watchlist UX  
**Priority:** P0  

**Description:**  
Add a "Remove" button (trash icon) to each `StockRow` in the watchlist detail view. Tapping it removes the instrument from the watchlist via the API and updates the UI.

**Dependencies:** TASK-214

**Files likely affected:**
```
frontend/src/components/StockRow.tsx
```

**Implementation notes:**
- "Remove" button: visible on hover (desktop) or as a swipe action (mobile — P2).
- No confirmation dialog needed (can re-add easily).
- On success: remove from the local list state immediately (optimistic update); call API in background.
- On API error: re-add to list and show error toast.

**Acceptance criteria:**
- Clicking remove removes the stock from the UI and calls the API.
- On API error: stock re-appears in list, error toast shown.

**Testing:**
- Happy path. Error recovery.

---

### TASK-217

**Title:** Empty watchlist state  
**Epic:** Watchlist UX  
**Priority:** P0  

**Description:**  
Build the empty state for a watchlist that has no instruments yet. Shows an illustration/icon and a call-to-action: "Add your first stock to start tracking changes."

**Dependencies:** TASK-213

**Files likely affected:**
```
frontend/src/components/EmptyWatchlist.tsx
```

**Implementation notes:**
- Show only when the watchlist exists but has 0 instruments.
- Includes "Add Stock" button that opens the AddStockModal (TASK-215).
- Illustration: simple SVG or icon.

**Acceptance criteria:**
- Empty watchlist shows the empty state component.
- "Add Stock" button in empty state opens the add stock modal.

**Testing:**
- Visual inspection with 0 instruments.

---

## EPIC 19 — Digest UX

---

### TASK-220

**Title:** "Since You Last Checked" digest banner  
**Epic:** Digest UX  
**Priority:** P0  

**Description:**  
Build the top-of-watchlist digest banner. Shows: "Since {date/time} — {N} changes deserve attention" with the benchmark Nifty 50 indicator.

**Dependencies:** TASK-213, TASK-201

**Files likely affected:**
```
frontend/src/components/DigestBanner.tsx
```

**Implementation notes:**
- Shows the `digest_window_label` from the API (e.g., "Since Friday, 6:32 PM").
- Shows the benchmark: "Nifty 50 +0.42% in this period".
- Shows count of digest items ("3 stocks deserve attention" or "Nothing significant changed").
- Dismiss button → see TASK-223.
- If `items.length > 0`: banner is highlighted (accent color background).
- If `items.length = 0`: banner is subdued (no-change state).

**Acceptance criteria:**
- Banner shows correct window label from API.
- Item count is accurate.
- Benchmark is shown.
- Dismiss button is present when items exist.

**Testing:**
- With items, without items, with null benchmark.

---

### TASK-221

**Title:** Meaningful change card (MCS rank, explanation, signals)  
**Epic:** Digest UX  
**Priority:** P0  

**Description:**  
Build the `ChangeCard` component that displays each digest item. Shows: rank, symbol/name, price + delta, plain-language explanation, and optionally the raw signal values (expandable).

**Dependencies:** TASK-220, TASK-214

**Files likely affected:**
```
frontend/src/components/ChangeCard.tsx
```

**Implementation notes:**
- Primary: stock symbol (large), price change (colour-coded), explanation text.
- Secondary (expandable "Details"): VAPM, SRM, VA raw values.
- MCS ranking badge: "1", "2", "3" pill.
- Tap: navigates to stock detail (TASK-230).
- The explanation is the pre-rendered string from the API response.

**Acceptance criteria:**
- Explanation text is displayed prominently.
- Signal values can be expanded/collapsed.
- MCS rank badge is correct.

**Testing:**
- Render with VAPM-primary, SRM-primary, VA-primary examples.

---

### TASK-222

**Title:** Attention priority section (digest items above fold)  
**Epic:** Digest UX  
**Priority:** P0  

**Description:**  
Build the "attention priority" section in the watchlist detail page. Digest items (ChangeCards) appear above the fold, sorted by MCS rank. Below the fold: the normal stock list.

**Dependencies:** TASK-221

**Files likely affected:**
```
frontend/src/pages/WatchlistDetailPage.tsx
frontend/src/components/AttentionPrioritySection.tsx
```

**Implementation notes:**
- Layout: DigestBanner → ranked ChangeCards → divider → normal StockRow list.
- The divider: "Remaining stocks — no significant changes" label.
- Smooth scroll to anchor if user taps a stock in the digest.

**Acceptance criteria:**
- Digest items appear above normal stock rows.
- Divider is visible between the two sections.
- Layout is correct on mobile.

**Testing:**
- Visual inspection with 3 digest items and 5 normal items.

---

### TASK-223

**Title:** Dismiss digest action (acknowledge)  
**Epic:** Digest UX  
**Priority:** P0  

**Description:**  
Implement the "Dismiss" button in the digest banner. On tap: calls `GET /digest?acknowledge=true`, hides the digest section, advances the window label to "Just now".

**Dependencies:** TASK-222

**Files likely affected:**
```
frontend/src/components/DigestBanner.tsx
frontend/src/pages/WatchlistDetailPage.tsx
```

**Implementation notes:**
- Button text: "Mark as seen" or "Dismiss".
- On tap: optimistic UI update (hide digest items immediately); call API.
- On API error: revert UI (show digest again), show error toast.
- After dismiss: the watchlist shows the normal stock list only (no digest section).
- State is managed in the page component.

**Acceptance criteria:**
- Dismiss hides the digest section immediately.
- API is called with `acknowledge=true`.
- API error → digest section reappears.

**Testing:**
- Happy path. Error recovery.

---

### TASK-224

**Title:** No-meaningful-change state  
**Epic:** Digest UX  
**Priority:** P0  

**Description:**  
Build the "Nothing significant changed" state. Shown when the digest has `items: []`. Uses a calm, reassuring visual design per product principle P4.

**Dependencies:** TASK-220

**Files likely affected:**
```
frontend/src/components/NoChangeState.tsx
```

**Implementation notes:**
- Text: "Nothing significant changed in {watchlist name} since {window_label}."
- Style: subdued, not an error state. Small checkmark icon.
- Still shows the normal stock list below.
- Does NOT show a "Dismiss" button (nothing to dismiss).

**Acceptance criteria:**
- Shows correct text with window label.
- Not styled as an error.
- Normal stock list is still visible below.

**Testing:**
- Visual inspection with an empty digest.

---

### TASK-225

**Title:** Benchmark Nifty 50 indicator in digest  
**Epic:** Digest UX  
**Priority:** P1  

**Description:**  
Add the Nifty 50 benchmark chip to the digest banner. Shows: "Nifty 50 +0.42%" (colour-coded by direction) as a reference point.

**Dependencies:** TASK-220

**Files likely affected:**
```
frontend/src/components/BenchmarkChip.tsx
```

**Implementation notes:**
- Positive: green chip. Negative: red chip. Zero: neutral.
- "Nifty 50 +0.42% since you last checked".
- If benchmark is null: hide the chip entirely (do not show "N/A").

**Acceptance criteria:**
- Correct colour for positive/negative.
- Hidden if benchmark is null.

**Testing:**
- Positive, negative, null benchmark.

---

### TASK-226

**Title:** Dwell-time dismiss timer (30-second front-end timer)  
**Epic:** Digest UX  
**Priority:** P0  

**Description:**  
Implement the front-end 30-second dwell timer. After the user has had the watchlist open for 30 seconds (and the digest is visible), automatically call `GET /digest?acknowledge=true` to advance the checkpoint.

**Dependencies:** TASK-223

**Files likely affected:**
```
frontend/src/pages/WatchlistDetailPage.tsx
frontend/src/hooks/useDwellTimer.ts
```

**Implementation notes:**
- Timer starts when the page mounts and the digest is visible.
- Timer is cancelled if user explicitly dismisses (TASK-223) before 30s.
- Timer is cancelled if user navigates away.
- After 30s: auto-acknowledge (same API call as explicit dismiss), but do NOT change the UI (the digest stays visible — the user may still be reading it). The checkpoint is advanced silently.
- Use `useEffect` with cleanup for the timer.

**Acceptance criteria:**
- After 30 seconds: `GET /digest?acknowledge=true` is called silently.
- Explicit dismiss before 30s: timer is cancelled.
- Navigation away before 30s: timer is cancelled.

**Testing:**
- Wait 30s with open watchlist; verify API call is made.
- Navigate away within 30s; verify no API call.

---

## EPIC 20 — Stock Detail UX

---

### TASK-230

**Title:** Stock detail page  
**Epic:** Stock Detail UX  
**Priority:** P1  

**Description:**  
Build the `/stocks/:symbol` page showing detailed market data for a single instrument: current price, day change, volume, 52w high/low, sector, and (if applicable) the most recent MCS and explanation.

**Dependencies:** TASK-214, TASK-205

**Files likely affected:**
```
frontend/src/pages/StockDetailPage.tsx
```

**Implementation notes:**
- Reads price and change data from the watchlist detail API (already fetched) or makes a direct call to `GET /watchlists/:id` filtered to this symbol.
- If the stock has a ChangeEvent (MCS > 0): show the explanation prominently at the top.
- Back button: returns to the watchlist.

**Acceptance criteria:**
- Stock name, symbol, price, change, volume are displayed.
- 52w high/low bar is shown (TASK-231).
- Sector is shown (TASK-232).
- If MCS > 0: explanation is shown at the top.

**Testing:**
- Visual inspection with a stock that has MCS > 0 and one that doesn't.

---

### TASK-231

**Title:** 52-week high/low bar component  
**Epic:** Stock Detail UX  
**Priority:** P1  

**Description:**  
Build a visual bar that shows the stock's current price relative to its 52-week high and low. A position indicator shows where the current price sits on the range.

**Dependencies:** TASK-230

**Files likely affected:**
```
frontend/src/components/HighLowBar.tsx
```

**Implementation notes:**
- Bar: from `low_52w` to `high_52w`.
- Position: `(current_price - low_52w) / (high_52w - low_52w) * 100%`.
- Labels: "52w Low ₹X" on left, "52w High ₹X" on right.
- If `high_52w = low_52w` (unlikely but possible): render a flat bar.

**Acceptance criteria:**
- Price at low shows position at left.
- Price at high shows position at right.
- Price halfway shows position in the middle.

**Testing:**
- Unit: position calculation for various price values.

---

### TASK-232

**Title:** Sector context row  
**Epic:** Stock Detail UX  
**Priority:** P1  

**Description:**  
Show the stock's sector and sector return in the stock detail page. "Sector: NIFTYBANK — +0.3% today".

**Dependencies:** TASK-230

**Files likely affected:**
```
frontend/src/components/SectorContextRow.tsx
```

**Implementation notes:**
- Sector name from the instrument's `sector` field.
- Sector return: from the `benchmark` data in the digest, or from a direct sector snapshot.
- Colour-coded by direction.

**Acceptance criteria:**
- Sector name is correct.
- Sector return is shown with correct colour.

**Testing:**
- Visual inspection with a banking stock and an IT stock.

---

## EPIC 21 — Error / Loading / Empty / Stale States

---

### TASK-240

**Title:** Loading skeleton screens  
**Epic:** Error / Loading / Empty / Stale States  
**Priority:** P0  

**Description:**  
Implement skeleton loading screens for the watchlist list page and watchlist detail page. Skeleton screens replace the loading spinner for a polished UX.

**Dependencies:** TASK-206

**Files likely affected:**
```
frontend/src/components/Skeleton.tsx
frontend/src/components/WatchlistListSkeleton.tsx
frontend/src/components/WatchlistDetailSkeleton.tsx
```

**Implementation notes:**
- Use CSS animation (`@keyframes pulse`) for the shimmer effect.
- WatchlistListSkeleton: 3 cards with placeholder dimensions.
- WatchlistDetailSkeleton: a digest banner placeholder + 5 stock row placeholders.
- Shown for the duration of the initial data fetch.

**Acceptance criteria:**
- Loading skeleton shows before data arrives.
- Skeleton disappears and is replaced by actual content.
- No layout shift (skeleton matches actual content dimensions).

**Testing:**
- Throttle network; verify skeleton appears.

---

### TASK-241

**Title:** API error state component  
**Epic:** Error / Loading / Empty / Stale States  
**Priority:** P0  

**Description:**  
Build a reusable `ApiErrorState` component that renders when an API call fails. Shows: error message, a retry button, and a support message.

**Dependencies:** TASK-206

**Files likely affected:**
```
frontend/src/components/ApiErrorState.tsx
```

**Implementation notes:**
- Props: `error: ApiError | null`, `onRetry: () => void`.
- Renders the `error.detail` from RFC-7807 (or a generic message if detail is absent).
- "Retry" button calls `onRetry`.
- Different messages for 404 (not found), 401 (session expired), 5xx (server error).

**Acceptance criteria:**
- API error → shows error message and retry button.
- "Retry" button re-triggers the API call.
- 401 → shows "Your session has expired. Please log in again." with login link.

**Testing:**
- Visual inspection with 404, 500, 401 error objects.

---

### TASK-242

**Title:** Stale data warning banner  
**Epic:** Error / Loading / Empty / Stale States  
**Priority:** P0  

**Description:**  
Build the stale data warning banner that appears at the top of the watchlist when `data_freshness = "unavailable"`. Shows: "Data unavailable — showing cached prices from HH:MM IST."

**Dependencies:** TASK-241, TASK-141

**Files likely affected:**
```
frontend/src/components/StaleDataBanner.tsx
```

**Implementation notes:**
- Styled as a warning (amber/yellow, not red).
- Shows `data_as_of` formatted as "last updated HH:MM IST".
- Not dismissable by the user (it disappears when data becomes fresh again).
- Appears above the digest section and the stock list.

**Acceptance criteria:**
- Banner appears when `data_freshness = "unavailable"`.
- Banner disappears when data becomes fresh.
- Shows correct timestamp.

**Testing:**
- Render with stale vs fresh data freshness values.

---

### TASK-243

**Title:** Data freshness indicator chip  
**Epic:** Error / Loading / Empty / Stale States  
**Priority:** P0  

**Description:**  
Build the `FreshnessChip` component that shows the data freshness label ("Live", "~3 min delayed", "Market closed") in the watchlist detail header.

**Dependencies:** TASK-141

**Files likely affected:**
```
frontend/src/components/FreshnessChip.tsx
```

**Implementation notes:**
- "Live": green dot + "Live" text.
- "Delayed": amber dot + "~N min delayed".
- "Market closed": grey dot + "Market closed — HH:MM IST".
- "Unavailable": red dot + "Data unavailable".

**Acceptance criteria:**
- Each freshness state shows the correct dot color and text.
- Updates when the watchlist is refreshed.

**Testing:**
- Render with all four freshness values.

---

### TASK-244

**Title:** Suspended instrument label in UI  
**Epic:** Error / Loading / Empty / Stale States  
**Priority:** P1  

**Description:**  
In the stock row, show a "Trading suspended" badge when `data_status = "suspended"`. The row should still be rendered but clearly marked.

**Dependencies:** TASK-214

**Files likely affected:**
```
frontend/src/components/StockRow.tsx
frontend/src/components/SuspendedBadge.tsx
```

**Implementation notes:**
- Badge: red or amber label reading "Suspended".
- Price and change data may be stale — show the last known price with a stale indicator.
- Do not show volume (it will be 0 and misleading).

**Acceptance criteria:**
- Suspended stock shows "Suspended" badge.
- Price shown is the last known price.

**Testing:**
- Visual inspection with a suspended instrument in the watchlist.

---

## EPIC 22 — Frontend ↔ Backend Integration

---

### TASK-250

**Title:** Connect watchlist list page to GET /watchlists  
**Epic:** Frontend ↔ Backend Integration  
**Priority:** P0  

**Description:**  
Wire the watchlist list page to the `GET /v1/watchlists` API. Implement data fetching, loading state (skeleton), error state, and empty state.

**Dependencies:** TASK-054, TASK-052, TASK-202, TASK-210, TASK-211

**Files likely affected:**
```
frontend/src/pages/WatchlistListPage.tsx
frontend/src/hooks/useWatchlists.ts
```

**Implementation notes:**
- Custom hook `useWatchlists()` that calls `GET /watchlists`, returns `{watchlists, loading, error, refetch}`.
- On success: render WatchlistCard list.
- Loading: render WatchlistListSkeleton.
- Error: render ApiErrorState with retry.
- Empty: render empty state.
- After create/delete: call `refetch()`.

**Acceptance criteria:**
- Watchlists from API render correctly.
- Loading skeleton shows during fetch.
- Error state shows on API failure.
- New watchlist appears after creation.

**Testing:**
- Integration test: renders with mocked API responses for loading, success, error, empty.

---

### TASK-251

**Title:** Connect watchlist detail to GET /watchlists/:id  
**Epic:** Frontend ↔ Backend Integration  
**Priority:** P0  

**Description:**  
Wire the watchlist detail page to `GET /v1/watchlists/{id}`. Render the instrument list with live market data. Handle all data states.

**Dependencies:** TASK-250, TASK-213, TASK-214

**Files likely affected:**
```
frontend/src/pages/WatchlistDetailPage.tsx
frontend/src/hooks/useWatchlistDetail.ts
```

**Implementation notes:**
- Fetch on mount and every 60 seconds (TASK-255).
- Render WatchlistDetailSkeleton during initial load.
- Render StockRow for each instrument.
- Render FreshnessChip from `data_freshness`.
- Handle 404 (watchlist not found or not owned): redirect to `/watchlists`.

**Acceptance criteria:**
- Instruments render with correct price data.
- FreshnessChip shows correct label.
- 404 redirects to list page.

**Testing:**
- Integration: mocked API success, error, 404.

---

### TASK-252

**Title:** Connect digest to GET /watchlists/:id/digest  
**Epic:** Frontend ↔ Backend Integration  
**Priority:** P0  

**Description:**  
Wire the digest section to `GET /v1/watchlists/{id}/digest`. Render DigestBanner, ChangeCards, and NoChangeState based on the response.

**Dependencies:** TASK-251, TASK-220, TASK-221, TASK-224

**Files likely affected:**
```
frontend/src/pages/WatchlistDetailPage.tsx
frontend/src/hooks/useDigest.ts
```

**Implementation notes:**
- Fetch digest separately from watchlist detail (the detail for stock list, digest for the change section).
- `useDigest(watchlistId)` returns `{digest, loading, error, acknowledge}`.
- `items.length > 0`: render AttentionPrioritySection with ChangeCards.
- `items.length = 0`: render NoChangeState.
- Render DigestBanner in both cases.

**Acceptance criteria:**
- Digest items render as ChangeCards.
- Empty digest renders NoChangeState.
- DigestBanner shows correct window label.

**Testing:**
- Integration: mocked digest with items, without items, loading, error.

---

### TASK-253

**Title:** Connect acknowledge to GET /digest?acknowledge=true  
**Epic:** Frontend ↔ Backend Integration  
**Priority:** P0  

**Description:**  
Wire the dismiss button (and 30s dwell timer) to call `GET /digest?acknowledge=true`. Handle the response and update UI state.

**Dependencies:** TASK-252, TASK-223, TASK-226

**Files likely affected:**
```
frontend/src/hooks/useDigest.ts
```

**Implementation notes:**
- The `acknowledge` function in `useDigest` calls the API with `?acknowledge=true`.
- On success: update the `last_checked_at` value in local state.
- The dismiss button and dwell timer both call `acknowledge()`.
- No race condition: subsequent calls are no-ops (advance-only on server).

**Acceptance criteria:**
- Dismiss button calls API correctly.
- Dwell timer calls API after 30s.
- Double calls (dismiss + dwell) do not cause errors.

**Testing:**
- Integration: dismiss, then verify `last_checked_at` updated.

---

### TASK-254

**Title:** Connect instrument search to GET /instruments/search  
**Epic:** Frontend ↔ Backend Integration  
**Priority:** P0  

**Description:**  
Wire the `InstrumentSearchInput` component to the `GET /v1/instruments/search?q=...` API. Handle debouncing, loading, empty results, and error states.

**Dependencies:** TASK-252, TASK-215, TASK-202

**Files likely affected:**
```
frontend/src/components/InstrumentSearchInput.tsx
frontend/src/hooks/useInstrumentSearch.ts
```

**Implementation notes:**
- `useInstrumentSearch(query)`: debounced 300ms, calls API only if query length >= 2.
- Returns `{results, loading, error}`.
- Loading: show spinner in the search input.
- No results: "No instruments found for '{query}'."
- Error: "Search unavailable. Try again."

**Acceptance criteria:**
- Search results appear after 300ms debounce.
- Short queries (1 char) do not trigger the API.
- No results state shows correctly.

**Testing:**
- Integration: various query lengths, debounce, API error.

---

### TASK-255

**Title:** 60-second auto-refresh polling strategy  
**Epic:** Frontend ↔ Backend Integration  
**Priority:** P1  

**Description:**  
Implement automatic data refresh on the watchlist detail page: refresh market data every 60 seconds while the page is visible. Pause refresh when the tab is hidden (browser `visibilitychange` API).

**Dependencies:** TASK-251

**Files likely affected:**
```
frontend/src/hooks/usePolling.ts
frontend/src/hooks/useWatchlistDetail.ts
```

**Implementation notes:**
- `usePolling(callback, intervalMs)`: calls `callback` every `intervalMs`, pauses when `document.hidden`.
- On return to tab: immediately refresh (don't wait for the next interval).
- Only poll watchlist detail (not digest — user must manually dismiss to reset digest state).
- Show last refreshed time in the FreshnessChip.

**Acceptance criteria:**
- Data refreshes every ~60s while tab is visible.
- Switching tabs pauses the refresh.
- Returning to tab triggers immediate refresh.

**Testing:**
- Manual: verify refresh intervals.

---

## EPIC 23 — Testing

---

### TASK-300

**Title:** Unit tests: VAPM signal computation  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Write comprehensive unit tests for `computeVAPM()` covering: normal move, large move (> 1.5 ATR), small move (< 1.5 ATR), ATR null, ATR = 0, baseline price = 0.

**Dependencies:** TASK-092

**Test file:** `worker/src/changeEngine/signals/__tests__/vapm.test.ts`

**Test cases:**
1. Stock at 2.0x ATR → VAPM = 2.0.
2. Stock at 1.5x ATR → VAPM = 1.5.
3. Stock at 0.5x ATR → VAPM = 0.5.
4. ATR = null → VAPM = null.
5. ATR = 0 → VAPM = null (zero-division guard).
6. Baseline price = 0 → VAPM = null.
7. Large move: stock moves 5x ATR.

**Acceptance criteria:** All test cases pass.

---

### TASK-301

**Title:** Unit tests: SRM signal computation  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Write unit tests for `computeSRM()`.

**Test cases:**
1. Stock +3%, sector +3% → SRM = 0.0.
2. Stock +4%, sector +1% → SRM = 3.0.
3. Stock -2%, sector +1% → SRM = 3.0.
4. Stock -4%, sector -1% → SRM = 3.0.
5. Stock 0%, sector 0% → SRM = 0.0.
6. Baseline = 0 → handled gracefully (null or 0).

**Acceptance criteria:** All test cases pass.

---

### TASK-302

**Title:** Unit tests: VA signal computation  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Write unit tests for `computeVA()`.

**Test cases:**
1. VA = 2.5 (2.5x avg) → 2.5.
2. VA = 1.0 (normal) → 1.0.
3. Avg = 0 (no history) → 0.
4. Volume = 0 (circuit halt) → 0.
5. VA = 10x (extreme spike).

**Acceptance criteria:** All test cases pass.

---

### TASK-303

**Title:** Unit tests: MCS weighted combination  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Verify the scoring examples from DESIGN.md §13 exactly.

**Test cases (from design document):**
1. HDFC Bank: VAPM=2.8, SRM=3.2, VA=1.1 → MCS=1.25.
2. Infosys: VAPM=1.3, SRM=0.4, VA=1.4 → MCS=0.0.
3. Zomato: VAPM=1.6, SRM=0.8, VA=3.1 → MCS~=0.165.
4. All signals at floor → MCS = 0.0.
5. All signals at 0 → MCS = 0.0.

**Acceptance criteria:** All design-document examples pass exactly (within floating point tolerance 0.001).

---

### TASK-304

**Title:** Unit tests: Signal floor application  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Test `applyFloors()`.

**Test cases:**
1. VAPM=2.8, floor=1.5 → vapmSignal=1.3.
2. VAPM=1.2, floor=1.5 → vapmSignal=0.0.
3. VAPM=1.5 (exactly at floor) → vapmSignal=0.0.
4. VAPM=null → vapmSignal=0.0.
5. VA=2.0, floor=2.0 → vaSignal=0.0.
6. VA=2.1, floor=2.0 → vaSignal=0.1.

**Acceptance criteria:** All cases pass.

---

### TASK-305

**Title:** Unit tests: Explanation template generation  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Test all 8 explanation templates and the guard rules.

**Test cases:**
1. VAPM-primary, stock rose → `VAPM_ROSE` template output.
2. VAPM-primary, stock fell → `VAPM_FELL` template output.
3. SRM-primary, outperform → `SRM_OUTPERFORMED`.
4. SRM-primary, underperform → `SRM_UNDERPERFORMED`.
5. VA-primary, price rose → `VA_PRICE_ROSE`.
6. VA-primary, price flat → `VA_FLAT`.
7. Two signals → combined template.
8. Explanation with banned word → guard substitutes fallback.
9. No forward-looking words in any template output.

**Acceptance criteria:** All cases pass.

---

### TASK-306

**Title:** Unit tests: Baseline snapshot anchor lookup  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Test the baseline snapshot resolver.

**Test cases:**
1. Timestamp between two snapshots → returns the earlier one.
2. Timestamp before any snapshot → returns last-close fallback.
3. `last_checked_at = null` → returns market-open baseline.
4. `last_checked_at` = 60 days ago → capped to 30 days ago.
5. Friday 15:00 IST → snapped to Friday 15:30 close.
6. Sunday 10:00 IST → snapped to Friday 15:30 close.

**Acceptance criteria:** All cases pass.

---

### TASK-307

**Title:** Unit tests: Data freshness label rules  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Parametrized unit tests for all freshness label conditions.

**Test cases (parametrized by snapshot age and market state):**
1. age=30s, market open → "live".
2. age=89s → "live".
3. age=90s → "~1 min delayed".
4. age=150s → "~2 min delayed".
5. age=300s → "~5 min delayed".
6. age=301s, market open → "delayed — last updated HH:MM".
7. market closed → "market closed — last updated HH:MM IST".
8. data_freshness=unavailable → "data unavailable — showing cached prices from HH:MM".

**Acceptance criteria:** All cases produce the correct label string.

---

### TASK-308

**Title:** Unit tests: Outlier filter  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Test `filterOutliers()`.

**Test cases:**
1. 25% tick move, max=20% → rejected.
2. 19% tick move, max=20% → accepted.
3. 20% exactly → rejected (> 20% is the condition; at boundary: accepted or rejected — clarify in implementation).
4. No previous price (new instrument) → accepted.
5. 0% move → accepted.
6. Negative price (impossible, corrupted data) → rejected.

**Acceptance criteria:** All cases pass.

---

### TASK-309

**Title:** Unit tests: Market hours checker  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Test `isMarketOpen()` and `getLastMarketClose()`.

**Test cases:**
1. Monday 10:00 IST, not holiday → `true`.
2. Monday 09:14 IST → `false` (pre-open).
3. Monday 15:31 IST → `false` (post-close).
4. Saturday any time → `false`.
5. NSE holiday (fixed from calendar) → `false`.
6. `getLastMarketClose()` called on Sunday → Friday 15:30 IST.
7. `getLastMarketClose()` called on Monday 09:00 → Friday 15:30 IST.
8. `getLastMarketClose()` called on Monday 10:00 → Monday 09:15 IST (today's open — no, this should be "last close before NOW", so Monday 09:15 is the open not the close. Verify: last close = previous Friday 15:30).

**Acceptance criteria:** All cases pass.

---

### TASK-310

**Title:** Unit tests: Optimistic last_checked_at SQL update  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Test the advance-only SQL update function.

**Test cases:**
1. Advance from T0 to T1 (T1 > T0) → updated to T1.
2. Attempt to rewind from T1 to T0 (T0 < T1) → no-op, T1 preserved.
3. First update from NULL → updated to T1.
4. Same timestamp → no-op (equal, not strictly less than).

**Acceptance criteria:** All cases pass with test DB.

---

### TASK-311

**Title:** Unit tests: 30-day cap on baseline  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Test the 30-day cap in baseline resolution.

**Test cases:**
1. `last_checked_at` = 29 days ago → not capped.
2. `last_checked_at` = 30 days ago → at boundary, not capped (< vs <=).
3. `last_checked_at` = 31 days ago → capped to 30 days ago.
4. `last_checked_at` = 60 days ago → capped to 30 days ago.
5. Response includes `window_notice` when capped.

**Acceptance criteria:** All cases pass.

---

### TASK-312

**Title:** Integration tests: Watchlist CRUD  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Integration tests for the full watchlist management API against a real test database.

**Test cases:**
1. Create watchlist → 201.
2. List watchlists → correct count.
3. Delete watchlist → 204, verify gone.
4. Create 11th watchlist → 422.
5. Create watchlist with 65-char name → 400.
6. User A cannot see User B's watchlists.

**Test setup:** Use a test PostgreSQL database (Docker), run migrations before test suite, clear data between tests.

**Acceptance criteria:** All cases pass.

---

### TASK-313

**Title:** Integration tests: Add and remove instruments  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Integration tests for instrument management within a watchlist.

**Test cases:**
1. Add valid instrument → 201.
2. Add same instrument twice → 422 duplicate-instrument.
3. Add non-existent symbol → 404.
4. Add 101st instrument → 422.
5. Remove instrument → 204.
6. Remove instrument not in watchlist → 404.

**Acceptance criteria:** All cases pass.

---

### TASK-314

**Title:** Integration tests: Digest endpoint end-to-end  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Integration test of the full digest pipeline: seed instruments, run the ChangeEngine, call the digest API.

**Test setup:**
1. Seed instruments with known snapshot data.
2. Run ChangeEngine.
3. Call `GET /watchlists/:id/digest`.
4. Verify response shape and values.

**Test cases:**
1. Instrument with MCS > 0 → appears in `items`.
2. Instrument with MCS = 0 → in `no_change_items_count`.
3. Items sorted by MCS descending.
4. Digest has correct `last_checked_at`.
5. Explanation string present for each item.
6. Benchmark is present.

**Acceptance criteria:** All cases pass.

---

### TASK-315

**Title:** Integration tests: Acknowledge updates last_checked_at  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Integration test for the acknowledge flow.

**Test cases:**
1. `GET /digest` → `last_checked_at` unchanged.
2. `GET /digest?acknowledge=true` → `last_checked_at` updated to NOW().
3. Second `acknowledge=true` with older timestamp → no-op.
4. Subsequent `GET /digest` shows new `last_checked_at`.

**Acceptance criteria:** All cases pass.

---

### TASK-316

**Title:** Integration tests: Instrument search  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Integration tests for the instrument search API.

**Test cases:**
1. `q=HDFC` → returns HDFCBANK and related.
2. `q=infy` (lowercase) → returns INFY (case-insensitive).
3. `q=` (empty) → 400.
4. `q=NONEXISTENT` → empty results, 200.
5. Suspended instrument → not in results.

**Acceptance criteria:** All cases pass.

---

### TASK-317

**Title:** E2E test: Core user journey  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
End-to-end test of the full user journey using Playwright or Supertest + a test client.

**Flow:**
1. Register a new user.
2. Log in.
3. Create a watchlist.
4. Add 3 instruments.
5. Simulate a market cycle (seed specific MCS data).
6. Open the watchlist digest.
7. Verify digest items, explanations, and ranking.
8. Dismiss digest.
9. Verify `last_checked_at` updated.
10. Re-open digest → verify it reflects post-dismiss state.

**Acceptance criteria:** Full journey passes without errors.

---

### TASK-318

**Title:** Edge case: Duplicate stock in watchlist  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Verify that adding the same stock twice returns a meaningful 422 error (not a 500 DB error). Test both the API response shape and the database constraint.

**Dependencies:** TASK-059

**Test:** Add INFY to watchlist. Add INFY again. Verify 422 with `type: "duplicate-instrument"`.

---

### TASK-319

**Title:** Edge case: Stock added after last_checked_at  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Verify that stocks added after the user's `last_checked_at` appear in the digest with `status: "added_since_last_check"` and do not have MCS computed.

**Dependencies:** TASK-138

**Test:** Set `last_checked_at = NOW() - 1 hour`. Add a stock. Call digest. Verify the stock appears with the correct note.

---

### TASK-320

**Title:** Edge case: ATR unavailable (new listing)  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Verify that a stock with `atr_14 = null` in the snapshot has MCS computed from SRM and VA only (VAPM excluded), and the ChangeEvent stores `vapm = null`.

**Dependencies:** TASK-097

**Test:** Insert a snapshot with `atr_14 = null`. Run ChangeEngine. Verify ChangeEvent has `vapm = null` but valid `srm` and `mcs`.

---

### TASK-321

**Title:** Edge case: Missing or stale market data  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Verify that missing snapshots for some instruments are handled gracefully: those instruments are skipped in ChangeEngine, others are computed normally.

**Dependencies:** TASK-098

**Test:** Write snapshots for 5 of 8 watchlist instruments. Run ChangeEngine. Verify ChangeEvents only for the 5 present instruments.

---

### TASK-322

**Title:** Edge case: Zero volume or zero/invalid prices  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Verify that zero or invalid price/volume data does not crash the ChangeEngine and produces MCS = 0.

**Test cases:**
- `volume = 0`: VA = 0, no VA contribution.
- `price = 0` (corrupted data): outlier filter rejects (if previous price exists, a move from anything to 0 is > 20%).
- `avgVolume20d = 0`: VA = 0.

---

### TASK-323

**Title:** Edge case: Market-wide circuit breaker (all stocks high MCS)  
**Epic:** Testing  
**Priority:** P1  

**Description:**  
Verify that when all stocks in a watchlist have high MCS (extreme market event), the digest correctly surfaces all of them with no artificial cap.

**Test:** Seed 10 instruments all with VAPM > 3.0. Run ChangeEngine. Verify digest `items.length = 10`.

---

### TASK-324

**Title:** Edge case: Concurrent multi-device last_checked_at update  
**Epic:** Testing  
**Priority:** P1  

**Description:**  
Simulate two simultaneous `acknowledge=true` requests from different sessions (same user, same watchlist). Verify the final `last_checked_at` is the maximum of the two and no error occurs.

**Dependencies:** TASK-127

**Test:** Two parallel requests with timestamps T1 and T2 (T2 > T1). Final value should be T2.

---

### TASK-325

**Title:** Edge case: Out-of-order market data (duplicate cycle_id)  
**Epic:** Testing  
**Priority:** P1  

**Description:**  
Verify that a slow worker cycle writing a snapshot with an already-used `cycle_id` is silently ignored via `ON CONFLICT DO NOTHING`.

**Dependencies:** TASK-083

**Test:** Insert cycle 5 snapshots. Insert cycle 5 again with different prices. Verify the DB still has the original cycle 5 prices (first write wins).

---

### TASK-326

**Title:** Edge case: Suspended/delisted instrument  
**Epic:** Testing  
**Priority:** P1  

**Description:**  
Verify that an instrument with `status = 'SUSPENDED'` in the instruments table:
- Appears in watchlist detail with `data_status: "suspended"`.
- Does NOT appear in digest items.

**Dependencies:** TASK-143

---

### TASK-327

**Title:** Edge case: User who has never checked (NEVER_CHECKED)  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Verify that a user with `last_checked_at = null` gets a digest with baseline = market open today (or last close). Verify the window label is correct.

**Dependencies:** TASK-124

---

### TASK-328

**Title:** Edge case: User not checked in > 30 days  
**Epic:** Testing  
**Priority:** P0  

**Description:**  
Verify that a user with `last_checked_at` 60 days ago gets a 30-day capped baseline, and the digest response includes `window_notice = "Showing changes over the past 30 days."`.

**Dependencies:** TASK-125

---

### TASK-329

**Title:** Load test: Watchlist digest at 100 instruments  
**Epic:** Testing  
**Priority:** P1  

**Description:**  
Verify that the digest endpoint responds within p95 < 400ms for a watchlist with 100 instruments. Use `autocannon` or `k6` for the load test.

**Test setup:**
- Seed one watchlist with 100 instruments.
- Seed Redis with MCS values for all 100.
- Run 50 concurrent requests for 30 seconds.
- Measure p95 latency.

**Acceptance criteria:** p95 < 400ms.

---

## EPIC 24 — Security

---

### TASK-400

**Title:** Input sanitization and parameterized queries audit  
**Epic:** Security  
**Priority:** P0  

**Description:**  
Audit all DB queries in backend and worker to verify that every query uses parameterized placeholders (no string concatenation). Document the review.

**Dependencies:** TASK-062

**Files likely affected:**
```
All repository files.
docs/SECURITY_AUDIT.md
```

**Acceptance criteria:**
- Zero instances of string-concatenated SQL in the codebase.
- SQL injection payloads tested on all input fields return 0 results or 400 errors.

**Testing:**
- Grep the codebase for string interpolation in SQL strings.
- SQL injection fuzzing test.

---

### TASK-401

**Title:** JWT user_id claim enforcement audit  
**Epic:** Security  
**Priority:** P0  

**Description:**  
Verify that every API handler that accesses user-scoped data uses `request.user.userId` from the JWT (not a client-supplied `user_id` in the body or params).

**Dependencies:** TASK-150

**Acceptance criteria:**
- No handler accepts `user_id` from the request body or query params for data scoping.
- All DB queries include `WHERE user_id = jwt.user_id`.

**Testing:**
- Attempt to access another user's data by spoofing user_id in the request body. Verify the actual JWT user_id is used.

---

### TASK-402

**Title:** PostgreSQL RLS verification test  
**Epic:** Security  
**Priority:** P1  

**Description:**  
Write a test that directly queries the database as the application DB role (not superuser), verifies that RLS prevents cross-user data access.

**Dependencies:** TASK-030

**Test:**
1. Create User A and User B with watchlists.
2. SET LOCAL app.current_user_id = UserA.id.
3. SELECT * FROM watchlists. Verify only User A's watchlists are returned.

**Acceptance criteria:** RLS prevents cross-user reads even without the API layer.

---

### TASK-403

**Title:** Redis namespace isolation verification  
**Epic:** Security  
**Priority:** P1  

**Description:**  
Verify that Redis keys are namespaced correctly and that reading one user's session key cannot return another user's data.

**Dependencies:** TASK-040

**Test:** Verify that `session:{userId_A}:{watchlistId}` and `session:{userId_B}:{watchlistId}` return different values.

**Acceptance criteria:** Redis keys are per-user; no cross-user reads possible.

---

### TASK-404

**Title:** Secret rotation documentation  
**Epic:** Security  
**Priority:** P2  

**Description:**  
Document the procedure for rotating: JWT RS256 key pair, market data API key, PostgreSQL password, Redis password (if set). Include how to rotate without downtime.

**Files likely affected:**
```
docs/SECRET_ROTATION.md
```

**Acceptance criteria:**
- Each secret has a documented rotation procedure.
- JWT key rotation: dual-key (old and new key accepted simultaneously during transition).

---

## EPIC 25 — Final QA

---

### TASK-500

**Title:** Full demo walkthrough — all 6 demo scenarios  
**Epic:** Final QA  
**Priority:** P0  

**Description:**  
Run through all 6 demo scenarios (NORMAL, VAPM_SPIKE, VOLUME_ANOMALY, NO_CHANGE, STALE_DATA, RECOVERY) end-to-end with the real frontend connected to the backend. Document any issues found.

**Dependencies:** TASK-317, TASK-318, TASK-323, TASK-325

**Acceptance criteria:**
- Each scenario produces the expected UI state.
- No errors in the console or server logs.
- Demo is repeatable: can run it twice in sequence.

---

### TASK-501

**Title:** Cross-device multi-session test  
**Epic:** Final QA  
**Priority:** P1  

**Description:**  
Test the multi-device scenario: open the watchlist on two browsers (Chrome + Firefox) simultaneously. Dismiss from one; verify the other reflects the updated `last_checked_at` on next refresh.

**Dependencies:** TASK-324

**Acceptance criteria:**
- Dismiss on Browser A → Browser B sees updated window label after refresh.
- No errors on either browser.

---

### TASK-502

**Title:** API contract validation (all endpoints)  
**Epic:** Final QA  
**Priority:** P0  

**Description:**  
Verify every API endpoint from DESIGN.md §26 against the actual implementation. Check: HTTP method, URL, request shape, response shape, error codes.

**Files likely affected:**
```
docs/API_AUDIT.md
```

**Acceptance criteria:**
- Every endpoint in DESIGN.md §26 is implemented.
- Response shapes match the design exactly.
- All error codes are correct.

---

### TASK-503

**Title:** Performance validation — p95 digest latency < 400ms  
**Epic:** Final QA  
**Priority:** P1  

**Description:**  
Run `autocannon` or `k6` against the `GET /watchlists/:id/digest` endpoint with a 100-instrument watchlist and Redis warm. Verify p95 < 400ms.

**Dependencies:** TASK-329

**Test command:** `autocannon -c 50 -d 30 http://localhost:3000/v1/watchlists/:id/digest`

**Acceptance criteria:** p95 < 400ms. p99 < 800ms.

---

### TASK-504

**Title:** Data freshness label accuracy verification  
**Epic:** Final QA  
**Priority:** P0  

**Description:**  
Manually verify all freshness label states by controlling the worker's cycle timing:
1. Run the worker normally → "Live" label.
2. Stop the worker for 5 minutes → "delayed" label.
3. Close market hours → "Market closed" label.
4. Kill the worker entirely → "Data unavailable" label after TTL expires.

**Dependencies:** TASK-243

**Acceptance criteria:** Each label state renders correctly in the frontend.

---

### TASK-505

**Title:** Final README and deployment docs  
**Epic:** Final QA  
**Priority:** P0  

**Description:**  
Write the final `README.md` covering: project overview, local development setup, demo mode instructions, environment variable reference, and a brief architecture summary.

**Dependencies:** TASK-502

**Files likely affected:**
```
README.md
docs/SETUP.md
docs/DEMO_GUIDE.md
```

**Acceptance criteria:**
- A new developer can follow the README to run the project locally with demo mode.
- All environment variables are documented.
- Demo guide explains how to advance scenarios.

---

*End of GROWW CODE 2026 Task Roadmap*
