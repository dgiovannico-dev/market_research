#!/usr/bin/env sh
# External cron entrypoint for multi-replica deployments.
# Prefer ENABLE_SCHEDULER=false on API replicas and schedule this script instead.
set -eu
API="${API_URL:-http://127.0.0.1:8000}"
HDR=""
if [ -n "${API_KEY:-}" ]; then
  HDR="-H X-API-Key:${API_KEY}"
fi
# shellcheck disable=SC2086
curl -sf -X POST $HDR "${API}/api/v1/scheduler/run"
echo
echo "scheduler_tick OK against ${API}"
