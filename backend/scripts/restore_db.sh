#!/usr/bin/env sh
set -eu
IN="${1:?Usage: restore_db.sh <backup.sql>}"
PGPASSWORD="${POSTGRES_PASSWORD:-fmi_dev_password_change_me}" \
  psql -h "${POSTGRES_HOST:-localhost}" -U "${POSTGRES_USER:-fmi}" -d "${POSTGRES_DB:-fmi}" < "$IN"
echo "Restore complete from $IN"
