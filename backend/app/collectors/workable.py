"""Workable public careers widget JSON (per-slug allowlist; no API key)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob
from app.core.config import get_settings

MAX_PER_TENANT = 40


def _split_csv(value: str) -> list[str]:
    return [p.strip() for p in value.split(",") if p.strip()]


def _parse_published(value: Any) -> datetime:
    published = datetime.now(timezone.utc)
    if not value:
        return published
    text = str(value).strip()
    # widget often returns YYYY-MM-DD
    if len(text) == 10 and text[4] == "-" and text[7] == "-":
        text = text + "T00:00:00+00:00"
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return published


def _location(item: dict[str, Any]) -> str | None:
    parts = [str(p) for p in (item.get("city"), item.get("state"), item.get("country")) if p]
    if parts:
        return ", ".join(parts)
    locs = item.get("locations")
    if isinstance(locs, list) and locs:
        first = locs[0]
        if isinstance(first, dict):
            chunk = ", ".join(
                str(p) for p in (first.get("city"), first.get("region"), first.get("country")) if p
            )
            return chunk or None
        if isinstance(first, str) and first.strip():
            return first.strip()
    return None


class WorkableCollector(BaseCollector):
    name = "Workable Careers Widget"
    source_key = "workable"
    collection_mode = "dump"
    base_url_tmpl = "https://apply.workable.com/api/v1/widget/accounts/{slug}"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        slugs = [s.lower() for s in _split_csv(get_settings().workable_slugs)]
        if not slugs:
            return CollectorResult(records=[], errors=["WORKABLE_SLUGS empty"])
        errors: list[str] = []
        records: list[RawJob] = []
        q = (query or "").lower().strip()
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}

        async with httpx.AsyncClient(timeout=45.0, headers=headers, follow_redirects=True) as client:
            for slug in slugs:
                matched = 0
                try:
                    resp = await client.get(
                        self.base_url_tmpl.format(slug=slug),
                        params={"details": "true"},
                    )
                    resp.raise_for_status()
                    payload = resp.json() or {}
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{slug}: {exc}")
                    continue
                if not isinstance(payload, dict):
                    errors.append(f"{slug}: unexpected payload")
                    continue
                company = payload.get("name") or slug
                jobs = payload.get("jobs") or []
                if not isinstance(jobs, list):
                    errors.append(f"{slug}: jobs not a list")
                    continue
                for item in jobs:
                    if matched >= MAX_PER_TENANT:
                        break
                    if not isinstance(item, dict):
                        continue
                    title = item.get("title") or "Untitled"
                    if q and q not in title.lower():
                        continue
                    shortcode = item.get("shortcode") or item.get("code")
                    if not shortcode:
                        continue
                    url = item.get("url") or item.get("shortlink") or item.get("application_url") or ""
                    tags = [t for t in (item.get("department"), item.get("employment_type")) if t]
                    records.append(
                        RawJob(
                            source_job_id=f"{slug}:{shortcode}",
                            url=url,
                            title=title,
                            company=company,
                            description=(
                                item.get("description")
                                if isinstance(item.get("description"), str) and item["description"].strip()
                                else None
                            ),
                            location=_location(item),
                            published_at=_parse_published(item.get("published_on") or item.get("created_at")),
                            tags=tags[:12],
                            job_type=item.get("employment_type"),
                            remote_hint=True if item.get("telecommuting") is True else (
                                False if item.get("telecommuting") is False else None
                            ),
                            raw={
                                "shortcode": shortcode,
                                "title": title,
                                "slug": slug,
                                "telecommuting": item.get("telecommuting"),
                            },
                        )
                    )
                    matched += 1

        return CollectorResult(records=records, pages_scanned=len(slugs), errors=errors)
