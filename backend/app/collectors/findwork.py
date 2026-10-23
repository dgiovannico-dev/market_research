"""Findwork.dev Jobs API — requires FINDWORK_API_KEY.

Official docs: https://findwork.dev/developers/
Endpoint: GET https://findwork.dev/api/jobs/
Auth: Authorization: Token <FINDWORK_API_KEY>
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

MAX_PAGES = 2


def _parse_published(value: Any) -> datetime:
    if value:
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _parse_item(item: dict[str, Any]) -> RawJob | None:
    job_id = item.get("id")
    if job_id is None:
        return None
    company = item.get("company_name") or item.get("company")
    if isinstance(company, dict):
        company = company.get("name") or company.get("display_name")
    tags_raw = item.get("keywords") or item.get("tags") or []
    tags: list[str] = []
    if isinstance(tags_raw, list):
        tags = [str(t) for t in tags_raw if t]
    elif isinstance(tags_raw, str) and tags_raw.strip():
        tags = [tags_raw.strip()]
    remote = item.get("remote")
    remote_hint: bool | None
    if isinstance(remote, bool):
        remote_hint = remote
    else:
        loc = str(item.get("location") or "").lower()
        remote_hint = True if "remote" in loc else None
    return RawJob(
        source_job_id=str(job_id),
        url=item.get("url") or item.get("job_url") or "",
        title=item.get("title") or "Untitled",
        company=str(company) if company else None,
        description=item.get("description") or item.get("text"),
        location=item.get("location"),
        published_at=_parse_published(item.get("pub_date") or item.get("created")),
        salary_text=(
            str(item["salary"])
            if item.get("salary") is not None
            else (str(item["salary_min"]) if item.get("salary_min") is not None else None)
        ),
        tags=tags,
        job_type=item.get("employment_type") or item.get("role_type"),
        remote_hint=remote_hint,
        raw=item if isinstance(item, dict) else {},
    )


class FindworkCollector(BaseCollector):
    name = "Findwork.dev"
    source_key = "findwork"
    collection_mode = "search"
    base_url = "https://findwork.dev/api/jobs/"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        settings = get_settings()
        api_key = (credential_bundle("findwork").get("api_key") or "").strip()
        if not api_key:
            return CollectorResult(
                records=[],
                pages_scanned=0,
                errors=["FINDWORK_API_KEY is required"],
            )

        search = simplify_query_for(self, query or "")
        location = settings.findwork_location.strip()
        errors: list[str] = []
        records: list[RawJob] = []
        seen: set[str] = set()
        pages_scanned = 0
        headers = {
            "Authorization": f"Token {api_key}",
            "Accept": "application/json",
            "User-Agent": "FMI-MarketIntel/1.0",
        }

        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            for page in range(1, MAX_PAGES + 1):
                params: dict[str, Any] = {"search": search, "page": page}
                if location:
                    params["location"] = location
                try:
                    resp = await client.get(self.base_url, params=params)
                    pages_scanned += 1
                    if resp.status_code in (401, 403):
                        return CollectorResult(
                            records=records,
                            pages_scanned=pages_scanned,
                            errors=[f"Findwork auth failed HTTP {resp.status_code}"],
                        )
                    resp.raise_for_status()
                    payload = resp.json() or {}
                except Exception as exc:  # noqa: BLE001
                    errors.append(str(exc))
                    break

                results = payload.get("results") or []
                if not isinstance(results, list) or not results:
                    break
                for item in results:
                    if not isinstance(item, dict):
                        continue
                    job = _parse_item(item)
                    if job is None or job.source_job_id in seen:
                        continue
                    seen.add(job.source_job_id)
                    records.append(job)
                if not payload.get("next"):
                    break

        return CollectorResult(records=records, pages_scanned=pages_scanned, errors=errors)
