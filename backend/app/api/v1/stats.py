from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import verify_api_key
from app.bootstrap import get_container

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])

# Keep in sync with ALLOWED_DATASETS (asserted in tests).
EurostatDataset = Literal[
    "earn_ses_hourly",
    "earn_ses18_hourly",
    "une_rt_a",
    "isoc_sk_oja",
    "isoc_sk_oja2",
]


@router.get("/stats/eurostat/series")
async def eurostat_series(
    dataset: EurostatDataset = "earn_ses_hourly",
    geo: str = Query("DE", min_length=2, max_length=8),
    time: str | None = Query("2022", max_length=16),
    limit: int = Query(20, ge=1, le=50),
) -> dict[str, Any]:
    """Free Eurostat JSON-stat slice — official statistics reference, not job KPIs."""
    stats = get_container().external_stats
    return await stats.eurostat_series(dataset, geo=geo, time=time, limit=limit)


@router.get("/stats/eurostat/datasets")
def eurostat_datasets() -> dict[str, Any]:
    return get_container().external_stats.eurostat_datasets()


@router.get("/stats/adem/skills-summary")
def adem_skills_summary(
    nace_prefix: str | None = Query(
        None,
        max_length=8,
        description="Optional NACE section filter (e.g. J = information/communication)",
    ),
    top_skills: int = Query(25, ge=1, le=100),
) -> dict[str, Any]:
    """ADEM LU skills-in-vacancies summary (CC0). Requires ADEM_CSV_PATH — not live ads."""
    stats = get_container().external_stats
    try:
        return stats.adem_skills_summary(
            nace_prefix=nace_prefix,
            top_skills=top_skills,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
