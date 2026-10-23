"""Text rematch of focus intents onto existing jobs (no re-crawl).

Historical jobs often lack ``job_intent_matches`` because matches are only
written when ``upsert_raw_job`` receives ``query_id`` during ingest. This
module backfills focus provenance by matching intent ``query_text`` tokens
against title / description / linked technology names.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ingestion.service import upsert_intent_match
from app.storage.models import Job, JobSkill, SearchQuery, Technology

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:\.[a-z0-9]+)*", re.IGNORECASE)

# Role / contract modifiers common in seed focus labels — not required for a hit.
_WEAK_TOKENS = frozenset(
    {
        "a",
        "an",
        "and",
        "b2b",
        "consultant",
        "contractor",
        "developer",
        "engineer",
        "for",
        "freelance",
        "freelancer",
        "infrastructure",
        "job",
        "jobs",
        "junior",
        "lead",
        "mid",
        "or",
        "principal",
        "remote",
        "role",
        "senior",
        "software",
        "staff",
        "the",
        "with",
    }
)


def query_signal_tokens(query_text: str) -> list[str]:
    """Extract distinctive tokens from an intent query (order preserved)."""
    raw = [t.lower() for t in _TOKEN_RE.findall(query_text or "")]
    signal = [t for t in raw if t not in _WEAK_TOKENS and len(t) >= 2]
    if not signal:
        signal = [t for t in raw if len(t) >= 3]
    seen: set[str] = set()
    out: list[str] = []
    for tok in signal:
        if tok not in seen:
            seen.add(tok)
            out.append(tok)
    return out


def tokens_match_haystack(tokens: Sequence[str], haystack: str) -> bool:
    """True when every token appears as a whole word in ``haystack``."""
    if not tokens:
        return False
    text = haystack.lower()
    for tok in tokens:
        if not re.search(rf"(?<![a-z0-9]){re.escape(tok)}(?![a-z0-9])", text):
            return False
    return True


def job_search_text(job: Job, tech_names: Sequence[str] = ()) -> str:
    parts = [
        job.title_original or "",
        job.title_normalized or "",
        job.description_original or "",
        " ".join(tech_names),
    ]
    return " ".join(p for p in parts if p)


def rematch_focus_intents(
    db: Session,
    *,
    query_ids: Optional[Sequence[int]] = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Match enabled focus intents to canonical jobs; upsert JobIntentMatch rows.

    Returns counts: intents, jobs_scanned, candidates, created, updated, skipped.
    """
    intent_q = select(SearchQuery).where(
        SearchQuery.kind == "focus",
        SearchQuery.deleted_at.is_(None),
        SearchQuery.enabled.is_(True),
    )
    if query_ids:
        intent_q = intent_q.where(SearchQuery.id.in_(list(query_ids)))
    intents = list(db.scalars(intent_q).all())

    jobs = list(
        db.scalars(select(Job).where(Job.is_canonical.is_(True))).all()
    )
    job_ids = [j.id for j in jobs]
    tech_by_job: dict[int, list[str]] = defaultdict(list)
    if job_ids:
        for jid, name in db.execute(
            select(JobSkill.job_id, Technology.canonical_name)
            .join(Technology, Technology.id == JobSkill.technology_id)
            .where(JobSkill.job_id.in_(job_ids))
        ).all():
            tech_by_job[int(jid)].append(str(name))

    now = datetime.now(timezone.utc)
    created = updated = skipped = candidates = 0
    per_intent: list[dict[str, Any]] = []

    for intent in intents:
        tokens = query_signal_tokens(intent.query_text)
        hit_jobs = 0
        for job in jobs:
            haystack = job_search_text(job, tech_by_job.get(job.id, []))
            if not tokens_match_haystack(tokens, haystack):
                continue
            candidates += 1
            hit_jobs += 1
            if dry_run:
                skipped += 1
                continue
            action = upsert_intent_match(
                db, job_id=job.id, query_id=intent.id, matched_at=now
            )
            if action == "created":
                created += 1
            else:
                updated += 1
        per_intent.append(
            {
                "query_id": intent.id,
                "name": intent.name,
                "tokens": tokens,
                "hits": hit_jobs,
            }
        )

    if not dry_run and (created or updated):
        db.flush()

    return {
        "intents": len(intents),
        "jobs_scanned": len(jobs),
        "candidates": candidates,
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "dry_run": dry_run,
        "per_intent": per_intent,
    }
