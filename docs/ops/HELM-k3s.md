# Deploy FMI on k3s with Helm

This guide is for **operators** who run a production-shaped FMI stack on k3s: build images, install the chart, smoke Ingress, and optionally wire external Postgres, Valkey, or Keycloak.

**Related docs:** [architecture/OVERVIEW.md](../architecture/OVERVIEW.md), [architecture/DATABASE.md](../architecture/DATABASE.md), [KEYCLOAK.md](KEYCLOAK.md), [RELEASE.md](RELEASE.md), [LOCAL.md](LOCAL.md), [RUNBOOKS.md](RUNBOOKS.md). Chart source: [`deploy/helm/fmi`](../../deploy/helm/fmi).

**Not covered here:** Day-one local `.env` setup (see [LOCAL.md](LOCAL.md)) or detailed auth troubleshooting (see [RUNBOOKS.md §4–§6](RUNBOOKS.md)).

---

## Why Valkey instead of Redis

Redis Community editions moved to RSALv2/SSPL. FMI uses **Valkey** (`valkey/valkey`, BSD-3-Clause) as the Redis-protocol backend. The API still sets `RATE_LIMIT_BACKEND=redis` and `REDIS_URL=redis://…` — the client speaks RESP; the server is Valkey.

Postgres uses the official `postgres:16-alpine` image (no Bitnami dependency).

---

## Workload architecture

Traefik (default k3s Ingress) terminates HTTP(S) on two hostnames and routes to frontend and API. Stateful data lives in PVC-backed StatefulSets; the API runs migrations before serving traffic.

```mermaid
flowchart TB
  subgraph ingress [Ingress Traefik]
    FEHost["Host: fmi.example"]
    APIHost["Host: api.fmi.example"]
  end
  subgraph fmi_ns [Namespace fmi]
    FE[Deployment frontend<br/>next start]
    API[Deployment api<br/>FastAPI]
    PG[(StatefulSet postgres)]
    VK[(StatefulSet valkey)]
    CJ[CronJob scheduler<br/>POST /scheduler/run]
    MJ[Job migrate hook<br/>alembic upgrade head]
  end
  Browser([Browser]) --> FEHost --> FE
  Browser --> APIHost --> API
  FE -->|SSR optional in-cluster| API
  API --> PG
  API --> VK
  CJ -->|X-API-Key| API
  MJ --> PG
  API -.->|initContainer| PG
```

| Workload | Role |
|----------|------|
| StatefulSet `postgres` | Primary DB + PVC |
| StatefulSet `valkey` | Rate-limit / shared cache |
| Deployment `api` | FastAPI; initContainer runs `alembic upgrade head` |
| Job `*-migrate` | Helm post-install/upgrade hook (idempotent) |
| Deployment `frontend` | Next.js `next start` |
| Ingress | Dual host → FE + API (Traefik) |
| CronJob `*-scheduler` | Daily `POST /api/v1/scheduler/run` (API has `ENABLE_SCHEDULER=false`) |

**Why scheduler is a CronJob:** the API Deployment stays horizontally scalable without duplicate in-process ticks. Set `ENABLE_SCHEDULER=false` on the API pod; the CronJob uses `X-API-Key`.

