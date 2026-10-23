# Spec: ops

## Objective

Provide production-safe runtime controls: configuration, optional API key, rate limiting, **daily crawler scheduling**, CI, logging, and backup scripts.

## In scope

- Settings via env (see `.env.example`) including connector/ATS/FX-related vars (`GREENHOUSE_BOARDS`, `LEVER_SITES`, `ASHBY_ORGS`, FX base, etc.).
- **Sync budgets** (not topic strings): `SYNC_MAX_DISCOVERY_PER_TICK`, `SYNC_MAX_FOCUS_PER_TICK`, `SYNC_MAX_COLLECTOR_CALLS_PER_INTENT`, `SYNC_MAX_TOTAL_COLLECTOR_CALLS_PER_TICK`.
- **Discovery topics** live in `data/research/discovery_watchlist.json` (seeded to DB), not env.
- **Deprecated for product sync:** `*_DEFAULT_QUERY` / `*_DEFAULT_WHAT` / `*_DEFAULT_TAG` ([ADR-007](../decisions/ADR-007-query-first-sync.md)). Optional `OPS_SMOKE_QUERY` for explicit smoke only—never used by the daily tick.
- Optional `API_KEY` dependency on protected routes.
- Rate limit: `RATE_LIMIT_PER_MINUTE` + `RATE_LIMIT_BACKEND=memory|redis`.
- **Daily crawlers (required for Demand Compass in production):** external cron (recommended cadence: once daily) → `backend/scripts/scheduler_tick.sh` → `POST /api/v1/scheduler/run` → dump → discovery → focus collectors ([SPEC-research-intents.md](SPEC-research-intents.md) §6).
- `ENABLE_SCHEDULER=true` only on a **single** replica if cron is unavailable; prefer `ENABLE_SCHEDULER=false` + cron when scaled.
- Crawler tick must record `collection_runs` and surface failures in `GET /api/v1/ops/metrics` / logs.
- `GET /api/v1/ops/metrics` observed counters; `GET /api/v1/ops/connectors` credential booleans.
- Public probes (no API key): `GET /livez` (liveness); `GET /readyz` and `GET /healthz` (readiness — same handler; DB ping, Redis when required; HTTP 503 when down).
- Taxonomy (free): `GET /api/v1/taxonomy/esco/search`, `GET /api/v1/taxonomy/jobtech/search` — reference labels only, not KPIs.
- Stats (free): `GET /api/v1/stats/eurostat/series` — official statistics reference only; never mixed into observed job KPIs.
- Structured logging (structlog); collection run error summaries.
- GitHub Actions CI: pytest + frontend build.
- DB backup/restore + `backup_smoke.sh` / `restore_smoke.sh` (schema dump + restore into disposable temp DB).
- Promote credentialed sources after live inserts: `scripts/promote_source_active.py`.
- Seed sync for global catalog (`POST /api/v1/admin/seed`).
- Production checklist in [../PRODUCTION.md](../PRODUCTION.md).
- MCP stdio + `DATABASE_URL_READONLY` ([../mcp/CURSOR.md](../mcp/CURSOR.md)).

## Out of scope (Later)

- Full OAuth2/OIDC.
- Kubernetes manifests.
- Prometheus scrape format (JSON metrics endpoint is enough for now).

## Acceptance criteria

- [x] App starts with `ENABLE_SCHEDULER=false` in CI and local tests.
- [x] Smoke script passes against a running API (includes ops/metrics + ops/connectors + gold eval).
- [x] CI workflow exists and uses service Postgres.
- [x] No secrets committed; `.env` gitignored; `.cursor/mcp.json` gitignored.
- [x] PRODUCTION.md lists TLS, CORS, cron vs in-process scheduler, Redis rate limit.
- [x] Rate limit tests cover 429; Redis backend falls back to memory.
- [x] `/livez` liveness + `/readyz`/`/healthz` readiness (503 when DB/required Redis down); backup_smoke.sh / restore_smoke.sh verify dump + restore path.
- [x] Daily/ops collect does not substitute Settings topic defaults when query/intent is omitted.
- [x] Scheduler/crawler summary exposes intents processed and skips (`missing_query`, budget).
- [ ] PRODUCTION.md documents **daily cron** as the normative crawler trigger for source freshness.

## Key paths

- `backend/app/core/config.py`
- `backend/app/core/middleware.py`
- `backend/app/main.py`
- `backend/app/scheduler/runner.py`
- `.github/workflows/ci.yml`
- `backend/scripts/`
- Plan: [../superpowers/plans/2026-10-20-production-hardening.md](../superpowers/plans/2026-10-20-production-hardening.md)
- Query-first: [SPEC-research-intents.md](SPEC-research-intents.md), [../superpowers/plans/2026-10-20-query-first-daily-sync.md](../superpowers/plans/2026-10-20-query-first-daily-sync.md)
- Demand Compass ops walkthrough: [../ops/demand-compass-walkthrough.md](../ops/demand-compass-walkthrough.md)
