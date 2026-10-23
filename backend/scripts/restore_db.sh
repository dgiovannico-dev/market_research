#!/usr/bin/env sh
set -eu
IN="${1:?Usage: restore_db.sh <backup.sql>}"
DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
PSQL_CMD="$("$DIR/psql_cmd.sh")"
# shellcheck disable=SC2086
eval "$PSQL_CMD" -v ON_ERROR_STOP=1 < "$IN"
echo "Restore complete from $IN"
