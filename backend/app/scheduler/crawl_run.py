"""Scheduler-facing alias for the shared RunSource use case (ADR-008)."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.application.collection.run_source import run_source
from app.collectors.base import BaseCollector
from app.storage.models import Source


async def crawl_one(
    db: Session,
    *,
    source: Source,
    collector: BaseCollector,
    query: str | None,
    query_id: int | None,
    phase: str,
) -> dict[str, Any]:
    return await run_source(
        db,
        source=source,
        collector=collector,
        query=query,
        query_id=query_id,
        phase=phase,
        collection_method="scheduled_api",
    )
