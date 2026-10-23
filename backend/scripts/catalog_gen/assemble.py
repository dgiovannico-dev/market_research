"""Assemble registered sources into catalog.json payload and write it."""

from __future__ import annotations

import json
from pathlib import Path

from . import extended_sources, market_sources, reference_sources
from .registry import SOURCES, reset

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "sources" / "catalog.json"


def register_all() -> None:
    """Populate SOURCES in the original registration order."""
    reset()
    market_sources.register()
    reference_sources.register()
    extended_sources.register()
    assert len({s["catalog_id"] for s in SOURCES}) == len(SOURCES)


def build_payload() -> dict:
    register_all()
    return {
        "version": "2026-10-20",
        "methodology": (
            "Statuses assigned from non-destructive HTTP probes and public docs review. "
            "ACTIVE requires a working connector returning real records in this repo. "
            "Prefer free public APIs/RSS/feeds over paid aggregator APIs when both exist. "
            "No scraping of ToS-protected / paywalled / login sites. No invented credentials success."
        ),
        "priority_roles": [
            "Senior Java / Spring Boot",
            "Backend / Full-Stack",
            "Cloud / Platform / DevOps",
            "Architect / Tech Lead",
            "AI / GenAI / LLM / RAG / Agents",
            "Data / ML Engineer",
            "Freelance IT Consultant",
        ],
        "geography": "Worldwide (source-biased; not total market)",
        "sources": list(SOURCES),
    }


def write_catalog(out: Path | None = None) -> Path:
    path = out or OUT
    payload = build_payload()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def status_counts() -> dict[str, int]:
    by: dict[str, int] = {}
    for s in SOURCES:
        by[s["verification_status"]] = by.get(s["verification_status"], 0) + 1
    return by
