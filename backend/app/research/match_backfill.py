"""Corpus rematch: link existing jobs to research intents via query tokens.

Dump/feed ingest creates unlabeled jobs (no ``job_intent_matches``). Focus/discovery
lenses need match rows; crawl-time upsert covers new hits, this backfill covers the
already-stored corpus without re-crawling.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Literal, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ingestion.service import upsert_intent_match
from app.storage.models import Job, JobIntentMatch, JobSkill, SearchQuery, Technology

IntentKind = Literal["focus", "discovery", "all"]

_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "for",
        "in",
        "of",
        "or",
        "the",
        "to",
        "with",
        "/",
    }
)
# Common role fillers in seed focus labels — optional when a tech/core token hits.
_ROLE_FILLERS = frozenset(
    {
        "architect",
        "b2b",
        "consultant",
        "contract",
        "contractor",
        "engineer",
        "freelance",
        "independent",
        "junior",
        "lead",
        "principal",
        "remote",
        "senior",
        "staff",
    }
)
_ALIASES = {
    "k8s": "kubernetes",
    "nodejs": "node",
    "node.js": "node",
    "golang": "go",
    "js": "javascript",
    "ts": "typescript",
    "reactjs": "react",
    "react.js": "react",
    "vuejs": "vue",
    "vue.js": "vue",
    "nextjs": "next.js",
    "postgres": "postgresql",
    "tf": "terraform",
    "genai": "generative ai",
    "llm": "llm",
    "llms": "llm",
    "pentest": "penetration testing",
    "appsec": "appsec",
    "devsecops": "devsecops",
    "infosec": "cybersecurity",
    "mlops": "mlops",
    "pytorch": "pytorch",
    "tensorflow": "tensorflow",
    "sklearn": "scikit-learn",
    "huggingface": "hugging face",
    "bedrock": "aws bedrock",
    "sagemaker": "sagemaker",
}


def _normalize_token(raw: str) -> str:
    t = raw.strip().lower()
    t = _ALIASES.get(t, t)
    return t


def tokenize_query_clauses(query_text: str) -> list[list[str]]:
    """Split ``OR`` groups; each group is an AND of significant tokens."""
    text = (query_text or "").strip()
    if not text:
        return []
    clauses: list[list[str]] = []
    for part in re.split(r"\bOR\b", text, flags=re.IGNORECASE):
        tokens: list[str] = []
        for raw in re.split(r"[^a-zA-Z0-9.+#]+", part):
            tok = _normalize_token(raw)
            if not tok or tok in _STOPWORDS:
                continue
            if len(tok) < 2:
                continue
            if tok not in tokens:
                tokens.append(tok)
        if tokens:
            clauses.append(tokens)
    return clauses


def _token_in_haystack(token: str, haystack: str) -> bool:
    if len(token) <= 3:
        return re.search(rf"(?<![a-z0-9]){re.escape(token)}(?![a-z0-9])", haystack) is not None
    return token in haystack


# Ambiguous short cores: require a role filler (or a second core) so "AI" alone
# does not match every description that mentions the letters as a product name.
_AMBIGUOUS_CORE = frozenset({"ai", "ml", "it"})


def clause_matches(haystack: str, tokens: Sequence[str]) -> bool:
    """True when all core (non-role) tokens hit; role-only clauses require all tokens."""
    if not tokens:
        return False
    core = [t for t in tokens if t not in _ROLE_FILLERS]
    fillers = [t for t in tokens if t in _ROLE_FILLERS]
    if not core:
        return all(_token_in_haystack(t, haystack) for t in tokens)
    if not all(_token_in_haystack(t, haystack) for t in core):
        return False
    if len(core) == 1 and core[0] in _AMBIGUOUS_CORE:
        if not fillers:
            return True
        return any(_token_in_haystack(t, haystack) for t in fillers)
    return True


def query_matches_text(haystack: str, query_text: str) -> bool:
    hay = (haystack or "").lower()
    for clause in tokenize_query_clauses(query_text):
        if clause_matches(hay, clause):
            return True
    return False


def _job_haystack(db: Session, job: Job) -> str:
    parts = [
        job.title_original or "",
        job.description_original or "",
        job.company_original or "",
    ]
    tech_names = db.scalars(
        select(Technology.canonical_name)
        .join(JobSkill, JobSkill.technology_id == Technology.id)
        .where(JobSkill.job_id == job.id)
    ).all()
    parts.extend(tech_names)
    return " ".join(parts).lower()


def backfill_intent_matches(
    db: Session,
    *,
    kind: IntentKind = "all",
    enabled_only: bool = True,
    query_ids: Optional[Sequence[int]] = None,
    limit_jobs: Optional[int] = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Upsert ``job_intent_matches`` for corpus jobs that match intent query tokens."""
    stmt = select(SearchQuery).where(SearchQuery.deleted_at.is_(None))
    if kind in ("focus", "discovery"):
        stmt = stmt.where(SearchQuery.kind == kind)
    if enabled_only:
        stmt = stmt.where(SearchQuery.enabled.is_(True))
    if query_ids:
        stmt = stmt.where(SearchQuery.id.in_(list(query_ids)))
    intents = list(db.scalars(stmt.order_by(SearchQuery.id)).all())

    job_stmt = select(Job).where(Job.is_canonical.is_(True)).order_by(Job.id)
    if limit_jobs is not None:
        job_stmt = job_stmt.limit(limit_jobs)
    jobs = list(db.scalars(job_stmt).all())

    now = datetime.now(timezone.utc)
    created = 0
    refreshed = 0
    per_intent: dict[int, int] = {i.id: 0 for i in intents}

    for job in jobs:
        hay = _job_haystack(db, job)
        for intent in intents:
            if not query_matches_text(hay, intent.query_text or ""):
                continue
            per_intent[intent.id] = per_intent.get(intent.id, 0) + 1
            if dry_run:
                created += 1
                continue

            existed = (
                db.scalar(
                    select(JobIntentMatch.id).where(
                        JobIntentMatch.job_id == job.id,
                        JobIntentMatch.query_id == intent.id,
                    )
                )
                is not None
            )
            upsert_intent_match(db, job_id=job.id, query_id=intent.id, matched_at=now)
            if existed:
                refreshed += 1
            else:
                created += 1

    if not dry_run:
        db.flush()

    return {
        "kind": kind,
        "enabled_only": enabled_only,
        "dry_run": dry_run,
        "intents_considered": len(intents),
        "jobs_scanned": len(jobs),
        "matches_created": created,
        "matches_refreshed": refreshed,
        "per_intent": [
            {
                "query_id": i.id,
                "name": i.name,
                "kind": i.kind,
                "matched_jobs": per_intent.get(i.id, 0),
            }
            for i in intents
        ],
    }
