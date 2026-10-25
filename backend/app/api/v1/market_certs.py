"""Certification market routes (kept out of market_extra for file-size / SRP)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.analytics.cert_country import certifications_by_country
from app.api.deps import verify_api_key
from app.api.v1.query_params import min_evidence_query, parse_lens_params
from app.storage.db import get_db

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])


@router.get(
    "/market/certifications/by-country",
    summary="Certifications by country (map + per-country top-N)",
    description=(
        "Observed certification mentions grouped by job country_code. "
        "map_items drive choropleth (jobs with ≥1 cert); countries[].top is the local ranking."
    ),
)
def market_certifications_by_country(
    days: int = Query(90, ge=7, le=730),
    country_code: Optional[str] = Query(
        None,
        description="ISO country code or CSV (e.g. IT,CH)",
    ),
    lens: Optional[str] = Query(None, description="Omit for all jobs; market|focus|compare."),
    query_ids: Optional[list[str]] = Query(None),
    min_evidence: Optional[str] = Query(
        None,
        description="Corpus gate: standard (default), all, or thin.",
    ),
    top_n_per_country: int = Query(5, ge=1, le=20),
    top_countries: int = Query(40, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    return certifications_by_country(
        db,
        days=days,
        country_code=country_code,
        lens=lens_name,
        query_ids=qids,
        min_evidence=min_evidence_query(min_evidence),
        top_n_per_country=top_n_per_country,
        top_countries=top_countries,
    )
