"""USAJOBS Search API — requires USAJOBS_API_KEY (+ User-Agent email)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

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


class USAJobsCollector(BaseCollector):
    name = "USAJOBS"
    source_key = "usajobs"
    collection_mode = "search"
    base_url = "https://data.usajobs.gov/api/search"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        settings = get_settings()
        creds = credential_bundle("usajobs")
        api_key = (creds.get("api_key") or "").strip()
        user_agent = (creds.get("user_agent") or "").strip()
        if not api_key:
            return CollectorResult(
                records=[],
                pages_scanned=0,
                errors=["USAJOBS_API_KEY is required"],
            )
        if not user_agent:
            return CollectorResult(
                records=[],
                pages_scanned=0,
                errors=["USAJOBS_USER_AGENT (contact email) is required"],
            )

        keyword = simplify_query_for(self, query or "")
        params: dict[str, str | int] = {
            "Keyword": keyword,
            "ResultsPerPage": 50,
            "Page": 1,
        }
        category = settings.usajobs_job_category_code.strip()
        if category:
            params["JobCategoryCode"] = category
        headers = {
            "Host": "data.usajobs.gov",
            "User-Agent": user_agent,
            "Authorization-Key": api_key,
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            try:
                resp = await client.get(self.base_url, params=params, headers=headers)
                if resp.status_code in (401, 403):
                    return CollectorResult(
                        records=[],
                        pages_scanned=1,
                        errors=[f"USAJOBS auth failed HTTP {resp.status_code}"],
                    )
                resp.raise_for_status()
                payload = resp.json()
            except Exception as exc:  # noqa: BLE001
                return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        items = ((payload or {}).get("SearchResult") or {}).get("SearchResultItems") or []
        records: list[RawJob] = []
        for row in items:
            desc = row.get("MatchedObjectDescriptor") or {}
            job_id = str(row.get("MatchedObjectId") or desc.get("PositionID") or "")
            if not job_id:
                continue
            pub_raw = desc.get("PublicationStartDate") or desc.get("PositionStartDate")
            published = datetime.now(timezone.utc)
            if pub_raw:
                try:
                    published = datetime.fromisoformat(str(pub_raw).replace("Z", "+00:00"))
                except ValueError:
                    pass
            user_area = desc.get("UserArea") or {}
            details = user_area.get("Details") if isinstance(user_area, dict) else {}
            summary = None
            if isinstance(details, dict):
                summary = details.get("JobSummary") or details.get("MajorDuties")
            if isinstance(summary, list):
                summary = "\n".join(str(x) for x in summary)
            schedule = desc.get("PositionSchedule")
            job_type = None
            if isinstance(schedule, list) and schedule:
                first = schedule[0]
                if isinstance(first, dict):
                    job_type = first.get("Name")
            records.append(
                RawJob(
                    source_job_id=job_id,
                    url=desc.get("PositionURI") or "",
                    title=desc.get("PositionTitle") or "Untitled",
                    company=desc.get("OrganizationName"),
                    description=summary if isinstance(summary, str) else None,
                    location=desc.get("PositionLocationDisplay"),
                    published_at=published,
                    salary_text=None,
                    tags=[],
                    job_type=job_type,
                    remote_hint=None,
                    raw=row if isinstance(row, dict) else {},
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=[])
