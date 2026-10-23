"""Find a Job UK (DWP) search API — requires FINDAJOB_DWP_API_ID + FINDAJOB_DWP_API_KEY.

Catalogue: https://www.api.gov.uk/dwp/find-a-job/ (cross-gov credentials).
Endpoint: GET https://findajob.dwp.gov.uk/api/search
Auth: query params api_id, api_key.
"""

from __future__ import annotations

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
from app.core.config import get_settings
from app.secrets.resolve import credential_bundle

MAX_RECORDS = 50


def _parse_published(value: Any) -> datetime:
    if value:
        text = str(value).strip()
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _as_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("results", "jobs", "items", "vacancies", "data", "SearchResults"):
        node = payload.get(key)
        if isinstance(node, list):
            return [x for x in node if isinstance(x, dict)]
        if isinstance(node, dict):
            nested = node.get("results") or node.get("items") or node.get("jobs")
            if isinstance(nested, list):
                return [x for x in nested if isinstance(x, dict)]
    return []


def _parse_item(item: dict[str, Any]) -> RawJob | None:
    job_id = (
        item.get("id")
        or item.get("job_id")
        or item.get("vacancy_id")
        or item.get("reference")
        or item.get("ref")
    )
    if job_id is None:
        return None
    title = item.get("title") or item.get("job_title") or item.get("vacancy_title") or "Untitled"
    url = (
        item.get("url")
        or item.get("link")
        or item.get("job_url")
        or item.get("vacancy_url")
        or ""
    )
    if not url and job_id:
        url = f"https://findajob.dwp.gov.uk/details/{job_id}"
    company = (
        item.get("employer")
        or item.get("company")
        or item.get("organisation")
        or item.get("organization")
    )
    if isinstance(company, dict):
        company = company.get("name") or company.get("display_name")
    location = item.get("location") or item.get("town") or item.get("postcode")
    if isinstance(location, dict):
        location = location.get("name") or location.get("display")
    desc = item.get("description") or item.get("html_description") or item.get("summary")
    salary = item.get("salary") or item.get("salary_text") or item.get("wage")
    return RawJob(
        source_job_id=str(job_id),
        url=str(url),
        title=str(title),
        company=str(company) if company else None,
        description=str(desc) if desc else None,
        location=str(location) if location else None,
        published_at=_parse_published(
            item.get("posted") or item.get("date_posted") or item.get("published_at")
        ),
        salary_text=str(salary) if salary is not None else None,
        tags=[],
        job_type=item.get("job_type") or item.get("contract_type"),
        remote_hint=None,
        raw=item,
    )


class FindAJobDwpCollector(BaseCollector):
    name = "Find a Job UK DWP"
    source_key = "findajob_dwp"
    collection_mode = "search"
    base_url = "https://findajob.dwp.gov.uk/api/search"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        settings = get_settings()
        creds = credential_bundle("findajob_dwp")
        api_id = (creds.get("api_id") or "").strip()
        api_key = (creds.get("api_key") or "").strip()
        if not api_id or not api_key:
            return CollectorResult(
                records=[],
                pages_scanned=0,
                errors=["FINDAJOB_DWP_API_ID and FINDAJOB_DWP_API_KEY are required"],
            )

        search = simplify_query_for(self, query or "")
        location = settings.findajob_dwp_location.strip()
        params: dict[str, Any] = {
            "api_id": api_id,
            "api_key": api_key,
            "q": search,
            "html_description": "1",
        }
        if location:
            params["w"] = location

        headers = {"Accept": "application/json", "User-Agent": "FMI-MarketIntel/1.0"}
        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            try:
                resp = await client.get(self.base_url, params=params)
                if resp.status_code in (401, 403):
                    return CollectorResult(
                        records=[],
                        pages_scanned=1,
                        errors=[f"Find a Job DWP auth failed HTTP {resp.status_code}"],
                    )
                resp.raise_for_status()
                # Some deployments return XML; prefer JSON
                ctype = (resp.headers.get("content-type") or "").lower()
                if "json" in ctype or resp.text.lstrip().startswith(("{", "[")):
                    payload = resp.json()
                else:
                    return CollectorResult(
                        records=[],
                        pages_scanned=1,
                        errors=[f"unexpected content-type: {ctype or 'unknown'}"],
                    )
            except Exception as exc:  # noqa: BLE001
                return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        records: list[RawJob] = []
        seen: set[str] = set()
        for item in _as_list(payload):
            if len(records) >= MAX_RECORDS:
                break
            job = _parse_item(item)
            if job is None or job.source_job_id in seen:
                continue
            seen.add(job.source_job_id)
            records.append(job)

        return CollectorResult(records=records, pages_scanned=1, errors=[])
