"""IngestBatch use case — application facade over JobWritePort."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.application.ports.driven.job_write import JobWritePort
from app.collectors.base import RawJob


def _default_job_write() -> JobWritePort:
    """Resolve driven adapter via composition root (not a direct adapters import)."""
    from app.bootstrap import get_container

    return get_container().job_write


def ingest_batch(
    db: Session,
    *,
    source_id: int,
    raw_jobs: list[RawJob],
    query_id: Optional[int] = None,
    collection_method: str = "api",
    port: JobWritePort | None = None,
) -> dict[str, Any]:
    writer = port or _default_job_write()
    return writer.ingest_raw_jobs(
        db,
        source_id=source_id,
        raw_jobs=raw_jobs,
        query_id=query_id,
        collection_method=collection_method,
    )


def soft_expire_batch(
    db: Session,
    *,
    source_id: int,
    seen_before: datetime,
    dump_complete: bool = False,
    port: JobWritePort | None = None,
) -> dict[str, Any]:
    writer = port or _default_job_write()
    return writer.soft_expire_source_jobs(
        db,
        source_id=source_id,
        seen_before=seen_before,
        dump_complete=dump_complete,
    )
