#!/usr/bin/env python3
"""Aggregate ADEM LU skills-vacancy open-data CSV into a metrics-friendly JSON summary.

Not a job collector — see data/sources/catalog.json (ADEM stats, not jobs).

Usage:
  python3 backend/scripts/adem_skills_summary.py --csv path/to/file.csv -o summary.json
  python3 backend/scripts/adem_skills_summary.py --download-latest -o summary.json
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

from app.stats.adem import LATEST_CSV_URL, summarize_csv


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} → {dest}", file=sys.stderr)
    urllib.request.urlretrieve(url, dest)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--csv", type=Path, help="Local ADEM skills-vacancies CSV")
    src.add_argument(
        "--download-latest",
        action="store_true",
        help="Fetch the portal's 2025-2026 bundle (~121MB)",
    )
    parser.add_argument("-o", "--output", type=Path, required=True, help="Write JSON summary here")
    parser.add_argument(
        "--nace-prefix",
        default=None,
        help="Optional NACE section filter (e.g. J for information/communication)",
    )
    parser.add_argument("--top-skills", type=int, default=50)
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path("/tmp/adem_lu_opendata"),
        help="Download target when using --download-latest",
    )
    args = parser.parse_args()

    if args.download_latest:
        csv_path = args.cache_dir / "datasc-skills-vacancies-2025-2026.csv"
        if not csv_path.is_file():
            download(LATEST_CSV_URL, csv_path)
    else:
        csv_path = args.csv
        if not csv_path.is_file():
            print(f"CSV not found: {csv_path}", file=sys.stderr)
            return 1

    summary = summarize_csv(
        csv_path,
        nace_prefix=(args.nace_prefix.strip() if args.nace_prefix else None),
        top_skills=args.top_skills,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
