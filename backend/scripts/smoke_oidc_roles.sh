#!/usr/bin/env sh
# Smoke matrix for ADR-009 when OIDC is enabled.
# When OIDC_ENABLED is false/off, this script exits 0 after a short note.
set -eu
API="${API_URL:-http://127.0.0.1:8000}"

# Probe config via a public health endpoint; role checks need tokens from env.
if ! curl -sf "$API/readyz" >/dev/null; then
  echo "smoke_oidc_roles: API not ready at $API" >&2
  exit 1
fi

# Detect OIDC from env / tokens; otherwise require explicit tokens
if [ "${OIDC_ENABLED:-false}" != "true" ] && [ -z "${OIDC_USER_TOKEN:-}" ] && [ -z "${OIDC_ADMIN_TOKEN:-}" ]; then
  echo "smoke_oidc_roles: OIDC off / no tokens — skip (set OIDC_ENABLED=true + OIDC_USER_TOKEN / OIDC_ADMIN_TOKEN)"
  exit 0
fi

USER_TOK="${OIDC_USER_TOKEN:-}"
ADMIN_TOK="${OIDC_ADMIN_TOKEN:-}"
API_KEY_HDR=""
if [ -n "${API_KEY:-}" ]; then
  API_KEY_HDR="-H X-API-Key:${API_KEY}"
fi

# Machine key still works for scheduler-style routes
if [ -n "${API_KEY:-}" ]; then
  curl -sf $API_KEY_HDR "$API/api/v1/ops/metrics" >/dev/null
  echo "smoke_oidc_roles: API_KEY ok for ops/metrics"
fi

if [ -n "$USER_TOK" ]; then
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer ${USER_TOK}" \
    "$API/api/v1/dashboard/summary")
  test "$code" = "200" || { echo "user dashboard expected 200 got $code" >&2; exit 1; }
  # Non-admin must not mutate credentials (any connector key)
  code=$(curl -s -o /dev/null -w "%{http_code}" -X PUT \
    -H "Authorization: Bearer ${USER_TOK}" \
    -H "Content-Type: application/json" \
    -d '{"fields":{}}' \
    "$API/api/v1/ops/connectors/greenhouse/credentials")
  test "$code" = "403" || { echo "user PUT credentials expected 403 got $code" >&2; exit 1; }
  echo "smoke_oidc_roles: user JWT ok (dashboard 200, credentials 403)"
fi

if [ -n "$ADMIN_TOK" ]; then
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer ${ADMIN_TOK}" \
    "$API/api/v1/ops/connectors")
  test "$code" = "200" || { echo "admin connectors expected 200 got $code" >&2; exit 1; }
  echo "smoke_oidc_roles: admin JWT ok"
fi

echo "smoke_oidc_roles OK against $API"
