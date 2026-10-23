"""Configurable technology taxonomy with aliases."""

from __future__ import annotations

from app.classification.taxonomy_catalog import TAXONOMY_ENTRIES

TAXONOMY: list[dict] = TAXONOMY_ENTRIES


def build_alias_index(items: list[dict] | None = None) -> dict[str, str]:
    index: dict[str, str] = {}
    for item in items or TAXONOMY:
        canonical = item["canonical_name"]
        index[canonical.lower()] = canonical
        for alias in item.get("aliases", []):
            index[alias.lower()] = canonical
    return index
