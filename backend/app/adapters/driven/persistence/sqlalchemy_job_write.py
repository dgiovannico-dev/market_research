"""SQLAlchemy adapter for JobWritePort — wraps existing ingestion modules."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.collectors.base import RawJob
from app.ingestion.service import ingest_raw_jobs as _ingest
from app.ingestion.soft_expire import soft_expire_source_jobs as _soft_expire


class SqlAlchemyJobWriteAdapter:
    def ingest_raw_jobs(
        self,
        db: Session,
        *,
        source_id: int,
        raw_jobs: list[RawJob],
        query_id: Optional[int] = None,
        collection_method: str = "api",
    ) -> dict[str, Any]:
        return _ingest(
            db,
            source_id=source_id,
            raw_jobs=raw_jobs,
            query_id=query_id,
            collection_method=collection_method,
        )

    def soft_expire_source_jobs(
        self,
        db: Session,
        *,
        source_id: int,
        seen_before: datetime,
        dump_complete: bool = False,
    ) -> dict[str, Any]:
        return _soft_expire(
            db,
            source_id=source_id,
            seen_before=seen_before,
            dump_complete=dump_complete,
        )


DEFAULT_JOB_WRITE = SqlAlchemyJobWriteAdapter()
