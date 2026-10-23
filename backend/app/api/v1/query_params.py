"""Shared FastAPI query-parameter parsing for market analytics routes."""

from __future__ import annotations

from typing import Optional

from fastapi import HTTPException

from app.analytics.evidence_gate import parse_min_evidence
from app.analytics.lenses import parse_lens, parse_query_ids


def parse_lens_params(
    lens: Optional[str],
    query_ids: Optional[list[str]],
) -> tuple[Optional[str], Optional[list[int]]]:
    try:
        return parse_lens(lens), parse_query_ids(query_ids)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def min_evidence_query(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    try:
        parse_min_evidence(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return value
