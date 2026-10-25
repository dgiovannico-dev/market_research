#!/usr/bin/env sh
# sessionStart: remind agent when full Compose stack relaunch check is due.
set -eu
ROOT="$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)"
INTERVAL_MIN="${COMPOSE_STACK_MIN_INTERVAL_MINUTES:-30}"
STAMP="$ROOT/.cursor/compose-stack-last-ok"

due=1
age_note="never ran"
if [ -f "$STAMP" ]; then
  now="$(date +%s)"
  last="$(cat "$STAMP" 2>/dev/null || echo 0)"
  age_min=$(( (now - last) / 60 ))
  age_note="${age_min}m ago"
  if [ "$age_min" -lt "$INTERVAL_MIN" ]; then
    due=0
  fi
fi

# Consume stdin (hook payload) so pipes do not hang.
cat >/dev/null || true

if [ "$due" -eq 1 ]; then
  msg="Compose stack check is due (last OK: ${age_note}; interval ${INTERVAL_MIN}m). Run: ./scripts/compose_stack_relaunch.sh"
  # sessionStart supports additional_context in Cursor hooks
  printf '%s\n' "{\"additional_context\":$(printf '%s' "$msg" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')}"
else
  printf '%s\n' '{}'
fi
