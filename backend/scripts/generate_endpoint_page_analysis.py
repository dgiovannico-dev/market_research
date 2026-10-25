#!/usr/bin/env python3
"""Retired: docs/sources analysis workbooks were removed in the lean docs rewrite.

Source of truth for catalog candidates is data/sources/catalog.json.
Connector ops: docs/ops/RUNBOOKS.md § connectors.
"""
from __future__ import annotations

import sys


def main() -> int:
    print(
        "generate_endpoint_page_analysis.py is retired. "
        "Use data/sources/catalog.json and docs/ops/RUNBOOKS.md.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
