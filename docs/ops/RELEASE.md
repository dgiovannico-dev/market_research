# Release checklist (FMI)

This document is the **operator sequence** from green CI to running pods: build images, deploy Helm, smoke, and roll back safely. Deep install detail lives in [HELM-k3s.md](HELM-k3s.md); identity checks in [KEYCLOAK.md](KEYCLOAK.md).

**Related docs:** [LOCAL.md](LOCAL.md) (local parity commands), [RUNBOOKS.md](RUNBOOKS.md), [architecture/OVERVIEW.md](../architecture/OVERVIEW.md), CI [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml).

**Not covered here:** First-time k3s cluster bootstrap or Keycloak realm creation.

---

## Release pipeline (overview)

```mermaid
flowchart LR
  subgraph pre [Pre-merge]
    CI[GitHub Actions CI]
    Local[Local parity optional]
  end
  subgraph build [Build]
    APIImg[fmi-api image]
    FEImg[fmi-frontend image<br/>NEXT_PUBLIC baked]
  end
  subgraph deploy [Deploy]
    Helm[helm upgrade --install]
    Mig[alembic upgrade head<br/>initContainer + hook Job]
  end
  subgraph post [Post-deploy]
    Ready[/readyz + Ingress]
    Smoke[smoke_compass / e2e / OIDC]
    Sched[manual scheduler Job optional]
  end
  CI --> Local
  Local --> APIImg
  Local --> FEImg
  APIImg --> Helm
  FEImg --> Helm
  Helm --> Mig
  Mig --> Ready
  Ready --> Smoke
  Smoke --> Sched
  Sched --> Done([Release slice done])
```

**Why frontend is a separate build step:** any change to browser-visible API URL or `NEXT_PUBLIC_OIDC_*` requires a **frontend rebuild** — rolling API only leaves the UI stale.

---

## Pre-merge / CI gate

GitHub Actions on `main` / PRs (no Helm lint job in CI yet — run locally):

| Job | What runs |
|-----|-----------|
| `backend` | `alembic upgrade head`, `pytest -q`, `backup_smoke.sh`, `restore_smoke.sh` |
| `compass-smoke` | API on `:8000`, `smoke_compass.sh` (Demand Compass §11; offline-deterministic) |
| `frontend` | `npm ci`, `npm run test:unit`, `npm run build` (`NEXT_PUBLIC_API_URL=http://localhost:8000`) |

**Local parity before tagging** (same commands an operator can run on a laptop):

```bash
cd backend && alembic upgrade head && pytest -q
./scripts/backup_smoke.sh && ./scripts/restore_smoke.sh
API_URL=http://127.0.0.1:8000 ./scripts/smoke_e2e.sh
API_URL=http://127.0.0.1:8000 ./scripts/smoke_compass.sh
cd ../frontend && npm run build
helm lint ./deploy/helm/fmi -f ./deploy/helm/fmi/ci/lint-values.yaml
```

Update `.env.example` when new env vars ship. **Never** commit secrets.

---

## Build and tag images

```bash
export TAG=0.1.0   # semver or git sha

docker build -t fmi-api:$TAG ./backend
docker build -f frontend/Dockerfile.prod \
  --build-arg NEXT_PUBLIC_API_URL=https://api.<your-domain> \
  --build-arg NEXT_PUBLIC_OIDC_ENABLED=true \
  # ... other NEXT_PUBLIC_OIDC_* if OIDC enabled \
  -t fmi-frontend:$TAG ./frontend
```

Push to your registry (or `docker save | k3s ctr images import` on single-node).

**Rule:** Any change to browser-visible API URL or OIDC public config requires a **frontend rebuild**.

Image load and first install: [HELM-k3s.md](HELM-k3s.md).

---

## Deploy (Helm)

```bash
helm upgrade --install fmi ./deploy/helm/fmi -n fmi \
  -f /path/to/private-values.yaml \
  --set api.image.tag=$TAG \
  --set frontend.image.tag=$TAG \
  --set secrets.postgresPassword='…' \
  --set secrets.apiKey='…' \
  --set secrets.credentialsMasterKey='…' \
  --wait --timeout 10m
```

