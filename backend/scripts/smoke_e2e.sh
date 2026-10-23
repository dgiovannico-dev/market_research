#!/usr/bin/env sh
set -eu
API="${API_URL:-http://127.0.0.1:8000}"

# Liveness (process up; no DB) + readiness aliases (DB; Redis when rate_limit_backend=redis)
curl -sf "$API/livez" >/dev/null
curl -sf "$API/readyz" >/dev/null
curl -sf "$API/healthz" >/dev/null
curl -sf "$API/api/v1/health" >/dev/null
curl -sf "$API/api/v1/dashboard/summary" >/dev/null
curl -sf "$API/api/v1/market/rates" >/dev/null
curl -sf "$API/api/v1/market/countries" >/dev/null
curl -sf "$API/api/v1/market/skills/cooccurrence" >/dev/null
curl -sf "$API/api/v1/profile/skill-gaps" >/dev/null
curl -sf "$API/api/v1/reports/weekly" >/dev/null
curl -sf "$API/api/v1/llm/status" >/dev/null
curl -sf "$API/api/v1/sources/catalog/summary" >/dev/null
curl -sf "$API/api/v1/fx/rates" >/dev/null
curl -sf "$API/api/v1/ops/metrics" >/dev/null
curl -sf "$API/api/v1/ops/connectors" >/dev/null
curl -sf "$API/api/v1/profile/dashboard-prefs" >/dev/null
curl -sf "$API/api/v1/taxonomy/esco/search?q=software%20engineer&limit=2" >/dev/null
curl -sf "$API/api/v1/taxonomy/jobtech/search?q=python&type=skill&limit=2" >/dev/null
curl -sf "$API/api/v1/stats/eurostat/series?dataset=earn_ses_hourly&geo=DE&limit=2" >/dev/null
curl -sf -X POST "$API/api/v1/alerts/evaluate" >/dev/null
curl -sf -X POST "$API/api/v1/llm/evaluation/run?limit=10" >/dev/null
curl -sf -X POST "$API/api/v1/llm/evaluation/gold" >/dev/null

# Demand Compass — HTTP 200 + JSON shape only (empty DB / thin sample OK)
curl -sf "$API/api/v1/research/intents" | python3 -c '
import json, sys
d = json.load(sys.stdin)
assert isinstance(d.get("items"), list), "research/intents: items"
assert isinstance(d.get("total"), int), "research/intents: total"
'
curl -sf "$API/api/v1/dashboard/summary?lens=market" | python3 -c '
import json, sys
d = json.load(sys.stdin)
assert d.get("lens") == "market", "dashboard/summary: lens"
assert isinstance(d.get("kpis"), list), "dashboard/summary: kpis"
'
curl -sf -X POST "$API/api/v1/assistant/brief" \
  -H "Content-Type: application/json" \
  -d '{"brief_type":"rising_cooling","lens":"market"}' | python3 -c '
import json, sys
d = json.load(sys.stdin)
assert d.get("kind") == "brief", "assistant/brief: kind"
b = d.get("brief") or {}
for key in (
    "brief_type", "lens", "sample_size", "evidence",
    "narrative", "limits", "methodology_version", "status",
):
    assert key in b, f"assistant/brief: missing {key}"
assert b["brief_type"] == "rising_cooling"
assert isinstance(b["evidence"], list)
assert isinstance(b["narrative"], str)
assert b["status"] in ("ok", "thin_sample", "refused")
'

# Full Demand Compass acceptance (SPEC-research-intents §11): COMPASS_SMOKE=1
if [ "${COMPASS_SMOKE:-0}" = "1" ]; then
  SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  API_URL="$API" "$SCRIPT_DIR/smoke_compass.sh"
fi

# Geo connector country_code DSS (Plan D): GEO_SMOKE=1 (default 0 — avoid CI flake)
if [ "${GEO_SMOKE:-0}" = "1" ]; then
  SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  API_URL="$API" "$SCRIPT_DIR/smoke_geo_country.sh"
fi

echo "smoke_e2e OK against $API"
