#!/usr/bin/env sh
# Resolve a pg_dump that matches Postgres 16 (Compose `db` service) when host client is older.
# Usage: . ./pg_dump_cmd.sh   → sets DUMP_CMD as a shell function-like string via eval, or:
#   $(./pg_dump_cmd.sh) --schema-only ...
set -eu
ROOT="$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)"
USER="${POSTGRES_USER:-fmi}"
DB="${POSTGRES_DB:-fmi}"
HOST="${POSTGRES_HOST:-localhost}"
PASS="${POSTGRES_PASSWORD:-fmi_dev_password_change_me}"

if [ -n "${PG_DUMP:-}" ]; then
  printf '%s\n' "env PGPASSWORD='$PASS' '$PG_DUMP' -h '$HOST' -U '$USER' -d '$DB'"
  exit 0
fi

if command -v docker >/dev/null 2>&1; then
  if docker compose -f "$ROOT/docker-compose.yml" ps --status running --services 2>/dev/null | grep -qx db; then
    printf '%s\n' "docker compose -f '$ROOT/docker-compose.yml' exec -T db pg_dump -U '$USER' -d '$DB'"
    exit 0
  fi
fi

printf '%s\n' "env PGPASSWORD='$PASS' pg_dump -h '$HOST' -U '$USER' -d '$DB'"
