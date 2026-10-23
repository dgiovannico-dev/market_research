"""Distinct facet values for Jobs explorer filters."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import distinct, select
from sqlalchemy.orm import Session

from app.research.jobs_search import apply_research_job_scope
from app.storage.models import Job, Source


def research_job_facets(
    db: Session,
    *,
    query_id: Optional[int] = None,
    lens: Optional[str] = None,
) -> dict[str, Any]:
    """Return distinct countries, sources, contracts, remotes for canonical jobs."""
    scoped = select(Job.id).where(Job.is_canonical.is_(True))
    scoped = apply_research_job_scope(db, scoped, query_id=query_id, lens=lens)

    countries = list(
        db.scalars(
            select(distinct(Job.country_code))
            .where(
                Job.id.in_(scoped),
                Job.country_code.is_not(None),
                Job.country_code != "",
            )
            .order_by(Job.country_code)
        ).all()
    )

    contracts = list(
        db.scalars(
            select(distinct(Job.contract_type))
            .where(
                Job.id.in_(scoped),
                Job.contract_type.is_not(None),
                Job.contract_type != "",
            )
            .order_by(Job.contract_type)
        ).all()
    )

    remotes = list(
        db.scalars(
            select(distinct(Job.remote_type))
            .where(
                Job.id.in_(scoped),
                Job.remote_type.is_not(None),
                Job.remote_type != "",
            )
            .order_by(Job.remote_type)
        ).all()
    )

    source_rows = db.execute(
        select(Source.id, Source.name)
        .join(Job, Job.source_id == Source.id)
        .where(Job.id.in_(scoped))
        .distinct()
        .order_by(Source.name)
    ).all()
    sources = [{"id": sid, "name": name} for sid, name in source_rows if name]

    return {
        "lens": lens,
        "query_id": query_id,
        "countries": countries,
        "sources": sources,
        "contracts": contracts,
        "remotes": remotes,
    }
