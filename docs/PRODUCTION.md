# Production readiness

Companion specs: [specs/SPEC-ops.md](specs/SPEC-ops.md), master [SPEC.md](SPEC.md), roadmap [ROADMAP.md](ROADMAP.md).

## Runtime

1. Configure secrets via environment / secret manager (`API_KEY`, `POSTGRES_PASSWORD`, LLM keys, optional `ADZUNA_APP_ID`/`ADZUNA_APP_KEY`).
1b. Apply migrations: `cd backend && alembic upgrade head` (includes `dashboard_prefs` on `user_profiles`).
2. **Daily crawlers (required for Demand Compass freshness):** source updates run through scheduled collector crawls (authorized API/RSS/boards only—not ToS-bypass scraping). Prefer external cron **once per day**, e.g.:
   ```cron
   0 3 * * * API_URL=https://your-api ./backend/scripts/scheduler_tick.sh
   ```
   ```bash
   API_URL=https://your-api ./backend/scripts/scheduler_tick.sh
   # optional: API_KEY=...
   ```
   Set `ENABLE_SCHEDULER=false` on all API replicas when using cron. Only enable in-process `ENABLE_SCHEDULER=true` on a **single** replica if cron is unavailable. Tick order: dump/feed → discovery watchlist → focus intents ([SPEC-research-intents.md](specs/SPEC-research-intents.md)). Dashboards read Postgres; they do not crawl on page view.

   **Local Compose (single API):** set `ENABLE_SCHEDULER=true` and `SCHEDULER_INTERVAL_SECONDS=86400` in `.env`, then recreate `api`. The process runs one tick on boot (UTC-day idempotent) and again every interval. Manual: `API_URL=http://127.0.0.1:8000 ./backend/scripts/scheduler_tick.sh` (needs `API_KEY` if configured). Check `GET /api/v1/ops/metrics` → `crawler.last_tick`.
3. Put Postgres behind managed backups; use `backend/scripts/backup_db.sh` as baseline. Verify dump path with `./backend/scripts/backup_smoke.sh` (schema-only, discarded). Verify restore path with `./backend/scripts/restore_smoke.sh` (schema → temp DB → drop; never touches primary). Scripts prefer `docker compose exec db pg_dump`/`psql` when Compose `db` is running (avoids host client major-version mismatch); override with `PG_DUMP` / `PSQL`.
3b. Probes (no API key): liveness `GET /livez` (always 200 if process up); readiness `GET /readyz` and `GET /healthz` (same handler — 200 only when DB is up, and Redis when `RATE_LIMIT_BACKEND=redis`; else **503** so `curl -sf` / Compose fail closed). Compose `api` healthcheck uses `/readyz`. Authenticated: `GET /api/v1/health`.
4. Set `APP_ENV=production` (or `prod`) and `API_CORS_ORIGINS` to the real frontend
   origin(s), comma-separated — empty or `*` fail startup. Locally keep
   `APP_ENV=development` and include both `http://localhost:3000` and
   `http://127.0.0.1:3000` (distinct Origins). Recreate the API container after env changes.
5. Terminate TLS at reverse proxy (Caddy/Nginx/Cloud LB).

## Security baseline

- Optional `API_KEY` header for private endpoints.
- Rate limiting: `RATE_LIMIT_PER_MINUTE` with `RATE_LIMIT_BACKEND=memory` (default) or `redis` (uses `REDIS_URL`; falls back to memory if Redis is down).
- **Containers run as non-root (image + Compose):**
  - **Production / image-only** (no `./backend` bind): Dockerfile `USER appuser` (uid 1000). Verify: `docker run --rm --entrypoint id <api-image>` → `uid=1000(appuser)`.
  - **Compose bind-mount dev** (`./backend:/app`, reload command): process UID is **not** taken from host file ownership. Compose sets `user: "${API_UID:-1000}:${API_GID:-1000}"` so the API stays non-root even with a stale image built before `USER` was added (those older images ran as root — `docker inspect` showed empty `Config.User` and `docker compose exec api id` → `uid=0`). After Dockerfile/`user:` changes: `docker compose build --no-cache api && docker compose up -d api` (or `up --build --force-recreate api`). Verify: `docker compose exec -T api id` → `uid=1000(appuser)` (or numeric `1000` when Compose `user:` is set); `curl -sf http://127.0.0.1:8000/readyz`. Match host ownership on Linux if bind writes fail: `API_UID=$(id -u) API_GID=$(id -g)`. macOS Docker Desktop usually tolerates uid 1000 on host-owned mounts.
  - **Frontend** (`frontend/Dockerfile`): `USER node` (uid 1000). Image `chown`s `/app` (and pre-creates `.next`) so Compose anonymous volumes for `node_modules` / `.next` inherit non-root ownership. Verify: `docker compose exec -T frontend id` → `uid=1000(node)`. If a stale image still runs as root, rebuild/recreate: `docker compose build --no-cache frontend && docker compose up -d frontend`. SSR uses `INTERNAL_API_URL` (Compose default `http://api:8000`); browser uses `NEXT_PUBLIC_API_URL`. Smoke: `GET /en/explorer` → 200.
