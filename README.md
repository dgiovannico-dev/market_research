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

## Bootstrap data

1. Open **Sources & LLM** and run **Remotive** / **Arbeitnow** (public APIs).
2. Or import sample CSV:

```bash
curl -F "file=@data/samples/jobs_sample.csv" http://localhost:8000/api/v1/imports
```

## Classification modes

- `CLASSIFICATION_MODE=rules|hybrid|llm` (default hybrid; MVP uses deterministic rules when LLM is `none`)
- `LLM_PROVIDER=none|ollama|vllm`

Platform works fully with LLM offline.

## Evidence model

Every classification/KPI carries an evidence kind:

- observed / extracted / inferred / derived / estimated / manually_verified

Missing rates are stored as `NULL`, never zero.

## Tests

```bash
cd backend && source .venv/bin/activate
pytest -q
```

## Backup / restore

```bash
./backend/scripts/backup_db.sh
./backend/scripts/restore_db.sh data/exports/<backup>.sql
```

## Current MVP scope / limits

Implemented:

- Modular backend + Next.js dashboards (Executive, Explorer, Trends, Jobs, Quality, Sources)
- PostgreSQL schema for sources, jobs, skills, rates, snapshots, metrics, profile, alerts, audit
- Remotive + Arbeitnow collectors
- Manual CSV/JSON/XLSX import with column mapping defaults
- Dedup by source id, canonical URL, description hash
- Rules-based classification + taxonomy
- KPI summary with definitions, sample size, limits
- Export CSV/JSON
- LLM provider abstraction (Ollama/vLLM/none)
- Unsupported sources declared (`requires_credentials` / `unsupported`)

Not fully implemented yet (planned next slices):

- Personal applications outcomes UI/API depth
- Alert scheduler workers
- LLM evaluation dataset UI
- Co-occurrence graph viz
- PDF reports
- Authorized connectors for LinkedIn/Malt/Indeed/Upwork (need credentials/partnerships)

## Legal / ethics

No scraping that bypasses auth, CAPTCHA, paywall, or ToS. Connectors that are not authorized remain non-runnable with explicit status.
