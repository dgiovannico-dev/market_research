"""Pinpoint public postings.json (per-subdomain allowlist; no API key)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob
from app.core.config import get_settings

MAX_PER_TENANT = 40


def _split_csv(value: str) -> list[str]:
    return [p.strip() for p in value.split(",") if p.strip()]


def _location(item: dict[str, Any]) -> str | None:
    loc = item.get("location")
    if isinstance(loc, str) and loc.strip():
        return loc.strip()
    if isinstance(loc, dict):
        name = loc.get("name")
        city = loc.get("city")
        province = loc.get("province")
        # Pinpoint sometimes stubs city/province as "l"
        parts: list[str] = []
        if name and str(name).strip() and str(name).strip().lower() != "l":
            parts.append(str(name).strip())
        else:
            for p in (city, province):
                if p and str(p).strip() and str(p).strip().lower() != "l":
                    parts.append(str(p).strip())
        return ", ".join(parts) if parts else None
    return None


def _remote_hint(item: dict[str, Any]) -> bool | None:
    wtype = (item.get("workplace_type") or item.get("workplace_type_text") or "").lower()
    if "remote" in wtype and "hybrid" not in wtype:
        return True
    if "onsite" in wtype or "on-site" in wtype or "office" in wtype:
        return False
    if "hybrid" in wtype:
        return None
    return None


def _salary_text(item: dict[str, Any]) -> str | None:
    comp = item.get("compensation")
    if isinstance(comp, str) and comp.strip():
        return comp.strip()
    lo = item.get("compensation_minimum")
    hi = item.get("compensation_maximum")
    cur = item.get("compensation_currency") or ""
    if lo is None and hi is None:
        return None
    if lo is not None and hi is not None:
        return f"{cur} {lo} - {hi}".strip()
    return f"{cur} {lo or hi}".strip()


def _tags(item: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    if item.get("employment_type_text"):
        tags.append(str(item["employment_type_text"]))
    if item.get("workplace_type_text"):
        tags.append(str(item["workplace_type_text"]))
    job = item.get("job") if isinstance(item.get("job"), dict) else {}
    for key in ("department", "division", "structure_custom_group_one"):
        node = job.get(key) if isinstance(job, dict) else None
        if isinstance(node, dict) and node.get("name"):
            tags.append(str(node["name"]))
    dept = item.get("department")
    if isinstance(dept, dict) and dept.get("name"):
        tags.append(str(dept["name"]))
    elif isinstance(dept, str) and dept.strip():
        tags.append(dept.strip())
    # dedupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out[:12]


class PinpointCollector(BaseCollector):
    name = "Pinpoint Postings"
    source_key = "pinpoint"
    collection_mode = "dump"
    base_url_tmpl = "https://{subdomain}.pinpointhq.com/postings.json"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        subdomains = [s.lower() for s in _split_csv(get_settings().pinpoint_subdomains)]
        if not subdomains:
            return CollectorResult(records=[], errors=["PINPOINT_SUBDOMAINS empty"])
        errors: list[str] = []
        records: list[RawJob] = []
        q = (query or "").lower().strip()
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        now = datetime.now(timezone.utc)

        async with httpx.AsyncClient(timeout=45.0, headers=headers, follow_redirects=True) as client:
            for subdomain in subdomains:
                matched = 0
                try:
                    resp = await client.get(self.base_url_tmpl.format(subdomain=subdomain))
                    resp.raise_for_status()
                    payload = resp.json() or {}
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{subdomain}: {exc}")
                    continue
                data = payload.get("data") if isinstance(payload, dict) else payload
                if not isinstance(data, list):
                    errors.append(f"{subdomain}: unexpected payload")
                    continue
                for item in data:
                    if matched >= MAX_PER_TENANT:
                        break
                    if not isinstance(item, dict):
                        continue
                    title = item.get("title") or "Untitled"
                    if q and q not in title.lower():
                        continue
                    job_id = item.get("id")
                    if job_id is None:
                        continue
                    url = item.get("url") or ""
                    if not url and item.get("path"):
                        url = f"https://{subdomain}.pinpointhq.com{item['path']}"
                    records.append(
                        RawJob(
                            source_job_id=f"{subdomain}:{job_id}",
                            url=url,
                            title=title,
                            company=subdomain,
                            description=(
                                item.get("description")
                                if isinstance(item.get("description"), str) and item["description"].strip()
                                else None
                            ),
                            location=_location(item),
                            published_at=now,
                            salary_text=_salary_text(item),
                            tags=_tags(item),
                            job_type=item.get("employment_type_text"),
                            remote_hint=_remote_hint(item),
                            raw={
                                "id": job_id,
                                "title": title,
                                "subdomain": subdomain,
                                "workplace_type": item.get("workplace_type"),
                            },
                        )
                    )
                    matched += 1

        return CollectorResult(records=records, pages_scanned=len(subdomains), errors=errors)
