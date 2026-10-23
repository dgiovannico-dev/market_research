#!/usr/bin/env python3
"""Backfill Job.country_code for unknown rows (no crawl).

Usage (API container or backend venv):

  python backend/scripts/backfill_country_codes.py --dry-run
  python backend/scripts/backfill_country_codes.py
  python backend/scripts/backfill_country_codes.py --limit 500
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.ingestion.country_backfill import backfill_country_codes  # noqa: E402
from app.storage.db import SessionLocal  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--all",
        action="store_true",
        help="Also re-resolve rows that already have a non-unknown code",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        result = backfill_country_codes(
            db,
            only_unknown=not args.all,
            limit=args.limit,
            dry_run=args.dry_run,
        )
        if not args.dry_run:
            db.commit()
    finally:
        db.close()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
