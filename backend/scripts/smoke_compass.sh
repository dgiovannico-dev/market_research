#!/usr/bin/env bash
# Demand Compass acceptance smoke — SPEC-research-intents §11 (automatable bits).
#
# Usage:
#   API_URL=http://127.0.0.1:8000 ./backend/scripts/smoke_compass.sh
#   API_KEY=... COMPASS_ACCEPT_WATCH=1 ./backend/scripts/smoke_compass.sh
#
# Exit codes:
#   0  all required checks passed (warnings allowed)
#   1  required check failed / bad response
#   2  missing dependency (curl)
#
# Optional: COMPASS_ACCEPT_WATCH=1  accept one proposed watch, then soft-DELETE it
# Force scheduler (manual; not run here):
#   curl -sf -X POST -H "X-API-Key: $API_KEY" \
#     "$API_URL/api/v1/scheduler/run?force=true"
#
# Soft rematch (never fails this smoke): when focus lens is empty after create,
#   docker compose exec api python scripts/rematch_focus_intents.py
# Script exit 1 = no enabled focus intents; exit 2 = 0 text candidates — both OK on empty DB.
set -euo pipefail

API="${API_URL:-http://127.0.0.1:8000}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACCEPT_WATCH="${COMPASS_ACCEPT_WATCH:-0}"
HAS_JQ=0
command -v curl >/dev/null 2>&1 || { echo "smoke_compass: curl required" >&2; exit 2; }
command -v jq >/dev/null 2>&1 && HAS_JQ=1

HDR=()
if [[ -n "${API_KEY:-}" ]]; then
  HDR=(-H "X-API-Key: ${API_KEY}")
fi

fail() { echo "smoke_compass FAIL: $*" >&2; exit 1; }
warn() { echo "smoke_compass WARN: $*" >&2; }
ok() { echo "smoke_compass OK: $*"; }

# shellcheck disable=SC2086
api_get() { curl -sf ${HDR[@]+"${HDR[@]}"} "$API$1"; }

api_post() {
  # shellcheck disable=SC2086
  curl -sf ${HDR[@]+"${HDR[@]}"} -H "Content-Type: application/json" \
    -X POST -d "$2" "$API$1"
}

json_total() {
  if [[ "$HAS_JQ" -eq 1 ]]; then
    echo "$1" | jq -r '.total // (.items | length) // 0'
  else
    echo "$1" | grep -o '"id":' | wc -l | tr -d ' '
  fi
}

# --- 1. probes: liveness (process) + readiness (DB / required Redis) ---
api_get "/livez" >/dev/null || fail "GET /livez"
ok "livez"
api_get "/healthz" >/dev/null || fail "GET /healthz"
ok "healthz"
api_get "/readyz" >/dev/null || fail "GET /readyz"
ok "readyz"

# --- 2. discovery intents (≥1 enabled or warn) ---
DISC="$(api_get "/api/v1/research/intents?kind=discovery")" \
  || fail "GET /api/v1/research/intents?kind=discovery"
if [[ "$HAS_JQ" -eq 1 ]]; then
  EN_DISC="$(echo "$DISC" | jq '[.items[]? | select(.enabled == true)] | length')"
else
  if echo "$DISC" | grep -q '"enabled": *true'; then EN_DISC=1; else EN_DISC=0; fi
fi
if [[ "${EN_DISC:-0}" -lt 1 ]]; then
  warn "no enabled discovery intents (seed/watchlist may be empty)"
else
  ok "discovery intents enabled=${EN_DISC}"
fi

# --- 3. dashboard summary lens=market ---
SUM="$(api_get "/api/v1/dashboard/summary?lens=market&days=30")" \
  || fail "GET dashboard/summary?lens=market"
if [[ "$HAS_JQ" -eq 1 ]]; then
  echo "$SUM" | jq -e '.lens == "market" and (.kpis | type == "array")' >/dev/null \
    || fail "summary missing lens=market or kpis[]"
else
  echo "$SUM" | grep -q '"lens": *"market"' || fail "summary missing lens=market"
  echo "$SUM" | grep -q '"kpis"' || fail "summary missing kpis"
fi
ok "dashboard/summary lens=market"

# --- 4. market trends ---
TRENDS="$(api_get "/api/v1/market/trends?lens=market")" \
  || fail "GET market/trends?lens=market"
if [[ "$HAS_JQ" -eq 1 ]]; then
  echo "$TRENDS" | jq -e 'type == "object"' >/dev/null || fail "trends not an object"
else
  [[ -n "$TRENDS" ]] || fail "trends empty"
fi
ok "market/trends lens=market"

# --- 5. rising_cooling brief ---
BRIEF="$(api_post "/api/v1/assistant/brief" \
  '{"brief_type":"rising_cooling","lens":"market","period_days":90}')" \
  || fail "POST assistant/brief rising_cooling"
