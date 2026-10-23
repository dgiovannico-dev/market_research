#!/usr/bin/env sh
set -eu
OUT="${1:-../data/exports/fmi-backup-$(date -u +%Y%m%dT%H%M%SZ).sql}"
mkdir -p "$(dirname "$OUT")"
DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
DUMP_PREFIX="$("$DIR/pg_dump_cmd.sh")"
# shellcheck disable=SC2086
eval "$DUMP_PREFIX" > "$OUT"
echo "Backup written to $OUT"