**Migrations:** API initContainer + optional migrate Job run `alembic upgrade head`. Policy is **forward-only** — no automatic downgrades on `helm rollback`. Plan Alembic reversions separately ([Alembic policy](#alembic-policy)).

Production overrides template: [`deploy/helm/fmi/values-prod.example.yaml`](../../deploy/helm/fmi/values-prod.example.yaml).

---

## Post-deploy smoke

Prove readiness before announcing the release:

```bash
curl -sf https://api.<domain>/readyz
curl -sfI https://<frontend-domain>/
API_URL=https://api.<domain> API_KEY=… ./backend/scripts/smoke_compass.sh
# Optional full e2e (external connectors): smoke_e2e.sh
kubectl -n fmi create job --from=cronjob/fmi-api-scheduler "post-release-$(date +%s)"
```

Verify crawler activity: `GET /api/v1/ops/metrics` → `crawler.last_tick` after the scheduler job.

OIDC enabled: run `smoke_oidc_roles.sh` against staging — [KEYCLOAK.md](KEYCLOAK.md).

Incidents during smoke: [RUNBOOKS.md](RUNBOOKS.md).

---

## Rollback

Rollback is **two-dimensional**: Kubernetes release revision **and** database schema revision **and** frontend bake.

1. **Helm release:** `helm rollback fmi <revision> -n fmi` (list: `helm history fmi -n fmi`).
2. **Image pin:** `helm upgrade … --set api.image.tag=<previous> --set frontend.image.tag=<previous>`.
3. **Schema:** If the failed release ran a **new** migration, rollback code to a tag that matches DB revision or apply a forward fix migration — Alembic does not auto-downgrade on helm rollback.
4. **Frontend URL mismatch:** Rolling back API only while frontend still points at wrong `NEXT_PUBLIC_API_URL` breaks the UI — redeploy matching frontend image.

When in doubt, prefer **forward fix** migration over `alembic downgrade` in production ([RUNBOOKS.md §2](RUNBOOKS.md#2-migrate-failed)).

---

## Environment matrix

| Variable | Local / Compose (`.env`) | Helm ConfigMap | Helm Secret | Prod required |
|----------|--------------------------|----------------|-------------|---------------|
| `DATABASE_URL` | Yes (host or `@db:5432` in compose override) | — | Yes (`fmi.databaseUrl`) | Yes |
| `REDIS_URL` | Yes (`localhost:6380` or `@valkey:6379`) | — | Yes | Yes if `RATE_LIMIT_BACKEND=redis` |
| `API_KEY` | Optional (empty = open machine paths in dev) | — | Recommended | Yes for scheduler/CronJob |
| `API_CORS_ORIGINS` | Yes (both localhost + 127.0.0.1) | Yes (`api.env`) | — | Yes (`APP_ENV=production`) |
| `APP_ENV` | `development` | Yes | — | `production` / `prod` |
| `OIDC_ENABLED` | `false` default | Yes (`oidc.enabled`) | — | If multi-user |
| `OIDC_ISSUER` | When OIDC on | Yes | — | When OIDC on |
| `OIDC_AUDIENCE` | When OIDC on | Yes | — | When OIDC on (or dev skip) |
| `OIDC_CLIENT_ID` | `fmi-frontend` | Yes | — | When OIDC on |
| `OIDC_REQUIRE_USER` | `false` local | Yes | — | Usually `true` prod |
| `NEXT_PUBLIC_API_URL` | `.env` / compose | Frontend env + **build-arg** | — | Yes (baked in prod image) |
| `NEXT_PUBLIC_OIDC_*` | When testing OIDC locally | Frontend env + build-arg | — | When OIDC on |
| `INTERNAL_API_URL` | Compose: `http://api:8000` | In-cluster service URL if set | — | SSR in K8s (optional if same as public) |
| `ENABLE_SCHEDULER` | `true` optional single replica | Yes (`false` prod) | — | `false` on API; use CronJob |
| `CREDENTIALS_MASTER_KEY` | When storing connector/LLM secrets | — | Yes | Yes if credentials or LLM keys in DB |

Also set via Secret when needed: `OPS_API_TOKEN`, connector API keys (`secrets.extra` / Sealed Secrets).

Database layout reference: [architecture/DATABASE.md](../architecture/DATABASE.md).

---

## Definition of done (release slice)

- CI green on target branch
- Images tagged and pushed (or imported to k3s)
- Helm upgrade succeeded; pods ready
- `/readyz` + compass smoke (and OIDC smoke if applicable)
- Ops docs updated when behaviour changes ([ops/](.))

---

## Alembic policy

- Ship migrations in the **same release** as code that depends on them.
- Run `alembic upgrade head` once per deploy (initContainer + hook).
- Never edit applied revision files in place; add new revisions.
- Failed migrate troubleshooting: [RUNBOOKS.md §2](RUNBOOKS.md#2-migrate-failed).
