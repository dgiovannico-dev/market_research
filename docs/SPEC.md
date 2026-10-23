# Spec: Freelance Market Intelligence

## Objective

Build and maintain an evidence-first web app that collects authorized/public IT freelance job data from a **global verified source catalog**, classifies it, computes KPIs, and exposes customizable dashboards (guided evidence mode and trends-only mode) for a Senior AI & Backend freelance persona—worldwide geography, no invented access or rates.

Product detail: [PRODUCT.md](PRODUCT.md). Modules: [CAPABILITY_MAP.md](CAPABILITY_MAP.md). Sources: [specs/SPEC-sources.md](specs/SPEC-sources.md). Demand Compass: [ideas/freelance-demand-compass.md](ideas/freelance-demand-compass.md), [specs/SPEC-research-intents.md](specs/SPEC-research-intents.md) ([ADR-007](decisions/ADR-007-query-first-sync.md)). Experience IT/EN + charts: [ideas/demand-compass-experience.md](ideas/demand-compass-experience.md), [specs/SPEC-i18n.md](specs/SPEC-i18n.md), [specs/SPEC-dashboard.md](specs/SPEC-dashboard.md).

## Commands

```bash
# Infra
docker compose up -d db redis
cp .env.example .env

# Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://fmi:fmi_dev_password_change_me@localhost:5432/fmi
export ENABLE_SCHEDULER=false
alembic upgrade head
uvicorn app.main:app --reload --port 8000
pytest -q
./scripts/smoke_e2e.sh

# Frontend
cd frontend && npm ci && npm run dev
npm run build

# Full stack
docker compose up --build
```

## Project structure

```
backend/app/          → FastAPI (collectors, sources, fx, ingestion, classification, analytics, API, llm, scheduler, reports)
backend/alembic/      → Migrations
backend/tests/        → Pytest (incl. live collectors where marked)
backend/scripts/      → backup, smoke_e2e, generate_source_catalog
frontend/app/         → Next.js App Router pages (incl. Sources)
frontend/components/  → Client components
frontend/lib/         → API client
docs/                 → Product, specs, ADRs, plans, sources validation, production
tasks/                → Agent plan + todo checklist
data/sources/         → catalog.json (global registry)
data/samples/         → Import samples (not secrets)
```

## Code style

- Python 3.12+, type hints, SQLAlchemy 2 mapped columns, FastAPI routers split by module.
- Source files **≤ 500 lines**; split by responsibility (SOLID / SRP).
- TypeScript strict; prefer server components for data fetch; client only for mutations/prefs.
- Evidence kinds: `observed | extracted | inferred | derived | estimated | manually_verified`.
- Missing rates: `NULL`, never `0`.

Example (classification call site):

```python
result = classify_job(
    title=job.title_original,
    description=job.description_original,
    location=job.location_original,
)
```

## Testing strategy

| Level | Where | What |
|-------|-------|------|
| Unit | `backend/tests/test_*.py` | Normalization, classification, analytics helpers |
| Collectors / catalog | live + unit tests for ACTIVE sources | Real HTTP where public; no fake credentials |
| API smoke | `test_api_smoke.py` + `scripts/smoke_e2e.sh` | Health, market, catalog, profile, reports, eval |
| Frontend | `npm run build` | Typecheck + production build |
| CI | `.github/workflows/ci.yml` | Pytest (Postgres service) + Next build |

Coverage expectation: every new endpoint or analytics function has at least one automated check before merge.

## Boundaries

### Always do

- Run `pytest -q` and `npm run build` before claiming a slice done.
- Keep evidence metadata on classifications and KPIs.
- Document env vars in `.env.example`.
- Respect ≤500 lines per source file.
- Flip catalog status to `ACTIVE` only after real connector evidence ([ADR-003](decisions/ADR-003-authorized-connectors-only.md)).

### Ask first

- Schema migrations that drop columns or change evidence semantics.
- New third-party connectors or dependencies (must update catalog + validation report).
- Changing default `view_mode` or removing guided methodology copy from APIs.
- Enabling multi-tenant auth / OAuth.

### Never do

- Commit secrets (`.env`, API keys, passwords).
- Invent market totals or fabricate rates.
- Scrape behind login/CAPTCHA/paywall/ToS.
- Delete failing tests to “go green.”
- Claim Java/K8s/OAuth as shipped when only documented in Later.

## Module specs

See [CAPABILITY_MAP.md](CAPABILITY_MAP.md) for the index of `SPEC-*` files, including [specs/SPEC-research-intents.md](specs/SPEC-research-intents.md) (user intents → daily sync) and [specs/SPEC-mcp-analytics.md](specs/SPEC-mcp-analytics.md) (MCP → dashboards/reports).
