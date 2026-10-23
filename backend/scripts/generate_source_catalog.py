#!/usr/bin/env python3
"""Generate data/sources/catalog.json from the FMI global sources prompt (deduped)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow `python3 backend/scripts/generate_source_catalog.py` without install.
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from catalog_gen.assemble import status_counts, write_catalog  # noqa: E402
from catalog_gen.registry import SOURCES  # noqa: E402


def main() -> None:
    path = write_catalog()
    print(f"Wrote {len(SOURCES)} sources to {path}")
    print("status counts:", json.dumps(status_counts(), indent=2))


if __name__ == "__main__":
    main()
