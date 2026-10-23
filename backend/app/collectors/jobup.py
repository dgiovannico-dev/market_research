"""JobUp.ch — free public Swiss jobs search API (no key).

Public search: GET /api/v1/public/search?query=&rows=&start=
``rows`` max is 20 (higher values return HTTP 422).
Response includes start, rows, current_page, num_pages, total_hits, documents.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.collectors.base import (
    BaseCollector,
    CollectorResult,
    RawJob,
    is_blank_query,
    missing_query_result,
    simplify_query_for,
)

BASE_URL = "https://www.jobup.ch/api/v1/public/search"
# Public search rejects rows > 20 with HTTP 422 ("20 is the upper limit for results").
ROWS_PER_PAGE = 20
MAX_RECORDS = 150
MAX_PAGES = 3
MAX_VARIANTS = 3

_IT_VARIANTS = ("software", "devops", "python")
_TECH_TERMS = frozenset(
    "it tech technology software developer engineer devops python java javascript "
    "typescript react cloud data backend frontend fullstack full-stack informatique "
    "informatik informatiker sre kubernetes aws azure golang kotlin nodejs sql ml ai".split()
)
_GENERIC_TERMS = frozenset(
    "it job jobs tech technology developer engineer informatique informatik "
    "arbeit stelle stellen".split()
)
_TOKEN_RE = re.compile(r"[a-z0-9+#.-]+", re.I)


class JobUpCollector(BaseCollector):
    name = "JobUp"
    source_key = "jobup"
    collection_mode = "search"
    base_url = BASE_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        q = simplify_query_for(self, query or "")
        variants = _query_variants(q)
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        records: list[RawJob] = []
        seen: set[str] = set()
        errors: list[str] = []
        pages = 0

        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            for variant in variants:
                start = 0
                while len(records) < MAX_RECORDS and pages < MAX_PAGES:
                    rows = min(ROWS_PER_PAGE, MAX_RECORDS - len(records))
                    params = {"query": variant, "rows": rows, "start": start}
                    try:
                        resp = await client.get(BASE_URL, params=params)
                        resp.raise_for_status()
                        payload = resp.json() or {}
                    except Exception as exc:  # noqa: BLE001
                        errors.append(f"{variant}: {exc}")
                        break

                    pages += 1
                    docs = payload.get("documents") if isinstance(payload, dict) else None
                    if not isinstance(docs, list):
                        errors.append(f"{variant}: unexpected payload")
                        break

                    added = 0
                    for item in docs:
                        job = _to_raw(item)
                        if job is None or job.source_job_id in seen:
                            continue
                        seen.add(job.source_job_id)
                        records.append(job)
                        added += 1
                        if len(records) >= MAX_RECORDS:
                            break

                    if added == 0 or len(docs) < rows:
                        break
                    start += rows

        return CollectorResult(records=records, pages_scanned=max(pages, 1), errors=errors)


def _query_variants(q: str) -> list[str]:
    """Original query plus up to 2 IT terms when generic or tech-related."""
    base = (q or "").strip()
    if not base:
        return []
    if not _should_fan_out(base):
        return [base]
    variants = [base]
    lower = base.lower()
    for term in _IT_VARIANTS:
        if term in lower:
            continue
        variants.append(term)
        if len(variants) >= MAX_VARIANTS:
            break
    return variants


def _should_fan_out(q: str) -> bool:
    tokens = {t.lower() for t in _TOKEN_RE.findall(q)}
    if not tokens:
        return False
    if tokens & _TECH_TERMS or len(tokens) <= 1:
        return True
    return bool(tokens & _GENERIC_TERMS)


def _to_raw(item: Any) -> RawJob | None:
    if not isinstance(item, dict) or not item.get("is_active", True):
        return None
    job_id = item.get("job_id") or item.get("datapool_id")
    if not job_id:
        return None
    return RawJob(
        source_job_id=str(job_id),
        url=_detail_url(item, job_id),
        title=item.get("title") or "Untitled",
        company=item.get("company_name"),
        description=item.get("preview"),
        location=item.get("place") or "Switzerland",
        published_at=_published(item),
        salary_text=_salary_text(item),
        tags=_tags(item),
        job_type=None,
        remote_hint=None,
        raw={
            "job_id": item.get("job_id"),
            "title": item.get("title"),
            "company_name": item.get("company_name"),
            "place": item.get("place"),
            "salary": item.get("salary"),
            "publication_date": item.get("publication_date"),
            "country_code": "CH",
        },
    )


def _detail_url(item: dict[str, Any], job_id: str) -> str:
    links = item.get("_links") or {}
    if isinstance(links, dict):
        for key in ("detail_en", "detail_fr", "detail_de"):
            node = links.get(key) or {}
            if isinstance(node, dict) and node.get("href"):
                return str(node["href"])
    return f"https://www.jobup.ch/en/jobs/detail/{job_id}/"


def _published(item: dict[str, Any]) -> datetime:
    raw = item.get("publication_date") or item.get("initial_publication_date")
    if raw:
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _salary_text(item: dict[str, Any]) -> str | None:
    salary = item.get("salary")
    if isinstance(salary, dict):
        cur = salary.get("currency") or "CHF"
        unit = salary.get("unit") or ""
        rng = salary.get("range") if isinstance(salary.get("range"), dict) else {}
        lo = rng.get("gte") if rng else item.get("salary_from")
        hi = rng.get("lte") if rng else None
        if lo is None and hi is None:
            return None
        if hi is None:
            return f"{lo}+ {cur}/{unit}".strip("/")
        return f"{lo}-{hi} {cur}/{unit}".strip("/")
    if item.get("salary_from") is not None:
        return f"{item['salary_from']}+ CHF"
    return None


def _tags(item: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    for t in item.get("listing_tags") or []:
        if isinstance(t, str):
            tags.append(t)
        elif isinstance(t, dict) and t.get("value"):
            tags.append(str(t["value"]))
    return tags[:15]
