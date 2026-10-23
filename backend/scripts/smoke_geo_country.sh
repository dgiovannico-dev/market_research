#!/usr/bin/env sh
# Geo connector Job.country_code DSS smoke (Plan D).
#
# Asserts known-country share ≥ 95% for ISO-tagged connectors when jobs exist:
#   okemprego (PT/BR/AO), jobbank_ca (CA), viewjobs (AU), devglobaljobs (LU/BG).
# Soft-SKIP when a connector has zero rows (empty DB / not crawled yet).
#
# Usage:
#   API_URL=http://127.0.0.1:8000 ./backend/scripts/smoke_geo_country.sh
#   # or pipe quality JSON:
#   curl -sf "$API/api/v1/market/quality?lens=all" | ./backend/scripts/smoke_geo_country.sh --stdin
#
# Exit codes:
#   0  all present sources PASS, or every source SKIP
#   1  hard FAIL (known country share below threshold) or bad/missing API response
#   2  missing dependency (curl / python3)
#
# Optional from smoke_e2e: GEO_SMOKE=1
set -eu

API="${API_URL:-http://127.0.0.1:8000}"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
BACKEND_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

command -v python3 >/dev/null 2>&1 || {
  echo "smoke_geo_country: python3 required" >&2
  exit 2
}

USE_STDIN=0
for arg in "$@"; do
  case "$arg" in
    --stdin) USE_STDIN=1 ;;
  esac
done

if [ "$USE_STDIN" = "1" ]; then
  PYTHONPATH="$BACKEND_ROOT" python3 -m app.ops.geo_country_smoke --stdin
  exit $?
fi

command -v curl >/dev/null 2>&1 || {
  echo "smoke_geo_country: curl required" >&2
  exit 2
}

# Prefer fetch inside the module (clear errors); shell still probes readiness lightly.
curl -sf "$API/readyz" >/dev/null || {
  echo "smoke_geo_country FAIL: GET $API/readyz" >&2
  exit 1
}

PYTHONPATH="$BACKEND_ROOT" python3 -m app.ops.geo_country_smoke --api-url "$API"
exit $?
