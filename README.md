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
```

- API docs: http://localhost:8000/docs
- UI: http://localhost:3000

Production hardening notes: [docs/PRODUCTION.md](docs/PRODUCTION.md)

## Bootstrap data

1. Open **Sources** and run **Remotive** / **Arbeitnow** (public APIs).
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
- PostgreSQL schema (sources, jobs, skills, rates, snapshots, metrics, profile, applications, alerts, audit)
- Remotive + Arbeitnow collectors; CSV/JSON/XLSX import; dedup
- Rules / hybrid / LLM classification with provider abstraction
- KPI summary, rates, countries, co-occurrence, skill gaps, positioning recommendations
- Applications / outcomes, alert evaluate, in-process scheduler (`ENABLE_SCHEDULER`)
- Weekly report JSON, rate limiting, optional `API_KEY`, structured logs
- Smoke script + CI

Explicit residual limits (not bugs):

- LinkedIn / Malt / Indeed / Upwork need authorized credentials or partnerships
- In-memory rate limit and scheduler are single-node (use external cron for multi-replica)
- LLM evaluation is rules self-consistency (no gold-label F1 UI yet)
- Weekly report is JSON (PDF export not shipped)

## Legal / ethics

No scraping that bypasses auth, CAPTCHA, paywall, or ToS. Connectors that are not authorized remain non-runnable with explicit status.
