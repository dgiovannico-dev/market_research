#!/usr/bin/env python3
"""Backfill Job.language_requirements from title/description (batched).

Usage:
  python -m scripts.backfill_language_requirements --dry-run
  python -m scripts.backfill_language_requirements --limit 500
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.classification.language_rules import extract_language_requirements
from app.storage.db import SessionLocal
from app.storage.models import Job


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=2000)
    parser.add_argument("--batch", type=int, default=200)
    args = parser.parse_args()

    db = SessionLocal()
    updated = 0
    scanned = 0
    try:
        q = (
            db.query(Job)
            .filter(Job.is_canonical.is_(True))
            .order_by(Job.id.desc())
            .limit(max(1, args.limit))
        )
        batch: list[Job] = []
        for job in q:
            scanned += 1
            langs = extract_language_requirements(
                title=job.title_original or "",
                description=job.description_original,
            )
            prev = list(job.language_requirements or [])
            if langs == prev:
                continue
            if not args.dry_run:
                job.language_requirements = langs
            updated += 1
            batch.append(job)
            if not args.dry_run and len(batch) >= args.batch:
                db.commit()
                batch.clear()
        if not args.dry_run and batch:
            db.commit()
        print(
            f"{'DRY-RUN ' if args.dry_run else ''}scanned={scanned} would_update={updated}"
            if args.dry_run
            else f"scanned={scanned} updated={updated}"
        )
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
