#!/usr/bin/env sh
set -eu
API="${API_URL:-http://127.0.0.1:8000}"

curl -sf "$API/api/v1/health" >/dev/null
curl -sf "$API/api/v1/dashboard/summary" >/dev/null
curl -sf "$API/api/v1/market/rates" >/dev/null
curl -sf "$API/api/v1/market/countries" >/dev/null
curl -sf "$API/api/v1/market/skills/cooccurrence" >/dev/null
curl -sf "$API/api/v1/profile/skill-gaps" >/dev/null
curl -sf "$API/api/v1/reports/weekly" >/dev/null
curl -sf "$API/api/v1/llm/status" >/dev/null
curl -sf -X POST "$API/api/v1/alerts/evaluate" >/dev/null
curl -sf -X POST "$API/api/v1/llm/evaluation/run?limit=10" >/dev/null
echo "smoke_e2e OK against $API"