- Security response headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`); disable with `SECURITY_HEADERS_ENABLED=false` (e.g. tests).
- No secrets in git; `.env` ignored.
- Connectors that need credentials stay non-runnable until authorized ([ADR-003](decisions/ADR-003-authorized-connectors-only.md)).
- LLM outputs validated with Pydantic; rates are never invented by LLM path ([ADR-002](decisions/ADR-002-classification-modes.md)).
- MCP: prefer `DATABASE_URL_READONLY` ([mcp/CURSOR.md](mcp/CURSOR.md)).

## Observability

- Structured JSON logs via structlog.
- Collection runs persisted with error summaries.
- Data quality page for coverage/missingness.
- Ops snapshot: `GET /api/v1/ops/metrics` (observed DB counters only).
- Smoke: `./backend/scripts/smoke_e2e.sh` (includes ops/metrics). Demand Compass §11: `./backend/scripts/smoke_compass.sh` (or `COMPASS_SMOKE=1 ./backend/scripts/smoke_e2e.sh`). Local compose relaunch runs nested compass by default (`COMPASS_SMOKE=1` in `./scripts/compose_stack_relaunch.sh`; opt out with `COMPASS_SMOKE=0`). UI ops path: [ops/demand-compass-walkthrough.md](ops/demand-compass-walkthrough.md).

## Definition of Done (release slice)

- [x] Module acceptance criteria in relevant `SPEC-*` met (ops/sources/mcp/dashboard slices)
- [x] `pytest -q` green (63)
- [x] `./backend/scripts/smoke_e2e.sh` green against running API
- [x] `./backend/scripts/backup_smoke.sh` + `restore_smoke.sh` green
- [x] `cd frontend && npm run build` green
- [x] No secrets committed; `.env.example` updated if new env vars
- [x] Source files remain ≤ 500 lines
- [x] Docs updated when behavior or ops constraints change

## Verification checklist

```bash
docker compose up -d db redis
cd backend && source .venv/bin/activate
pytest -q
./scripts/backup_smoke.sh
./scripts/restore_smoke.sh
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
./scripts/smoke_e2e.sh
./scripts/smoke_compass.sh    # Demand Compass (SPEC-research-intents §11)
./scripts/scheduler_tick.sh   # optional cron smoke
# force tick: curl -sf -X POST "$API_URL/api/v1/scheduler/run?force=true"
cd ../frontend && npm run build
# Full Compose stack (db+redis+api+frontend), throttled every 30m by default:
#   ./scripts/compose_stack_relaunch.sh          # includes smoke_e2e + Demand Compass
#   COMPOSE_STACK_FORCE=1 ./scripts/compose_stack_relaunch.sh
#   COMPASS_SMOKE=0 ./scripts/compose_stack_relaunch.sh   # skip nested compass
```

## Known limits

- Source coverage is partial; dashboards show observed DB records only ([ADR-001](decisions/ADR-001-evidence-first-kpis.md)).
- Global catalog (~193) includes many `NEEDS_CREDENTIALS` / `UNDER_REVIEW` entries—see [sources/COVERAGE_GAPS.md](sources/COVERAGE_GAPS.md). Only `ACTIVE` connectors ingest jobs ([ADR-003](decisions/ADR-003-authorized-connectors-only.md), [ADR-005](decisions/ADR-005-global-source-catalog.md)).
- In-memory rate limit is single-node; use `RATE_LIMIT_BACKEND=redis` for multi-replica.
- LinkedIn/Malt/Indeed/Upwork/etc. still need partnerships. Adzuna/USAJOBS/France Travail/Bundesagentur/Jooble are scaffolded — set env keys, live-run, then ACTIVE ([sources/CREDENTIALED_CONNECTORS.md](sources/CREDENTIALED_CONNECTORS.md); `GET /api/v1/ops/connectors`). Reed is free via public RSS.
- Dashboard Guided / Trends-only + Prefs (+ profile sync) are shipped ([ADR-004](decisions/ADR-004-dashboard-modes.md)).
- ATS boards only cover **configured** tenants (`GREENHOUSE_BOARDS`, `LEVER_SITES`, `ASHBY_ORGS`, `SMARTRECRUITERS_COMPANIES`, `PERSONIO_COMPANIES`).
- MCP analytics: `python -m app.mcp` — [specs/SPEC-mcp-analytics.md](specs/SPEC-mcp-analytics.md); Cursor wiring [mcp/CURSOR.md](mcp/CURSOR.md).
