# Freelance Market Intelligence (FMI)

Evidence-first web application for IT freelance market research: collect authorized/public job data, normalize, classify, compute KPI, and explore dashboards. Counts always mean **observed records in this database**, never invented total market size.

## Stack

- Backend: Python 3.12, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL
- Frontend: Next.js (TypeScript), Tailwind
- Optional: Redis, Ollama, vLLM
- Orchestration: Docker Compose

## Quick start

```bash
cp .env.example .env
docker compose up -d db redis
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://fmi:fmi_dev_password_change_me@localhost:5432/fmi
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

In another terminal:

```bash
cd frontend && npm install && npm run dev
```

Or full stack:

```bash
docker compose up --build
# Relaunch + health/smoke (throttled every 30m; force with COMPOSE_STACK_FORCE=1):
./scripts/compose_stack_relaunch.sh
```

Compose `api` runs as uid 1000 (`API_UID`/`API_GID`, default 1000) — same as image `USER appuser`. Bind mounts enable reload; they do not force root. Rebuild after Dockerfile user changes (`docker compose up --build`). See [docs/PRODUCTION.md](docs/PRODUCTION.md) § Security.

- API docs: http://localhost:8000/docs
- UI: http://localhost:3000 (prefer `localhost` over `127.0.0.1`, or list both in `API_CORS_ORIGINS`)
- Browser calls use `NEXT_PUBLIC_API_URL` (host-reachable, default `http://localhost:8000`). Compose SSR uses `INTERNAL_API_URL=http://api:8000` inside the frontend container — do not put the Docker service hostname in `NEXT_PUBLIC_*`.

## Documentation

Full product, specs, ADRs, roadmap, and agent task lists:

- **Index:** [docs/README.md](docs/README.md)
- **Product (persona, guided vs trends-only, customization):** [docs/PRODUCT.md](docs/PRODUCT.md)
- **Roadmap:** [docs/ROADMAP.md](docs/ROADMAP.md)
- **Production:** [docs/PRODUCTION.md](docs/PRODUCTION.md)
- **Global sources registry:** [docs/sources/README.md](docs/sources/README.md) · catalog [`data/sources/catalog.json`](data/sources/catalog.json)
- **Source validation / gaps:** [docs/sources/VALIDATION_REPORT.md](docs/sources/VALIDATION_REPORT.md) · [docs/sources/COVERAGE_GAPS.md](docs/sources/COVERAGE_GAPS.md)
- **Sources spec + expansion plan:** [docs/specs/SPEC-sources.md](docs/specs/SPEC-sources.md) · [docs/superpowers/plans/2026-10-20-global-sources.md](docs/superpowers/plans/2026-10-20-global-sources.md)
- **MCP analytics (Cursor):** [docs/mcp/CURSOR.md](docs/mcp/CURSOR.md) · [docs/specs/SPEC-mcp-analytics.md](docs/specs/SPEC-mcp-analytics.md)
- **Next implementation tasks:** [tasks/todo.md](tasks/todo.md)

## MCP analytics (stdio)

Schema metadata + semantic metrics for LLM-proposed dashboards/reports:

```bash
cd backend && source .venv/bin/activate
python -m app.mcp
```

Wire into Cursor via [docs/mcp/CURSOR.md](docs/mcp/CURSOR.md). Prefer `DATABASE_URL_READONLY` (SELECT-only).

## Bootstrap data

1. Open **Sources** and run public collectors (Remotive, Arbeitnow, Remote OK, Working Nomads, We Work Remotely, The Muse; Greenhouse/Lever if boards configured).
2. Or import sample CSV:

```bash
curl -F "file=@data/samples/jobs_sample.csv" http://localhost:8000/api/v1/imports
```

## Classification modes

- `CLASSIFICATION_MODE=rules|hybrid|llm` (default hybrid; uses deterministic rules when LLM is `none`)
- `LLM_PROVIDER=none|ollama|vllm`

Platform works fully with LLM offline. Sources page can run batch LLM classify and a rules consistency evaluation stub.

## Evidence model

Every classification/KPI carries an evidence kind:

- observed / extracted / inferred / derived / estimated / manually_verified

Missing rates are stored as `NULL`, never zero.

## Dashboards

Executive · Explorer · Trends · Skills (co-occurrence) · Rates · Countries · Jobs · Profile / skill gaps · Applications · Quality · Alerts · Weekly report · Sources & LLM

**Modes (specified; UI customization Next):**

- `guided` — evidence copy, definitions, limits, recommendations (current default UX)
- `trends_only` — charts/tables of observed trends without guidelines/recommendation panels

Prefs (period, widgets, focus filters, nav, presets) are specified in [docs/specs/SPEC-dashboard.md](docs/specs/SPEC-dashboard.md) and [ADR-004](docs/decisions/ADR-004-dashboard-modes.md).

## Tests & smoke

```bash
cd backend && source .venv/bin/activate
pytest -q
./scripts/smoke_e2e.sh
cd ../frontend && npm run build
```

CI runs the same backend pytest + frontend build on GitHub Actions.

## Backup / restore

```bash
./backend/scripts/backup_db.sh
./backend/scripts/restore_db.sh data/exports/<backup>.sql
```

## Production scope

Implemented:

- Modular FastAPI + Next.js analytics UI
- PostgreSQL schema (sources + catalog verification, jobs, skills, rates, snapshots, metrics, profile, applications, alerts, audit)
- Global ~193-source catalog (A–I) with honest statuses; ACTIVE public collectors (Remotive, Arbeitnow, Remote OK, Working Nomads, WWR, The Muse, Greenhouse/Lever/Ashby when configured); CSV/JSON/XLSX import; dedup; FX (Frankfurter/ECB)
- Credentialed scaffolds (env keys, fail closed, not ACTIVE until live): Adzuna, USAJOBS, Reed, France Travail, Bundesagentur, Jooble — [docs/sources/CREDENTIALED_CONNECTORS.md](docs/sources/CREDENTIALED_CONNECTORS.md); promote with `backend/scripts/promote_source_active.py`
- Rules / hybrid / LLM classification; gold-label eval + rules consistency; dashboard Guided / Trends-only + prefs (+ profile sync)
- MCP analytics stdio (`python -m app.mcp`); in-app Assistant propose/apply DashboardSpec
- KPI summary, rates, countries, co-occurrence, skill gaps, positioning recommendations
- Applications / outcomes, alert evaluate, scheduler tick script / optional in-process scheduler
- Weekly report JSON, rate limiting (memory|redis), optional `API_KEY`, ops metrics/connectors, structured logs
- Smoke script + CI

Explicit residual limits (not bugs):

- Most catalog entries are `NEEDS_CREDENTIALS` / `UNDER_REVIEW` — scaffolds need keys + live run before ACTIVE ([docs/sources/COVERAGE_GAPS.md](docs/sources/COVERAGE_GAPS.md))
- LinkedIn / Malt / Indeed / Upwork / etc. still need authorized partnerships (no connector yet)
- In-memory rate limit is single-node (use `RATE_LIMIT_BACKEND=redis` + external cron for multi-replica)
- Weekly report is JSON (PDF export not shipped)

## Legal / ethics

No scraping that bypasses auth, CAPTCHA, paywall, or ToS. Connectors that are not authorized remain non-runnable with explicit status.
