#!/usr/bin/env python3
"""Retired: docs/sources/analysis/candidates were removed in the lean docs rewrite.

Source of truth: data/sources/catalog.json.
"""
from __future__ import annotations

import sys


def main() -> int:
    print(
        "generate_candidates_index.py is retired. "
        "Use data/sources/catalog.json.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
