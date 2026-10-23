"""Hacker News 'Who is hiring?' via public Algolia API (no key; not HTML scrape)."""

from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob

_TAG_RE = re.compile(r"<[^>]+>")
_SEEK_RE = re.compile(
    r"\b(seeking work|looking for work|available for hire|seeking (an )?opportunity)\b",
    re.I,
)


def _plain(text: str) -> str:
    return html.unescape(_TAG_RE.sub(" ", text or "")).strip()


def _is_hiring_comment(text: str) -> bool:
    if not text or _SEEK_RE.search(text):
        return False
    low = text.lower()
    if "|" in text:
        return True
    return any(p in low for p in ("is hiring", "we're hiring", "we are hiring", "hiring for"))


def _parse_title_company(text: str) -> tuple[str, str | None]:
    first = text.split("\n", 1)[0].strip()
    if "|" in first:
        parts = [p.strip() for p in first.split("|") if p.strip()]
        company = parts[0] if parts else None
        title = " | ".join(parts[1:3]) if len(parts) > 1 else first
        return title or "Hiring", company
    return first[:180] or "Hiring", None


class HnWhoIsHiringCollector(BaseCollector):
    name = "HN Who is hiring"
    source_key = "hn_whoishiring"
    collection_mode = "feed"
    search_url = "https://hn.algolia.com/api/v1/search_by_date"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        errors: list[str] = []
        records: list[RawJob] = []
        q = (query or "").lower().strip()

        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            try:
                story_resp = await client.get(
                    self.search_url,
                    params={"tags": "story,author_whoishiring", "hitsPerPage": 1},
                )
                story_resp.raise_for_status()
                stories = (story_resp.json() or {}).get("hits") or []
            except Exception as exc:  # noqa: BLE001
                return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

            if not stories:
                return CollectorResult(records=[], pages_scanned=1, errors=["no whoishiring story"])

            story = stories[0]
            story_id = str(story.get("objectID") or "")
            story_title = story.get("title") or "Who is hiring?"
            if not story_id:
                return CollectorResult(records=[], pages_scanned=1, errors=["missing story id"])

            pages = 0
            for page in range(3):
                try:
                    resp = await client.get(
                        self.search_url,
                        params={
                            "tags": f"comment,story_{story_id}",
                            "hitsPerPage": 100,
                            "page": page,
                        },
                    )
                    resp.raise_for_status()
                    payload = resp.json() or {}
                except Exception as exc:  # noqa: BLE001
                    errors.append(str(exc))
                    break
                pages += 1
                hits = payload.get("hits") or []
                if not hits:
                    break
                for hit in hits:
                    text = _plain(hit.get("comment_text") or "")
                    if not _is_hiring_comment(text):
                        continue
                    if q and q not in text.lower():
                        continue
                    object_id = hit.get("objectID")
                    if not object_id:
                        continue
                    title, company = _parse_title_company(text)
                    created = hit.get("created_at")
                    published = datetime.now(timezone.utc)
                    if created:
                        try:
                            published = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
                        except ValueError:
                            pass
                    url = f"https://news.ycombinator.com/item?id={object_id}"
                    remote = None
                    low = text.lower()
                    if "remote" in low:
                        remote = True
                    records.append(
                        RawJob(
                            source_job_id=str(object_id),
                            url=url,
                            title=title,
                            company=company,
                            description=text[:8000],
                            location="Remote" if remote else None,
                            published_at=published,
                            tags=[story_title[:80]],
                            remote_hint=remote,
                            raw={"story_id": story_id, "author": hit.get("author")},
                        )
                    )
                nb_pages = int(payload.get("nbPages") or 1)
                if page + 1 >= nb_pages:
                    break

        return CollectorResult(records=records, pages_scanned=max(pages, 1), errors=errors)
