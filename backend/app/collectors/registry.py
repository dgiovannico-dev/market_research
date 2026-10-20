from __future__ import annotations

from app.collectors.arbeitnow import ArbeitnowCollector
from app.collectors.base import BaseCollector
from app.collectors.remotive import RemotiveCollector

COLLECTORS: dict[str, BaseCollector] = {
    "remotive": RemotiveCollector(),
    "arbeitnow": ArbeitnowCollector(),
}

# Declared but not implemented without authorized access
UNSUPPORTED_SOURCES = [
    {
        "name": "LinkedIn Jobs",
        "source_key": "linkedin",
        "connector_status": "requires_credentials",
        "coverage_notes": "Only authorized LinkedIn APIs/partners. No scraping.",
    },
    {
        "name": "Malt",
        "source_key": "malt",
        "connector_status": "requires_credentials",
        "coverage_notes": "Requires official integration or permitted export.",
    },
    {
        "name": "Indeed",
        "source_key": "indeed",
        "connector_status": "requires_credentials",
        "coverage_notes": "Authorized publisher APIs only.",
    },
    {
        "name": "Upwork",
        "source_key": "upwork",
        "connector_status": "requires_credentials",
        "coverage_notes": "Official API / permitted export only.",
    },
    {
        "name": "Freelancermap",
        "source_key": "freelancermap",
        "connector_status": "unsupported",
        "coverage_notes": "No verified public API in MVP scope.",
    },
    {
        "name": "Free-Work",
        "source_key": "freework",
        "connector_status": "unsupported",
        "coverage_notes": "No verified public API in MVP scope.",
    },
    {
        "name": "Manual CSV/JSON/XLSX Import",
        "source_key": "manual_import",
        "connector_status": "manual_import",
        "coverage_notes": "Primary bootstrap path for arbitrary lawful exports.",
    },
]


def get_collector(source_key: str) -> BaseCollector | None:
    return COLLECTORS.get(source_key)
