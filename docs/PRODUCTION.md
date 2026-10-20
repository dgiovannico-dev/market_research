# Production readiness

## Runtime

1. Configure secrets via environment / secret manager (`API_KEY`, `POSTGRES_PASSWORD`, LLM keys).
2. `ENABLE_SCHEDULER=true` only on a single API replica (in-memory scheduler; use external cron for multi-replica).
3. Put Postgres behind managed backups; use `backend/scripts/backup_db.sh` as baseline.
4. Set `API_CORS_ORIGINS` to the real frontend origin(s).
5. Terminate TLS at reverse proxy (Caddy/Nginx/Cloud LB).

## Security baseline

- Optional `API_KEY` header for private endpoints.
- In-memory rate limiting (`RATE_LIMIT_PER_MINUTE`).
- No secrets in git; `.env` ignored.
- Connectors that need credentials stay non-runnable until authorized.
- LLM outputs validated with Pydantic; rates are never invented by LLM path.

## Observability

- Structured JSON logs via structlog.
- Collection runs persisted with error summaries.
- Data quality page for coverage/missingness.

## Verification checklist

```bash
docker compose up -d db redis
cd backend && source .venv/bin/activate
pytest -q
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
./scripts/smoke_e2e.sh
cd ../frontend && npm run build
```

## Known limits

- Source coverage is partial; dashboards show observed DB records only.
- In-memory rate limit and scheduler are single-node.
- LinkedIn/Malt/Indeed/Upwork require authorized integrations.
