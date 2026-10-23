from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends, Query

from app.api.deps import verify_api_key
from app.taxonomy.esco import search_esco
from app.taxonomy.jobtech import search_jobtech

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])


@router.get("/taxonomy/esco/search")
async def esco_search(
    q: str = Query(..., min_length=1, max_length=200),
    type: Literal["occupation", "skill", "concept"] = "occupation",
    language: str = Query("en", min_length=2, max_length=8),
    limit: int = Query(10, ge=1, le=25),
) -> dict[str, Any]:
    """Free ESCO public search — taxonomy reference, not market KPIs."""
    return await search_esco(q, type_=type, language=language, limit=limit)


@router.get("/taxonomy/jobtech/search")
async def jobtech_search(
    q: str = Query(..., min_length=1, max_length=200),
    type: Literal["occupation", "skill"] = "skill",
    limit: int = Query(10, ge=1, le=25),
) -> dict[str, Any]:
    """Free JobTech Taxonomy autocomplete (Sweden) — reference labels only."""
    return await search_jobtech(q, type_=type, limit=limit)
