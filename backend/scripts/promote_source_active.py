#!/usr/bin/env python3
"""Promote a Source to ACTIVE only after a successful live CollectionRun with inserts.

Does not rewrite catalog.json — update generate_source_catalog.py + regenerate after evidence.
Usage:
  cd backend && source .venv/bin/activate
  python scripts/promote_source_active.py --connector-key bundesagentur
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow `python scripts/promote_source_active.py` from backend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.collectors.registry import CREDENTIALED_SCAFFOLDS, COLLECTORS
from app.storage.db import SessionLocal
from app.storage.models import CollectionRun, Source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--connector-key", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    key = args.connector_key.strip()
    if key not in COLLECTORS:
        print(f"Unknown connector_key: {key}", file=sys.stderr)
        return 2

    db = SessionLocal()
    try:
        source = db.scalar(select(Source).where(Source.connector_type == key))
        if not source:
            print(f"No Source row for connector_type={key}. Seed/restart API first.", file=sys.stderr)
            return 1
        run = db.scalars(
            select(CollectionRun)
            .where(
                CollectionRun.source_id == source.id,
                CollectionRun.status == "succeeded",
                CollectionRun.records_inserted > 0,
            )
            .order_by(CollectionRun.completed_at.desc())
            .limit(1)
        ).first()
        if not run:
            print(
                "No succeeded CollectionRun with records_inserted > 0. "
                "Run the connector live before promoting.",
                file=sys.stderr,
            )
            return 1
        print(
            f"Evidence run id={run.id} inserted={run.records_inserted} "
            f"completed_at={run.completed_at}"
        )
        if args.dry_run:
            print(f"DRY RUN: would set Source id={source.id} verification_status=ACTIVE")
            return 0
        source.verification_status = "ACTIVE"
        source.connector_status = "enabled"
        source.enabled = True
        source.last_validated_at = datetime.now(timezone.utc)
        db.commit()
        print(f"Updated Source id={source.id} name={source.name!r} → ACTIVE")
        if key in CREDENTIALED_SCAFFOLDS:
            print(
                "Reminder: set status=ACTIVE in backend/scripts/generate_source_catalog.py "
                "and regenerate data/sources/catalog.json for catalog parity."
            )
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
