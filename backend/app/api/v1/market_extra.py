from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.analytics.cooccurrence import skill_cooccurrence
from app.analytics.countries import country_comparison
from app.analytics.rates import rate_explorer
from app.api.deps import verify_api_key
from app.storage.db import get_db

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])


@router.get("/market/rates")
def market_rates(
    days: int = Query(180, ge=7, le=730),
    country_code: Optional[str] = None,
    unit: Optional[str] = None,
    currency: Optional[str] = None,
    min_sample: int = Query(5, ge=1),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return rate_explorer(
        db,
        days=days,
        country_code=country_code,
        unit=unit,
        currency=currency,
        min_sample=min_sample,
    )


@router.get("/market/countries")
def market_countries(
    days: int = Query(90, ge=7, le=365),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return country_comparison(db, days=days)


@router.get("/market/skills/cooccurrence")
def market_cooccurrence(
    days: int = Query(90, ge=7, le=365),
    min_support: int = Query(3, ge=1),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return skill_cooccurrence(db, days=days, min_support=min_support)
