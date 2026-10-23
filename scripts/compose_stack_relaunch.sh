#!/usr/bin/env sh
# Relaunch full Docker Compose stack and verify API + frontend respond.
# Throttle: skip if last success was within COMPOSE_STACK_MIN_INTERVAL_MINUTES (default 30)
# unless COMPOSE_STACK_FORCE=1.
#
# Env:
#   COMPOSE_STACK_FORCE=1              ignore throttle
#   COMPOSE_STACK_MIN_INTERVAL_MINUTES throttle window (default 30)
#   COMPOSE_STACK_WAIT_SEC             health wait (default 180)
#   COMPOSE_STACK_SKIP_SMOKE=1         readyz + frontend only (no smoke_e2e)
#   COMPASS_SMOKE=0                    skip nested Demand Compass smoke (default 1 here)
#   API_URL / FRONTEND_URL             probe targets
set -eu
ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

INTERVAL_MIN="${COMPOSE_STACK_MIN_INTERVAL_MINUTES:-30}"
FORCE="${COMPOSE_STACK_FORCE:-0}"
STAMP_DIR="${COMPOSE_STACK_STAMP_DIR:-$ROOT/.cursor}"
STAMP_FILE="$STAMP_DIR/compose-stack-last-ok"
API_URL="${API_URL:-http://127.0.0.1:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://127.0.0.1:3000}"
WAIT_SEC="${COMPOSE_STACK_WAIT_SEC:-180}"

mkdir -p "$STAMP_DIR"

if [ "$FORCE" != "1" ] && [ -f "$STAMP_FILE" ]; then
  now="$(date +%s)"
  last="$(cat "$STAMP_FILE" 2>/dev/null || echo 0)"
  age_min=$(( (now - last) / 60 ))
  if [ "$age_min" -lt "$INTERVAL_MIN" ]; then
    echo "compose_stack_relaunch SKIP (last OK ${age_min}m ago; interval ${INTERVAL_MIN}m). Set COMPOSE_STACK_FORCE=1 to override."
    exit 0
  fi
fi

if [ ! -f "$ROOT/.env" ]; then
  echo "compose_stack_relaunch: missing .env — copy from .env.example first" >&2
  exit 1
fi

echo "compose_stack_relaunch: docker compose up --build -d ..."
docker compose -f "$ROOT/docker-compose.yml" up --build -d

echo "compose_stack_relaunch: waiting up to ${WAIT_SEC}s for health..."
deadline=$(( $(date +%s) + WAIT_SEC ))
api_ok=0
fe_ok=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  if curl -sf "$API_URL/readyz" >/dev/null 2>&1; then
    api_ok=1
  fi
  if curl -sf -o /dev/null "$FRONTEND_URL" >/dev/null 2>&1; then
    fe_ok=1
  fi
  if [ "$api_ok" -eq 1 ] && [ "$fe_ok" -eq 1 ]; then
    break
  fi
  sleep 3
done

if [ "$api_ok" -ne 1 ]; then
  echo "compose_stack_relaunch FAIL: API not ready at $API_URL/readyz" >&2
  docker compose -f "$ROOT/docker-compose.yml" ps >&2 || true
  exit 1
fi

if [ "$fe_ok" -ne 1 ]; then
  echo "compose_stack_relaunch FAIL: frontend not reachable at $FRONTEND_URL" >&2
  docker compose -f "$ROOT/docker-compose.yml" ps >&2 || true
  exit 1
fi

if [ "${COMPOSE_STACK_SKIP_SMOKE:-0}" != "1" ]; then
  # Nested Demand Compass §11 (smoke_compass via smoke_e2e). Opt out: COMPASS_SMOKE=0
  COMPASS_SMOKE="${COMPASS_SMOKE:-1}" API_URL="$API_URL" "$ROOT/backend/scripts/smoke_e2e.sh"
fi

date +%s > "$STAMP_FILE"
echo "compose_stack_relaunch OK (api=$API_URL frontend=$FRONTEND_URL)"
docker compose -f "$ROOT/docker-compose.yml" ps