if [[ "$HAS_JQ" -eq 1 ]]; then
  echo "$BRIEF" | jq -e '
    (.brief.sample_size // .sample_size) != null
    and ((.brief.narrative // .narrative) | type == "string" and length > 0)
  ' >/dev/null || fail "rising_cooling missing sample_size/narrative"
else
  echo "$BRIEF" | grep -q 'sample_size' || fail "rising_cooling missing sample_size"
  echo "$BRIEF" | grep -q 'narrative' || fail "rising_cooling missing narrative"
fi
ok "assistant/brief rising_cooling"

# --- 6. suggest_watches must NOT persist intents ---
ALL="$(api_get "/api/v1/research/intents")" || fail "GET research/intents"
BEFORE="$(json_total "$ALL")"
WATCH="$(api_post "/api/v1/assistant/brief" \
  '{"brief_type":"suggest_watches","lens":"market","period_days":90}')" \
  || fail "POST assistant/brief suggest_watches"
if [[ "$HAS_JQ" -eq 1 ]]; then
  echo "$WATCH" | jq -e '
    (.brief // .) | .brief_type == "suggest_watches"
      and (.sample_size != null)
      and ((.narrative | type == "string") and (.narrative | length > 0))
  ' >/dev/null || fail "suggest_watches bad payload"
else
  echo "$WATCH" | grep -q 'suggest_watches' || fail "suggest_watches missing type"
  echo "$WATCH" | grep -q 'sample_size' || fail "suggest_watches missing sample_size"
fi
ALL2="$(api_get "/api/v1/research/intents")" || fail "GET research/intents (after)"
AFTER="$(json_total "$ALL2")"
if [[ "$AFTER" -ne "$BEFORE" ]]; then
  fail "suggest_watches changed SearchQuery count (${BEFORE} → ${AFTER}); must not persist without accept"
fi
ok "suggest_watches (intents unchanged: ${BEFORE})"

# --- 7. optional accept + soft-delete ---
if [[ "$ACCEPT_WATCH" == "1" ]]; then
  if [[ "$HAS_JQ" -ne 1 ]]; then
    warn "COMPASS_ACCEPT_WATCH=1 needs jq; skip accept/delete"
  else
    CAND="$(echo "$WATCH" | jq -c '
      (.brief.proposed_intents // .proposed_intents // [])[0] // empty
    ')"
    if [[ -z "$CAND" || "$CAND" == "null" ]]; then
      warn "no proposed_intents; skip accept/delete"
    else
      NAME="$(echo "$CAND" | jq -r '.name // "smoke-watch"')"
      QTEXT="$(echo "$CAND" | jq -r '.query_text')"
      KIND="$(echo "$CAND" | jq -r '.kind // "focus"')"
      ACC="$(api_post "/api/v1/research/watches/accept" \
        "$(jq -n --arg n "$NAME" --arg q "$QTEXT" --arg k "$KIND" \
          '{name:$n, query_text:$q, kind:$k, enabled:true}')")" \
        || fail "POST research/watches/accept"
      WID="$(echo "$ACC" | jq -r '.id')"
      [[ -n "$WID" && "$WID" != "null" ]] || fail "accept missing id"
      ALL3="$(api_get "/api/v1/research/intents")" || fail "GET intents after accept"
      AFTER_ACC="$(json_total "$ALL3")"
      [[ "$AFTER_ACC" -gt "$AFTER" ]] || fail "accept did not increase intent count"
      # shellcheck disable=SC2086
      curl -sf ${HDR[@]+"${HDR[@]}"} -X DELETE "$API/api/v1/research/intents/${WID}" >/dev/null \
        || fail "DELETE research/intents/${WID}"
      ok "accepted watch id=${WID} then soft-deleted"
    fi
  fi
else
  echo "smoke_compass NOTE: set COMPASS_ACCEPT_WATCH=1 to exercise accept+soft-delete"
fi

# --- 8. soft rematch focus intents (optional; never fails smoke) ---
# Text-rematch historical jobs onto enabled focus intents. Empty DB / no focus /
# 0 candidates must not fail CI.
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
if command -v docker >/dev/null 2>&1 \
  && (cd "$REPO_ROOT" && docker compose ps --status running api 2>/dev/null | grep -q api); then
  set +e
  REMATCH_OUT="$(cd "$REPO_ROOT" && docker compose exec -T api python scripts/rematch_focus_intents.py 2>&1)"
  REMATCH_RC=$?
  set -e
  if [[ "$REMATCH_RC" -eq 0 ]]; then
    ok "rematch_focus_intents"
  else
    warn "rematch soft rc=${REMATCH_RC} (no focus intents / 0 candidates OK on empty DB): ${REMATCH_OUT%%$'\n'*}"
  fi
else
  echo "smoke_compass NOTE: when focus lens empty after create:"
  echo "  docker compose exec api python scripts/rematch_focus_intents.py"
fi

# --- 9. geo country DSS (soft: empty DB → all SKIP → exit 0) ---
GEO_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/smoke_geo_country.sh"
if [[ -x "$GEO_SCRIPT" ]] || [[ -f "$GEO_SCRIPT" ]]; then
  set +e
  QUAL_JSON="$(api_get "/api/v1/market/quality?lens=all" 2>/dev/null)"
  QUAL_RC=$?
  if [[ "$QUAL_RC" -eq 0 && -n "$QUAL_JSON" ]]; then
    echo "$QUAL_JSON" | "$GEO_SCRIPT" --stdin
    GEO_RC=$?
    set -e
    if [[ "$GEO_RC" -eq 0 ]]; then
      ok "smoke_geo_country (stdin quality; SKIP when zero jobs)"
    elif [[ "$GEO_RC" -eq 2 ]]; then
      warn "smoke_geo_country missing dependency (rc=2) — skipped"
    else
      warn "smoke_geo_country rc=${GEO_RC} (soft; not failing compass)"
    fi
  else
    set -e
    warn "skip smoke_geo_country (quality endpoint unavailable)"
  fi
else
  warn "smoke_geo_country.sh missing — skip geo DSS check"
fi

# --- 10. scheduler force (document only; endpoint exists) ---
echo "smoke_compass NOTE: force crawler tick (bypass UTC-day idempotency):"
echo "  curl -sf -X POST -H \"X-API-Key: \$API_KEY\" \\"
echo "    \"\${API_URL:-$API}/api/v1/scheduler/run?force=true\""

echo "smoke_compass OK against ${API} (SPEC-research-intents §11 automatable)"
exit 0
