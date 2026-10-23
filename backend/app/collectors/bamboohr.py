"""BambooHR public careers JSON (per-subdomain allowlist; no API key).

List: GET https://{slug}.bamboohr.com/careers/list
Optional detail: GET https://{slug}.bamboohr.com/careers/{id}/detail (description / share URL).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob
from app.core.config import get_settings

MAX_PER_TENANT = 40
# Cap detail fetches to keep multi-tenant runs bounded
MAX_DETAIL_PER_TENANT = 15


def _split_csv(value: str) -> list[str]:
    return [p.strip() for p in value.split(",") if p.strip()]


def _parse_dt(value: Any) -> datetime:
    published = datetime.now(timezone.utc)
    if not value:
        return published
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return published


def _location(item: dict[str, Any]) -> str | None:
    loc = item.get("location")
    if isinstance(loc, str) and loc.strip():
        return loc.strip()
    if isinstance(loc, dict):
        parts = [
            str(p)
            for p in (loc.get("city"), loc.get("state"), loc.get("addressCountry"), loc.get("country"))
            if p
        ]
        return ", ".join(parts) if parts else None
    return None


def _remote_hint(item: dict[str, Any]) -> bool | None:
    if item.get("isRemote") is True:
        return True
    ltype = str(item.get("locationType") or "").lower()
    if "remote" in ltype:
        return True
    if "hybrid" in ltype:
        return None
    if "office" in ltype or "onsite" in ltype or "on-site" in ltype:
        return False
    return None


class BambooHRCollector(BaseCollector):
    name = "BambooHR Careers"
    source_key = "bamboohr"
    collection_mode = "dump"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        slugs = [s.lower() for s in _split_csv(get_settings().bamboohr_companies)]
        if not slugs:
            return CollectorResult(
                records=[],
                errors=[
                    "BAMBOOHR_COMPANIES empty — probe careers/list then set CSV "
                    "(docs/sources/ATS_TENANTS.md)"
                ],
            )
        errors: list[str] = []
        records: list[RawJob] = []
        q = (query or "").lower().strip()
        headers = {
            "User-Agent": "FMI-MarketIntel/1.0",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(
            timeout=45.0, headers=headers, follow_redirects=False
        ) as client:
            for slug in slugs:
                matched = 0
                list_url = f"https://{slug}.bamboohr.com/careers/list"
                try:
                    resp = await client.get(list_url)
                    if resp.status_code in {301, 302, 303, 307, 308}:
                        errors.append(f"{slug}: redirect (not a careers board)")
                        continue
                    if resp.status_code == 503:
                        errors.append(
                            f"{slug}: HTTP 503 (BambooHR often blocks datacenter "
                            "egress — re-probe from residential)"
                        )
                        continue
                    resp.raise_for_status()
                    payload = resp.json() or {}
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{slug}: {exc}")
                    continue
                result = payload.get("result") if isinstance(payload, dict) else payload
                if not isinstance(result, list):
                    errors.append(f"{slug}: unexpected payload")
                    continue
                if not result:
                    errors.append(f"{slug}: empty careers list")
                    continue
                for item in result:
                    if matched >= MAX_PER_TENANT:
                        break
                    if not isinstance(item, dict):
                        continue
                    title = item.get("jobOpeningName") or item.get("name") or "Untitled"
                    if q and q not in title.lower():
                        continue
                    job_id = item.get("id")
                    if job_id is None:
                        continue
                    desc = None
                    url = ""
                    published = datetime.now(timezone.utc)
                    salary_text = None
                    location = _location(item)
                    remote = _remote_hint(item)
                    if matched < MAX_DETAIL_PER_TENANT:
                        try:
                            det = await client.get(
                                f"https://{slug}.bamboohr.com/careers/{job_id}/detail"
                            )
                            if det.status_code == 200:
                                dpay = det.json() or {}
                                opening = (
                                    (dpay.get("result") or {}).get("jobOpening")
                                    if isinstance(dpay, dict)
                                    else None
                                )
                                if isinstance(opening, dict):
                                    desc = opening.get("description") or desc
                                    url = opening.get("jobOpeningShareUrl") or url
                                    if opening.get("datePosted"):
                                        published = _parse_dt(opening.get("datePosted"))
                                    salary_text = opening.get("compensation")
                                    location = _location(opening) or location
                                    remote = _remote_hint(opening) if opening.get("isRemote") is not None or opening.get("locationType") else remote
                        except Exception:  # noqa: BLE001
                            pass
                    if not url:
                        url = f"https://{slug}.bamboohr.com/careers/{job_id}"
                    tags = [
                        t
                        for t in (
                            item.get("departmentLabel"),
                            item.get("employmentStatusLabel"),
                            item.get("employmentType"),
                        )
                        if t
                    ]
                    records.append(
                        RawJob(
                            source_job_id=f"{slug}:{job_id}",
                            url=url,
                            title=title,
                            company=slug,
                            description=desc if isinstance(desc, str) and desc.strip() else None,
                            location=location,
                            published_at=published,
                            salary_text=salary_text if isinstance(salary_text, str) else None,
                            tags=tags[:12],
                            job_type=item.get("employmentType") or item.get("employmentStatusLabel"),
                            remote_hint=remote,
                            raw={"id": job_id, "title": title, "slug": slug},
                        )
                    )
                    matched += 1

        if not records and errors and all("503" in e for e in errors):
            errors.append(
                "all slugs HTTP 503 — leave BAMBOOHR_COMPANIES empty until a "
                "residential probe returns 200 + jobs"
            )
        return CollectorResult(records=records, pages_scanned=len(slugs), errors=errors)