Config split: non-secret API env in ConfigMap; `DATABASE_URL`, `REDIS_URL`, `API_KEY`, `OPS_API_TOKEN`, `CREDENTIALS_MASTER_KEY` in Secret — see [RELEASE.md#environment-matrix](RELEASE.md#environment-matrix).

---

## Prerequisites

- k3s with Traefik Ingress (default)
- Helm 3.14+
- Docker (or another OCI builder) to build `fmi-api` / `fmi-frontend`
- DNS or `/etc/hosts` for the two Ingress hosts (frontend + API)

Optional: external Keycloak — [KEYCLOAK.md](KEYCLOAK.md).

---

## Build and load images

**Why bake the frontend:** `NEXT_PUBLIC_*` and OIDC flags are compile-time in `frontend/Dockerfile.prod`. Changing the public API URL without rebuilding leaves the UI pointing at the wrong host.

```bash
docker build -t fmi-api:0.1.0 ./backend

docker build -f frontend/Dockerfile.prod \
  --build-arg NEXT_PUBLIC_API_URL=https://api.fmi.local \
  -t fmi-frontend:0.1.0 ./frontend

# Single-node k3s without a registry
docker save fmi-api:0.1.0 | sudo k3s ctr images import -
docker save fmi-frontend:0.1.0 | sudo k3s ctr images import -
```

Rebuild the frontend image whenever the public API URL or `NEXT_PUBLIC_OIDC_*` changes.

Local chart lint (not in CI yet — run before install):

```bash
helm lint ./deploy/helm/fmi -f ./deploy/helm/fmi/ci/lint-values.yaml
```

Release sequence: [RELEASE.md](RELEASE.md).

---

## Install

Generate secrets at install time; do not commit them.

```bash
export PG_PASS="$(openssl rand -base64 24)"
export API_KEY="$(openssl rand -hex 16)"

helm upgrade --install fmi ./deploy/helm/fmi \
  -n fmi --create-namespace \
  --set secrets.postgresPassword="$PG_PASS" \
  --set secrets.apiKey="$API_KEY" \
  --set api.image.repository=fmi-api \
  --set api.image.tag=0.1.0 \
  --set frontend.image.repository=fmi-frontend \
  --set frontend.image.tag=0.1.0 \
  --set frontend.publicApiUrl=https://api.fmi.local \
  --set api.env.API_CORS_ORIGINS=https://fmi.local \
  --set ingress.hosts.frontend=fmi.local \
  --set ingress.hosts.api=api.fmi.local \
  --wait --timeout 10m
```

For production hostnames, replicas, and TLS, start from [`values-prod.example.yaml`](../../deploy/helm/fmi/values-prod.example.yaml) (copy privately; do not commit secrets).

**Optional Fernet key** for connector + LLM secrets at rest:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# helm ... --set secrets.credentialsMasterKey='…'
```

**Rollback note:** `helm rollback` reverts Kubernetes objects, not database schema. See [RELEASE.md#rollback](RELEASE.md#rollback).

---

## Smoke checklist

Prove pods, Ingress, and API readiness before handing off to users.

```bash
kubectl -n fmi get pods,ingress,cronjob

kubectl -n fmi wait --for=condition=ready pod \
  -l app.kubernetes.io/instance=fmi,app.kubernetes.io/component=api \
  --timeout=180s

kubectl -n fmi port-forward svc/fmi-api 8000:8000
curl -sf http://127.0.0.1:8000/livez
curl -sf http://127.0.0.1:8000/readyz

# One-shot crawler tick (same contract as backend/scripts/scheduler_tick.sh)
kubectl -n fmi create job --from=cronjob/fmi-api-scheduler "manual-tick-$(date +%s)"
```

With Ingress and hosts mapped:

```bash
curl -sf https://api.fmi.local/readyz   # or http:// if TLS disabled
curl -sfI https://fmi.local/
```

Demand Compass smoke:

```bash
API_URL=https://api.fmi.local ./backend/scripts/smoke_compass.sh
# with API_KEY if set on the cluster
```

---

## TLS

- Set `ingress.tls.enabled=true` and `ingress.tls.secretName` to an existing Secret, or
- Use cert-manager annotations on `ingress.annotations` (see `values-prod.example.yaml`).

Align `API_CORS_ORIGINS` with the **exact** frontend origin (scheme + host + port).

---

## External Postgres / Valkey

**Why disable in-chart StatefulSets:** managed databases or a shared Valkey cluster reduce operational burden on the k3s node.

```yaml
postgres:
  enabled: false
externalDatabase:
  url: "postgresql+psycopg://user:pass@host:5432/fmi"

valkey:
  enabled: false
externalValkey:
  url: "redis://valkey.example:6379/0"
```

Alternatively set `secrets.databaseUrl` directly in Helm values.

Schema and backup expectations: [architecture/DATABASE.md](../architecture/DATABASE.md), [RUNBOOKS.md §9](RUNBOOKS.md#9-backup--restore).

---

## Uninstall

```bash
helm uninstall fmi -n fmi
# PVCs for StatefulSets may remain — delete explicitly if desired
kubectl -n fmi delete pvc -l app.kubernetes.io/instance=fmi
```

**Warning:** deleting PVCs destroys Postgres data unless you have external backups.

---

## Compose vs Helm (decision summary)

| | Docker Compose | Helm / k3s |
|---|----------------|------------|
| Purpose | Local dev, bind mounts, `next dev` / `--reload` | Production-shaped deploy |
| Cache | Valkey service (`valkey/valkey:8-alpine`) | Valkey StatefulSet |
| Scheduler | Optional in-process (`ENABLE_SCHEDULER=true`) or manual tick | CronJob; `ENABLE_SCHEDULER=false` on API |
| Frontend API URL | Runtime env + dev server | Bake `NEXT_PUBLIC_*` in image; Ingress hostnames |
| Identity | OIDC off by default | External Keycloak — [KEYCLOAK.md](KEYCLOAK.md) |

Local path: [LOCAL.md](LOCAL.md). Incidents: [RUNBOOKS.md](RUNBOOKS.md).
