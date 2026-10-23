from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

CATALOG_PATH = Path(__file__).resolve().parents[3] / "data" / "sources" / "catalog.json"


@lru_cache
def load_catalog() -> dict[str, Any]:
    if not CATALOG_PATH.exists():
        return {"version": None, "sources": [], "error": f"missing {CATALOG_PATH}"}
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def catalog_summary() -> dict[str, Any]:
    data = load_catalog()
    sources = data.get("sources") or []
    by_status: dict[str, int] = {}
    by_category: dict[str, int] = {}
    active_connectors: list[str] = []
    for s in sources:
        st = s.get("verification_status") or "UNKNOWN"
        by_status[st] = by_status.get(st, 0) + 1
        cat = s.get("category") or "?"
        by_category[cat] = by_category.get(cat, 0) + 1
        if st == "ACTIVE" and s.get("connector_key"):
            active_connectors.append(s["connector_key"])
    return {
        "version": data.get("version"),
        "methodology": data.get("methodology"),
        "total": len(sources),
        "by_status": by_status,
        "by_category": by_category,
        "active_connector_keys": sorted(set(active_connectors)),
        "priority_roles": data.get("priority_roles"),
        "geography": data.get("geography"),
    }
