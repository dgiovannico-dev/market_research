#!/usr/bin/env sh
# Resolve a psql that can talk to Compose Postgres 16 when host client is older.
# Prints a command that reads SQL from stdin. Optional arg: database name (default POSTGRES_DB).
# Usage: eval "$(./psql_cmd.sh [db])" < file.sql
set -eu
ROOT="$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)"
USER="${POSTGRES_USER:-fmi}"
DB="${1:-${POSTGRES_DB:-fmi}}"
HOST="${POSTGRES_HOST:-localhost}"
PASS="${POSTGRES_PASSWORD:-fmi_dev_password_change_me}"

if [ -n "${PSQL:-}" ]; then
  printf '%s\n' "env PGPASSWORD='$PASS' '$PSQL' -h '$HOST' -U '$USER' -d '$DB'"
  exit 0
fi

if command -v docker >/dev/null 2>&1; then
  if docker compose -f "$ROOT/docker-compose.yml" ps --status running --services 2>/dev/null | grep -qx db; then
    printf '%s\n' "docker compose -f '$ROOT/docker-compose.yml' exec -T db psql -U '$USER' -d '$DB'"
    exit 0
  fi
fi

printf '%s\n' "env PGPASSWORD='$PASS' psql -h '$HOST' -U '$USER' -d '$DB'"
