# Production Hardening Implementation Plan

> **For agentic workers:** Implement task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make FMI safer to run on more than one API replica and clearer to operate in production.

**Architecture:** Keep single-process defaults; add documented external cron entrypoint, optional Redis-backed rate limit, and a lightweight metrics/health expansion. No Kubernetes in this plan.

**Tech Stack:** FastAPI, existing Redis service in Compose, GitHub Actions

**Spec:** [docs/specs/SPEC-ops.md](../../specs/SPEC-ops.md), [docs/PRODUCTION.md](../../PRODUCTION.md)

## Global Constraints

- Scheduler must not run on every replica when horizontally scaled.
- No secrets in git.
- ≤500 lines per file.

## Review Focus

- Double collection if two replicas enable in-process scheduler.
- Rate-limit bypass via multiple instances without Redis.
- CORS misconfiguration in prod.
- Backup restore smoke path.

---

### Task 1: External scheduler contract

**Files:**
- Modify: `backend/app/api/v1/ops.py` (document `POST /scheduler/run`)
- Create or modify: `backend/scripts/scheduler_tick.sh`
- Modify: `docs/PRODUCTION.md`

**Steps:**
- [x] Script curls `POST /api/v1/scheduler/run` with optional API key
- [x] PRODUCTION.md: prefer cron + `ENABLE_SCHEDULER=false` for multi-replica
- [x] Shipped (no separate commit required in this working tree)

---

### Task 2: Optional Redis rate limit

**Files:**
- Modify: `backend/app/core/middleware.py` and/or new `backend/app/core/rate_limit.py`
- Modify: `backend/app/core/config.py`, `.env.example`

**Steps:**
- [x] If `REDIS_URL` set and flag enabled, use Redis counter; else in-memory
- [x] Tests for limit header/status 429 behavior
- [x] Shipped

---

### Task 3: Ops metrics snapshot

**Files:**
- Modify: `backend/app/api/v1/router.py` or ops router
- Modify: smoke script

**Steps:**
- [x] `GET /api/v1/ops/metrics` with job counts, last collection success, error counters (observed DB only)
- [x] Extend smoke_e2e
- [x] Shipped (`/ops/connectors`, `/healthz`, `backup_smoke.sh` follow-ons)
- [x] `restore_smoke.sh` + `psql_cmd.sh` (temp-DB schema restore; primary untouched)

---

### Task 4: Liveness vs readiness probes

**Files:**
- Create: `backend/app/core/health.py`
- Modify: `backend/app/main.py`, `backend/app/core/middleware.py`, `docker-compose.yml`
- Modify: `docs/PRODUCTION.md`, tests

**Steps:**
- [x] `GET /livez` — process liveness (always 200)
- [x] `GET /readyz` + `GET /healthz` — readiness (same handler; DB; Redis when `RATE_LIMIT_BACKEND=redis`); **503** when required deps down
- [x] Compose `api` healthcheck on `/readyz`; frontend `depends_on` healthy api
- [x] Unit tests for ready/not_ready; smoke path asserts 200 + `probe=ready`

## Checkpoint

- [x] pytest + smoke green
- [x] PRODUCTION.md matches runtime advice
- [x] backup_smoke + restore_smoke green against Compose Postgres

## Residual (not in this plan / later slices)

- [x] Dockerfile non-root user (api `USER appuser` uid 1000 + frontend `USER node`)
- [x] Security response headers middleware (`SecurityHeadersMiddleware`: X-Content-Type-Options, X-Frame-Options, Referrer-Policy)
- [x] Safer prod CORS defaults (reject `*` / empty when `APP_ENV=production|prod`)
- [x] SPEC-ops: crawler summary exposes intents processed / skips
- [x] SPEC-ops: collect path never substitutes deprecated `*_DEFAULT_QUERY`
- [x] `COMPASS_SMOKE` default-on in `scripts/compose_stack_relaunch.sh` (opt out `COMPASS_SMOKE=0`)
- [ ] CSP / HSTS at reverse proxy (not set in Starlette middleware)
