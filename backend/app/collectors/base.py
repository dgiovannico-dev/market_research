from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, Optional

CollectionMode = Literal["search", "dump", "feed"]

MISSING_QUERY = "missing_query"

_OR_SPLIT = re.compile(r"\s+OR\s+", re.IGNORECASE)


@dataclass
class RawJob:
    source_job_id: str
    url: str
    title: str
    company: str | None = None
    description: str | None = None
    location: str | None = None
    published_at: datetime | None = None
    salary_text: str | None = None
    tags: list[str] = field(default_factory=list)
    job_type: str | None = None
    remote_hint: bool | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class CollectorResult:
    records: list[RawJob]
    pages_scanned: int = 1
    errors: list[str] = field(default_factory=list)
    # When True, soft-expire may mark jobs missing from this dump as closed_stale.
    # Capped / sampled dumps must leave this False (age-only expire).
    dump_complete: bool = False
    # Optional run metadata (e.g. CKAN resource) merged into CollectionRun.summary.
    meta: dict[str, Any] = field(default_factory=dict)


def is_blank_query(query: Optional[str]) -> bool:
    return query is None or not str(query).strip()


def missing_query_result() -> CollectorResult:
    """Search-mode collectors must return this when query is None/blank."""
    return CollectorResult(records=[], pages_scanned=0, errors=[MISSING_QUERY])


def simplify_query_for(_collector: BaseCollector | str | None, text: str) -> str:
    """Best-effort query text for APIs without boolean OR.

    When ``text`` contains ``OR`` clauses, collectors may use the first clause
    (or pass the full string through). Callers that support native boolean
    syntax may skip this helper.
    """
    q = (text or "").strip()
    if not q:
        return q
    if _OR_SPLIT.search(q):
        return _OR_SPLIT.split(q, maxsplit=1)[0].strip()
    return q


class BaseCollector(ABC):
    name: str
    source_key: str
    collection_mode: CollectionMode  # required on every concrete collector

    @abstractmethod
    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        raise NotImplementedError
