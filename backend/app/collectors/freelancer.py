"""Freelancer.com projects API — requires FREELANCER_OAUTH_TOKEN.

Docs: https://developers.freelancer.com/
Endpoint: GET {base}/projects/0.1/projects/active/
Auth: Authorization: Bearer <token>
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
    if value is None or value == "":
        return datetime.now(timezone.utc)
    # API often returns unix seconds
    try:
        if isinstance(value, (int, float)) or str(value).isdigit():
            return datetime.fromtimestamp(int(value), tz=timezone.utc)
    except (ValueError, OSError, OverflowError):
        pass
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)


def _salary_text(item: dict[str, Any]) -> str | None:
    budget = item.get("budget")
    currency = item.get("currency")
    cur_code = ""
    if isinstance(currency, dict):
        cur_code = str(currency.get("code") or "")
    elif isinstance(currency, str):
        cur_code = currency
    if isinstance(budget, dict):
        lo, hi = budget.get("minimum"), budget.get("maximum")
        if lo is not None and hi is not None:
            return f"{cur_code} {lo}-{hi}".strip()
        if lo is not None:
            return f"{cur_code} {lo}".strip()
    return None


def _tags(item: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for key in ("jobs", "skills"):
        raw = item.get(key) or []
        if not isinstance(raw, list):
            continue
        for node in raw:
            if isinstance(node, dict) and node.get("name"):
                out.append(str(node["name"]))
            elif isinstance(node, str) and node.strip():
                out.append(node.strip())
    seen: set[str] = set()
    deduped: list[str] = []
    for t in out:
        if t not in seen:
            seen.add(t)
            deduped.append(t)
    return deduped[:12]


def _parse_item(item: dict[str, Any]) -> RawJob | None:
    job_id = item.get("id")
    if job_id is None:
        return None
    seo = item.get("seo_url") or item.get("url") or ""
    if seo and not str(seo).startswith("http"):
        seo = f"https://www.freelancer.com/projects/{str(seo).lstrip('/')}"
    owner = item.get("owner") or item.get("employer")
    company = None
    if isinstance(owner, dict):
        company = owner.get("username") or owner.get("display_name") or owner.get("name")
    title = item.get("title") or "Untitled"
    desc = item.get("preview_description") or item.get("description")
    return RawJob(
        source_job_id=str(job_id),
        url=str(seo) if seo else f"https://www.freelancer.com/projects/{job_id}",
        title=str(title),
        company=str(company) if company else None,
        description=str(desc) if desc else None,
        location=None,
        published_at=_parse_published(item.get("time_updated") or item.get("time_submitted")),
        salary_text=_salary_text(item),
        tags=_tags(item),
        job_type=item.get("type"),
        remote_hint=True,
        raw=item,
    )


class FreelancerCollector(BaseCollector):
    name = "Freelancer.com"
    source_key = "freelancer"
    collection_mode = "search"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        settings = get_settings()
        token = (credential_bundle("freelancer").get("oauth_token") or "").strip()
        if not token:
            return CollectorResult(
                records=[],
                pages_scanned=0,
                errors=["FREELANCER_OAUTH_TOKEN is required"],
            )

        search = simplify_query_for(self, query or "")
        base = settings.freelancer_api_base.rstrip("/") or "https://www.freelancer.com/api"
        url = f"{base}/projects/0.1/projects/active/"
        headers = {
            "Authorization": f"Bearer {token}",
            "Freelancer-OAuth-V1": token,
            "Accept": "application/json",
            "User-Agent": "FMI-MarketIntel/1.0",
        }
        params: dict[str, Any] = {
            "query": search,
            "limit": MAX_RECORDS,
            "offset": 0,
            "compact": "true",
        }

        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            try:
                resp = await client.get(url, params=params)
                if resp.status_code in (401, 403):
                    return CollectorResult(
                        records=[],
                        pages_scanned=1,
                        errors=[f"Freelancer auth failed HTTP {resp.status_code}"],
                    )
                resp.raise_for_status()
                payload = resp.json() or {}
            except Exception as exc:  # noqa: BLE001
                return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        result = payload.get("result") if isinstance(payload, dict) else None
        projects: list[Any] = []
        if isinstance(result, dict):
            projects = result.get("projects") or []
        elif isinstance(payload, dict):
            projects = payload.get("projects") or []

        records: list[RawJob] = []
        seen: set[str] = set()
        for item in projects:
            if not isinstance(item, dict):
                continue
            job = _parse_item(item)
            if job is None or job.source_job_id in seen:
                continue
            seen.add(job.source_job_id)
            records.append(job)
            if len(records) >= MAX_RECORDS:
                break

        return CollectorResult(records=records, pages_scanned=1, errors=[])
