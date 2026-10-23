#!/usr/bin/env sh
# Schema-only dump to prove dump credentials/path work (does not keep the file).
set -eu
DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
TMP="${TMPDIR:-/tmp}/fmi-backup-smoke-$$.sql"
cleanup() { rm -f "$TMP"; }
trap cleanup EXIT INT TERM
DUMP_PREFIX="$("$DIR/pg_dump_cmd.sh")"
# shellcheck disable=SC2086
eval "$DUMP_PREFIX --schema-only --no-owner --no-privileges" > "$TMP"
test -s "$TMP"
echo "backup_smoke OK ($(wc -c < "$TMP") bytes schema dump)"
