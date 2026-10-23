#!/usr/bin/env python3
"""Backfill job_intent_matches for the local corpus (no crawl).

Usage (from repo root, API container or backend venv):

  python backend/scripts/backfill_intent_matches.py
  python backend/scripts/backfill_intent_matches.py --kind all --dry-run

Or via API:

  curl -X POST -H "X-API-Key: $API_KEY" \\
    "$API_URL/api/v1/research/matches/backfill?kind=focus"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow `python scripts/...` from backend/ or repo root.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.research.match_backfill import backfill_intent_matches  # noqa: E402
from app.storage.db import SessionLocal  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--kind",
        choices=("focus", "discovery", "all"),
        default="all",
        help="Default all: discovery+focus so dump jobs stay in market lens",
    )
    parser.add_argument("--include-disabled", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit-jobs", type=int, default=None)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        result = backfill_intent_matches(
            db,
            kind=args.kind,
            enabled_only=not args.include_disabled,
            limit_jobs=args.limit_jobs,
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
