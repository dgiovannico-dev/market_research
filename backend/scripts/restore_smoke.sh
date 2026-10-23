#!/usr/bin/env sh
# Schema-only dump → temp database → verify alembic_version → drop temp DB.
# Does not modify the primary POSTGRES_DB.
set -eu
DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
TMP="${TMPDIR:-/tmp}/fmi-restore-smoke-$$.sql"
ERR="${TMPDIR:-/tmp}/fmi-restore-smoke-$$.err"
SMOKE_DB="fmi_restore_smoke_$$"
PSQL_ADMIN="$("$DIR/psql_cmd.sh" postgres)"

run_psql() {
  db="$1"
  shift
  cmd="$("$DIR/psql_cmd.sh" "$db")"
  # shellcheck disable=SC2086
  eval "$cmd" "$@"
}

cleanup() {
  rm -f "$TMP" "$ERR"
  printf "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%s' AND pid <> pg_backend_pid();\n" "$SMOKE_DB" \
    | run_psql postgres -v ON_ERROR_STOP=1 -q >/dev/null 2>&1 || true
  printf "DROP DATABASE IF EXISTS %s;\n" "$SMOKE_DB" \
    | run_psql postgres -v ON_ERROR_STOP=1 -q >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

DUMP_PREFIX="$("$DIR/pg_dump_cmd.sh")"
# shellcheck disable=SC2086
eval "$DUMP_PREFIX --schema-only --no-owner --no-privileges" > "$TMP"
test -s "$TMP"

printf "CREATE DATABASE %s;\n" "$SMOKE_DB" | run_psql postgres -v ON_ERROR_STOP=1 -q >/dev/null

# Dump may contain SELECT set_config(...); discard result rows.
if ! run_psql "$SMOKE_DB" -v ON_ERROR_STOP=1 -q < "$TMP" >/dev/null 2>"$ERR"; then
  echo "restore_smoke FAIL: restore into $SMOKE_DB" >&2
  sed -n '1,40p' "$ERR" >&2 || true
  exit 1
fi

# Schema-only dump creates empty tables; prove critical relations exist.
out="$(printf "SELECT CASE WHEN to_regclass('public.alembic_version') IS NOT NULL AND to_regclass('public.sources') IS NOT NULL THEN 'ok' ELSE 'missing' END;\n" \
  | run_psql "$SMOKE_DB" -v ON_ERROR_STOP=1 -tA 2>"$ERR" | tr -d '[:space:]')"
if [ "$out" != "ok" ]; then
  echo "restore_smoke FAIL: expected alembic_version + sources (got: ${out:-empty})" >&2
  sed -n '1,20p' "$ERR" >&2 || true
  exit 1
fi

echo "restore_smoke OK (temp db $SMOKE_DB, schema tables present)"
