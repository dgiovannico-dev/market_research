"""NAV pam-stilling-feed — authorized public dump (collection_mode=dump).

ADR-003: JWT from GET /api/publicToken (experimental; rotates). Prefer a private
consumer token for production (register with nav.team.arbeidsplassen@nav.no).

Dedupe vs ``nav_arbeidsplassen`` (search): same vacancy UUID and the same
arbeidsplassen stilling URL → ingest merges on ``canonical_url``.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from typing import Any, Optional
from urllib.parse import urljoin

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob

BASE = "https://pam-stilling-feed.nav.no"
TOKEN_URL = f"{BASE}/api/publicToken"
FEED_URL = f"{BASE}/api/v1/feed"
DETAIL_URL = "https://arbeidsplassen.nav.no/stillinger/stilling/{uuid}"

MAX_RECORDS = 100
MAX_PAGES = 3
LOOKBACK_DAYS = 7

_JWT_RE = re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")


class NavStillingFeedCollector(BaseCollector):
    name = "NAV Stillingsfeed"
    source_key = "nav_stilling_feed"
    collection_mode = "dump"
    base_url = FEED_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        q = (query or "").strip().lower()
        headers = {
            "User-Agent": "FMI-MarketIntel/1.0 (+market_research; pam-stilling-feed)",
            "Accept": "application/json",
        }
        errors: list[str] = []
        records: list[RawJob] = []
        pages = 0

        try:
            async with httpx.AsyncClient(
                timeout=45.0, headers=headers, follow_redirects=True
            ) as client:
                token = await _public_jwt(client)
                if not token:
                    return CollectorResult(
                        records=[], pages_scanned=1, errors=["publicToken: no JWT"]
                    )
                auth = {"Authorization": f"Bearer {token}"}
                ims = format_datetime(
                    datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS),
                    usegmt=True,
                )
                url: str | None = FEED_URL
                feed_headers = {**auth, "If-Modified-Since": ims}

                while url and pages < MAX_PAGES and len(records) < MAX_RECORDS:
                    try:
                        resp = await client.get(url, headers=feed_headers)
                        resp.raise_for_status()
                        payload = resp.json() or {}
                    except Exception as exc:  # noqa: BLE001
                        if pages == 0:
                            return CollectorResult(
                                records=[], pages_scanned=1, errors=[str(exc)]
                            )
                        errors.append(str(exc))
                        break

                    pages += 1
                    items = payload.get("items") if isinstance(payload, dict) else None
                    if not isinstance(items, list):
                        errors.append("unexpected feed payload")
                        break

                    for item in items:
                        if len(records) >= MAX_RECORDS:
                            break
                        if not isinstance(item, dict):
                            continue
                        mapped = _map_item(item)
                        if mapped is None:
                            continue
                        if q and not _matches(item, q):
                            continue
                        records.append(mapped)

                    next_path = payload.get("next_url") if isinstance(payload, dict) else None
                    if not next_path or len(records) >= MAX_RECORDS:
                        break
                    url = urljoin(BASE, str(next_path))
                    # Subsequent pages: keep auth; IMS only needed on the first hop.
                    feed_headers = auth
        except Exception as exc:  # noqa: BLE001
            return CollectorResult(records=[], pages_scanned=max(pages, 1), errors=[str(exc)])

        return CollectorResult(
            records=records,
            pages_scanned=max(pages, 1),
            errors=errors,
            dump_complete=False,
            meta={
                "lookback_days": LOOKBACK_DAYS,
                "feed": "pam-stilling-feed",
                "active_only": True,
            },
        )


async def _public_jwt(client: httpx.AsyncClient) -> str | None:
    resp = await client.get(TOKEN_URL, headers={"Accept": "text/plain"})
    resp.raise_for_status()
    m = _JWT_RE.search(resp.text or "")
    return m.group(0) if m else None


def _map_item(item: dict[str, Any]) -> RawJob | None:
    entry = item.get("_feed_entry") if isinstance(item.get("_feed_entry"), dict) else {}
    status = str(entry.get("status") or "").upper()
    if status != "ACTIVE":
        return None
    uid = entry.get("uuid") or item.get("id")
    title = entry.get("title") or item.get("title") or "Untitled"
    if not uid:
        return None
    company = entry.get("businessName")
    municipal = entry.get("municipal")
    location = f"{municipal}, Norway" if municipal else "Norway"
    return RawJob(
        source_job_id=str(uid),
        url=DETAIL_URL.format(uuid=uid),
        title=str(title).strip() or "Untitled",
        company=str(company).strip() if company else None,
        description=None,
        location=location,
        published_at=_published(item.get("date_modified") or entry.get("sistEndret")),
        salary_text=None,
        tags=[],
        job_type=None,
        remote_hint=None,
        raw={
            "uuid": uid,
            "status": status,
            "businessName": company,
            "municipal": municipal,
            "date_modified": item.get("date_modified"),
            "feed_entry_url": item.get("url"),
            "country_code": "NO",
        },
    )


def _matches(item: dict[str, Any], q: str) -> bool:
    entry = item.get("_feed_entry") if isinstance(item.get("_feed_entry"), dict) else {}
    hay = " ".join(
        [
            str(item.get("title") or ""),
            str(entry.get("title") or ""),
            str(entry.get("businessName") or ""),
            str(entry.get("municipal") or ""),
        ]
    ).lower()
    return q in hay


def _published(raw: Any) -> datetime:
    if raw:
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)
