#!/usr/bin/env sh
set -eu
OUT="${1:-../data/exports/fmi-backup-$(date -u +%Y%m%dT%H%M%SZ).sql}"
mkdir -p "$(dirname "$OUT")"
PGPASSWORD="${POSTGRES_PASSWORD:-fmi_dev_password_change_me}" \
  pg_dump -h "${POSTGRES_HOST:-localhost}" -U "${POSTGRES_USER:-fmi}" -d "${POSTGRES_DB:-fmi}" > "$OUT"
echo "Backup written to $OUT"
