"""Workday public career CXS JSON (per-tenant allowlist; no API key).

POST https://{tenant}.{wd}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs
Body: {"appliedFacets":{},"limit":N,"offset":0,"searchText":""}
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob
from app.core.config import get_settings

MAX_PER_TENANT = 40
PAGE_LIMIT = 20


def _split_tenants(value: str) -> list[tuple[str, str, str]]:
    """Parse CSV of tenant:wdN:siteSlug (site may contain underscores)."""
    out: list[tuple[str, str, str]] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        bits = part.split(":", 2)
        if len(bits) != 3:
            continue
        tenant, wd, site = (b.strip() for b in bits)
        if not tenant or not wd or not site:
            continue
        wd_norm = wd.lower()
        if not wd_norm.startswith("wd"):
            wd_norm = f"wd{wd_norm}"
        out.append((tenant.lower(), wd_norm, site))
    return out


def _job_id(tenant: str, item: dict[str, Any]) -> str | None:
    bullets = item.get("bulletFields")
    if isinstance(bullets, list) and bullets:
        first = bullets[0]
        if first is not None and str(first).strip():
            return f"{tenant}:{str(first).strip()}"
    path = item.get("externalPath")
    if isinstance(path, str) and path.strip():
        # last path segment often includes JR requisition id
        slug = path.rstrip("/").rsplit("/", 1)[-1]
        return f"{tenant}:{slug}" if slug else None
    return None


def _job_url(tenant: str, wd: str, site: str, external_path: str) -> str:
    path = external_path if external_path.startswith("/") else f"/{external_path}"
    return f"https://{tenant}.{wd}.myworkdayjobs.com/{site}{path}"


def _remote_hint(item: dict[str, Any]) -> bool | None:
    text = " ".join(
        str(p)
        for p in (
            item.get("locationsText"),
            item.get("title"),
            " ".join(str(b) for b in (item.get("bulletFields") or []) if b),
        )
        if p
    ).lower()
    if "remote" in text and "hybrid" not in text:
        return True
    if "hybrid" in text:
        return None
    return None


def _parse_posted_on(value: Any) -> datetime:
    """Workday list often returns relative 'Posted Today' — use now."""
    return datetime.now(timezone.utc)


class WorkdayCollector(BaseCollector):
    name = "Workday Careers CXS"
    source_key = "workday"
    collection_mode = "dump"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        tenants = _split_tenants(get_settings().workday_tenants)
        if not tenants:
            return CollectorResult(records=[], errors=["WORKDAY_TENANTS empty"])
        errors: list[str] = []
        records: list[RawJob] = []
        q = (query or "").lower().strip()
        headers = {
            "User-Agent": "FMI-MarketIntel/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=45.0, headers=headers, follow_redirects=True) as client:
            for tenant, wd, site in tenants:
                matched = 0
                offset = 0
                host = f"{tenant}.{wd}.myworkdayjobs.com"
                url = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
                company = tenant.replace("-", " ").title()
                while matched < MAX_PER_TENANT:
                    body = {
                        "appliedFacets": {},
                        "limit": min(PAGE_LIMIT, MAX_PER_TENANT - matched),
                        "offset": offset,
                        "searchText": "",
                    }
                    try:
                        resp = await client.post(url, json=body)
                        resp.raise_for_status()
                        payload = resp.json() or {}
                    except Exception as exc:  # noqa: BLE001
                        errors.append(f"{tenant}/{wd}/{site}: {exc}")
                        break
                    if not isinstance(payload, dict):
                        errors.append(f"{tenant}/{wd}/{site}: unexpected payload")
                        break
                    jobs = payload.get("jobPostings") or []
                    if not isinstance(jobs, list) or not jobs:
                        break
                    total = payload.get("total")
                    for item in jobs:
                        if matched >= MAX_PER_TENANT:
                            break
                        if not isinstance(item, dict):
                            continue
                        title = item.get("title") or "Untitled"
                        if q and q not in title.lower():
                            continue
                        jid = _job_id(tenant, item)
                        path = item.get("externalPath")
                        if not jid or not isinstance(path, str) or not path.strip():
                            continue
                        records.append(
                            RawJob(
                                source_job_id=jid,
                                url=_job_url(tenant, wd, site, path.strip()),
                                title=title,
                                company=company,
                                description=None,
                                location=(
                                    str(item["locationsText"]).strip()
                                    if item.get("locationsText")
                                    else None
                                ),
                                published_at=_parse_posted_on(item.get("postedOn")),
                                salary_text=None,
                                tags=[],
                                job_type=None,
                                remote_hint=_remote_hint(item),
                                raw=item,
                            )
                        )
                        matched += 1
                    offset += len(jobs)
                    if isinstance(total, int) and offset >= total:
                        break
                    if len(jobs) < PAGE_LIMIT:
                        break

        return CollectorResult(records=records, errors=errors)
