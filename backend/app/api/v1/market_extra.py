from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.analytics.cooccurrence import skill_cooccurrence
from app.analytics.countries import country_comparison
from app.analytics.facets import market_facets
from app.analytics.language_country import language_country_matrix
from app.analytics.languages import language_demand
from app.analytics.rate_series import rate_series
from app.analytics.rates import rate_explorer
from app.analytics.role_tech import role_tech_matrix
from app.analytics.seniority_tech import seniority_tech_matrix
from app.analytics.series import country_series, technology_series
from app.analytics.tech_country import tech_country_matrix
from app.api.deps import verify_api_key
from app.api.v1.query_params import min_evidence_query, parse_lens_params
from app.storage.db import get_db

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])


@router.get("/market/facets")
def market_facets_route(
    days: int = Query(30, ge=7, le=730),
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
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    return market_facets(
        db,
        days=days,
        country_code=country_code,
        lens=lens_name,
        query_ids=qids,
        min_evidence=min_evidence_query(min_evidence),
    )


@router.get("/market/languages")
def market_languages_route(
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
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    return language_demand(
        db,
        days=days,
        country_code=country_code,
        lens=lens_name,
        query_ids=qids,
        min_evidence=min_evidence_query(min_evidence),
        limit=limit,
    )


@router.get("/market/rates")
def market_rates(
    days: int = Query(180, ge=7, le=730),
    country_code: Optional[str] = Query(
        None,
        description="ISO country code or CSV (e.g. IT,CH)",
    ),
    unit: Optional[str] = None,
    currency: Optional[str] = None,
    min_sample: int = Query(5, ge=1),
    lens: Optional[str] = Query(None, description="Omit for all jobs; market|focus|compare."),
    query_ids: Optional[list[str]] = Query(None),
    min_evidence: Optional[str] = Query(
        None,
        description="Corpus gate: standard (default), all, or thin.",
    ),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    return rate_explorer(
        db,
        days=days,
        country_code=country_code,
        unit=unit,
        currency=currency,
        min_sample=min_sample,
        lens=lens_name,
        query_ids=qids,
        min_evidence=min_evidence_query(min_evidence),
    )


@router.get("/market/countries")
def market_countries(
    days: int = Query(90, ge=7, le=365),
    country_code: Optional[str] = Query(
        None,
        description="ISO country code or CSV — restrict comparison rows",
    ),
    lens: Optional[str] = Query(None, description="Omit for all jobs; market|focus|compare."),
    query_ids: Optional[list[str]] = Query(None),
    for_map: bool = Query(
        False,
        description="When true, return all ISO counts for choropleth (cap 250).",
    ),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    return country_comparison(
        db,
        days=days,
        country_code=country_code,
        lens=lens_name,
        query_ids=qids,
        for_map=for_map,
    )


@router.get("/market/skills/cooccurrence")
def market_cooccurrence(
    days: int = Query(90, ge=7, le=365),
    min_support: int = Query(3, ge=1),
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
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    return skill_cooccurrence(
        db,
        days=days,
        min_support=min_support,
        country_code=country_code,
        lens=lens_name,
        query_ids=qids,
        min_evidence=min_evidence_query(min_evidence),
    )


@router.get(
    "/market/matrix/tech-country",
    summary="Technology × country job counts",
)
def market_tech_country_matrix(
    days: int = Query(30, ge=7, le=730),
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
    top_tech: int = Query(12, ge=1, le=50),
    top_country: int = Query(10, ge=1, le=50),
    min_cell: int = Query(2, ge=1),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    return tech_country_matrix(
        db,
        days=days,
        country_code=country_code,
        lens=lens_name,
        query_ids=qids,
        min_evidence=min_evidence_query(min_evidence),
        top_tech=top_tech,
        top_country=top_country,
        min_cell=min_cell,
    )


@router.get(
    "/market/matrix/role-tech",
    summary="Role family × technology job counts",
    description=(
        "Matrix of Job.role_family × Technology.canonical_name via JobSkill. "
        "Observed inventory only; cells below min_cell omitted. "
        "Jobs without role_family excluded from axes."
    ),
)
def market_role_tech_matrix(
    days: int = Query(30, ge=7, le=730),
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
    top_role: int = Query(12, ge=1, le=50),
    top_tech: int = Query(12, ge=1, le=50),
    min_cell: int = Query(2, ge=1),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    return role_tech_matrix(
        db,
        days=days,
        country_code=country_code,
        lens=lens_name,
        query_ids=qids,
        min_evidence=min_evidence_query(min_evidence),
        top_role=top_role,
        top_tech=top_tech,
        min_cell=min_cell,
    )


@router.get(
    "/market/matrix/seniority-tech",
    summary="Seniority × technology job counts",
    description=(
        "Matrix of Job.seniority × Technology.canonical_name via JobSkill. "
        "Observed inventory only; cells below min_cell omitted. "
        "Jobs without seniority excluded from axes."
    ),
)
def market_seniority_tech_matrix(
    days: int = Query(30, ge=7, le=730),
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
    top_seniority: int = Query(8, ge=1, le=50),
    top_tech: int = Query(12, ge=1, le=50),
    min_cell: int = Query(2, ge=1),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    return seniority_tech_matrix(
        db,
        days=days,
        country_code=country_code,
        lens=lens_name,
        query_ids=qids,
        min_evidence=min_evidence_query(min_evidence),
        top_seniority=top_seniority,
        top_tech=top_tech,
        min_cell=min_cell,
    )


@router.get(
    "/market/matrix/language-country",
    summary="Human language × country job counts",
    description=(
        "Matrix of ISO 639-1 language_requirements × country_code. "
        "Observed extraction only; cells below min_cell omitted."
    ),
)
def market_language_country_matrix(
    days: int = Query(30, ge=7, le=730),
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
    top_language: int = Query(12, ge=1, le=50),
    top_country: int = Query(10, ge=1, le=50),
    min_cell: int = Query(2, ge=1),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    return language_country_matrix(
        db,
        days=days,
        country_code=country_code,
        lens=lens_name,
        query_ids=qids,
        min_evidence=min_evidence_query(min_evidence),
        top_language=top_language,
        top_country=top_country,
        min_cell=min_cell,
    )


@router.get("/market/series/technologies")
def market_technology_series(
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
    top: int = Query(8, ge=1, le=30),
    grain: Optional[str] = Query(
        None,
        description="day|week|month; auto from days when omitted.",
    ),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    try:
        return technology_series(
            db,
            days=days,
            country_code=country_code,
            lens=lens_name,
            query_ids=qids,
            min_evidence=min_evidence_query(min_evidence),
            top=top,
            grain=grain,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/market/series/countries")
def market_country_series(
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
    top: int = Query(8, ge=1, le=30),
    grain: Optional[str] = Query(
        None,
        description="day|week|month; auto from days when omitted.",
    ),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    try:
        return country_series(
            db,
            days=days,
            country_code=country_code,
            lens=lens_name,
            query_ids=qids,
            min_evidence=min_evidence_query(min_evidence),
            top=top,
            grain=grain,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get(
    "/market/series/rates",
    summary="Median advertised rate over time",
    description=(
        "Multi-series of median JobRate.amount_min (rate_type=advertised) "
        "grouped by currency/unit. Field `count` is the median value for chart reuse. "
        "Not a market wage estimate."
    ),
)
def market_rate_series(
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
    top: int = Query(5, ge=1, le=30),
    grain: Optional[str] = Query(
        None,
        description="day|week|month; auto from days when omitted.",
    ),
    unit: Optional[str] = Query(
        None,
        description="Optional rate unit filter (e.g. hour, day).",
    ),
    currency: Optional[str] = Query(
        None,
        description="Optional ISO currency filter (e.g. EUR, CHF).",
    ),
    min_sample: int = Query(
        3,
        ge=1,
        description="Minimum rate observations for a series key to appear.",
    ),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    try:
        return rate_series(
            db,
            days=days,
            country_code=country_code,
            lens=lens_name,
            query_ids=qids,
            min_evidence=min_evidence_query(min_evidence),
            top=top,
            grain=grain,
            unit=unit,
            currency=currency,
            min_sample=min_sample,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
