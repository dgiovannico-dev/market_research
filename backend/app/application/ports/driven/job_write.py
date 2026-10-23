"""Driven port: persist jobs from RawJob batches (write side)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, Protocol

from sqlalchemy.orm import Session

from app.collectors.base import RawJob


class JobWritePort(Protocol):
    """Outbound persistence for ingestion / soft-expire (ADR-008 Wave 3)."""

    def ingest_raw_jobs(
        self,
        db: Session,
        *,
        source_id: int,
        raw_jobs: list[RawJob],
        query_id: Optional[int] = None,
        collection_method: str = "api",
    ) -> dict[str, Any]:
        """Upsert a batch; returns inserted/updated/duplicates/errors counts."""
        ...

    def soft_expire_source_jobs(
        self,
        db: Session,
        *,
        source_id: int,
        seen_before: datetime,
        dump_complete: bool = False,
    ) -> dict[str, Any]:
        """Mark aged / unseen dump jobs closed_stale; returns expire stats."""
        ...
