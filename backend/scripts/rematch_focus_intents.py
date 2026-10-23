#!/usr/bin/env python3
"""Backfill job_intent_matches for enabled focus intents (text rematch, no crawl).

Usage (host or api container):
  cd backend && python scripts/rematch_focus_intents.py
  python scripts/rematch_focus_intents.py --dry-run
  python scripts/rematch_focus_intents.py --query-id 1 --query-id 4
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.research.rematch import rematch_focus_intents
from app.storage.db import SessionLocal


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count candidates without writing matches",
    )
    parser.add_argument(
        "--query-id",
        action="append",
        type=int,
        dest="query_ids",
        help="Limit to one or more focus intent ids (repeatable)",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        # rematch_focus_intents commits when it writes; dry-run leaves the session clean.
        stats = rematch_focus_intents(
            db,
            query_ids=args.query_ids,
            dry_run=args.dry_run,
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(json.dumps(stats, indent=2, default=str))
    if stats["intents"] == 0:
        print("No enabled focus intents found.", file=sys.stderr)
        return 1
    if stats["candidates"] == 0:
        print("No text matches; focus lens will stay empty.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
