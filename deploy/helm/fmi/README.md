# FMI Helm chart (k3s, OSS-only)

Umbrella chart for Freelance Market Intelligence:

| Component | Image | License note |
|-----------|--------|--------------|
| API | `fmi-api` (backend Dockerfile) | App |
| Frontend | `fmi-frontend` (`frontend/Dockerfile.prod`) | App |
| Postgres | `postgres:16-alpine` | PostgreSQL License |
| Valkey | `valkey/valkey:8-alpine` | BSD-3 (Redis-compatible; not Redis SSPL) |
| Scheduler | `curlimages/curl` | CronJob → `POST /api/v1/scheduler/run` |

Ingress defaults to **Traefik** (`ingressClassName: traefik`) as shipped with k3s.

## Build images

```bash
# API
docker build -t fmi-api:0.1.0 ./backend

# Frontend — bake public API URL at build time
docker build -f frontend/Dockerfile.prod \
  --build-arg NEXT_PUBLIC_API_URL=https://api.fmi.example.com \
  -t fmi-frontend:0.1.0 ./frontend
```

Import into k3s (single-node, no registry):

```bash
docker save fmi-api:0.1.0 | sudo k3s ctr images import -
docker save fmi-frontend:0.1.0 | sudo k3s ctr images import -
```

## Lint

```bash
helm lint ./deploy/helm/fmi -f ./deploy/helm/fmi/ci/lint-values.yaml
```

## Install

```bash
helm upgrade --install fmi ./deploy/helm/fmi \
  -n fmi --create-namespace \
  --set secrets.postgresPassword="$(openssl rand -base64 24)" \
  --set api.image.tag=0.1.0 \
  --set frontend.image.tag=0.1.0 \
  --set frontend.publicApiUrl=https://api.fmi.local \
  --set api.env.API_CORS_ORIGINS=https://fmi.local \
  --set ingress.hosts.frontend=fmi.local \
  --set ingress.hosts.api=api.fmi.local \
  --wait --timeout 10m
```

Production: copy [`values-prod.example.yaml`](values-prod.example.yaml) to a private file and pass `-f` plus secrets via `--set` / Sealed Secrets.

## Ops notes

- `ENABLE_SCHEDULER=false` on API replicas; daily tick is the CronJob.
- `RATE_LIMIT_BACKEND=redis` with `REDIS_URL` pointing at Valkey.
- Migrations: API initContainer + optional post-install Job (`migrate.enabled`).
- Never commit real passwords; chart fails render if Postgres password is empty.

Full guide: [docs/ops/HELM-k3s.md](../../../docs/ops/HELM-k3s.md).
