"""ExternalStatsGateway over Eurostat + ADEM helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.stats.adem import LATEST_CSV_URL, summarize_csv
from app.stats.eurostat import ALLOWED_DATASETS, fetch_eurostat_series


class HttpExternalStats:
    async def eurostat_series(
        self,
        dataset: str,
        *,
        geo: str = "DE",
        time: str | None = "2022",
        limit: int = 20,
    ) -> dict[str, Any]:
        return await fetch_eurostat_series(dataset, geo=geo, time=time, limit=limit)

    def eurostat_datasets(self) -> dict[str, Any]:
        return {
            "evidence_kind": "config_observed",
            "provider": "eurostat",
            "datasets": sorted(ALLOWED_DATASETS),
            "disclaimer": "Allowlisted datasets only for safe reference lookups.",
        }

    def adem_skills_summary(
        self,
        *,
        nace_prefix: str | None = None,
        top_skills: int = 25,
    ) -> dict[str, Any]:
        """Load ADEM CSV from settings; raise FileNotFoundError / ValueError on bad input."""
        settings = get_settings()
        raw = (settings.adem_csv_path or "").strip()
        if not raw:
            return {
                "evidence_kind": "official_statistics_reference",
                "provider": "adem",
                "country": "LU",
                "status": "not_configured",
                "download_url": LATEST_CSV_URL,
                "hint": (
                    "Set ADEM_CSV_PATH to a local skills-vacancies CSV "
                    "(see data/sources/catalog.json (ADEM stats, not jobs)), then retry."
                ),
                "disclaimer": (
                    "Not live job ads — do not mix into Countries KPI counts."
                ),
            }
        path = Path(raw)
        if not path.is_file():
            raise FileNotFoundError(f"ADEM_CSV_PATH not found: {path}")
        return summarize_csv(
            path,
            nace_prefix=(nace_prefix.strip() if nace_prefix else None),
            top_skills=top_skills,
        )


DEFAULT_EXTERNAL_STATS = HttpExternalStats()
