"""Wave 3: JobWritePort seam — fake port + default adapter wiring."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from unittest.mock import MagicMock

import pytest

from app.application.collection.ingest_batch import ingest_batch, soft_expire_batch
from app.application.collection.run_source import run_source
from app.collectors.base import BaseCollector, CollectorResult, RawJob


class FakeJobWrite:
    def __init__(self) -> None:
        self.ingest_calls: list[dict[str, Any]] = []
        self.expire_calls: list[dict[str, Any]] = []

    def ingest_raw_jobs(
        self,
        db: Any,
        *,
        source_id: int,
        raw_jobs: list[RawJob],
        query_id: Optional[int] = None,
        collection_method: str = "api",
    ) -> dict[str, Any]:
        self.ingest_calls.append(
            {
                "source_id": source_id,
                "n": len(raw_jobs),
                "query_id": query_id,
                "collection_method": collection_method,
            }
        )
        return {"inserted": len(raw_jobs), "updated": 0, "duplicates": 0, "errors": 0}

    def soft_expire_source_jobs(
        self,
        db: Any,
        *,
        source_id: int,
        seen_before: datetime,
        dump_complete: bool = False,
    ) -> dict[str, Any]:
        self.expire_calls.append(
            {
                "source_id": source_id,
                "dump_complete": dump_complete,
                "seen_before": seen_before,
            }
        )
        return {"closed_stale_aged": 0, "dump_complete": dump_complete}


class DumpCollector(BaseCollector):
    name = "Dump"
    source_key = "fake_dump"
    collection_mode = "dump"

    async def collect(self, query: str | None = None) -> CollectorResult:
        return CollectorResult(
            records=[
                RawJob(
                    source_job_id="1",
                    url="https://example.com/1",
                    title="dev",
                )
            ],
            pages_scanned=1,
            dump_complete=True,
            meta={"mode": "test"},
        )


def test_ingest_batch_uses_injected_port():
    fake = FakeJobWrite()
    db = MagicMock()
    raw = [RawJob(source_job_id="a", url="https://x/a", title="t")]
    stats = ingest_batch(
        db,
        source_id=9,
        raw_jobs=raw,
        query_id=3,
        collection_method="api",
        port=fake,
    )
    assert stats["inserted"] == 1
    assert fake.ingest_calls[0]["source_id"] == 9
    assert fake.ingest_calls[0]["query_id"] == 3
    soft_expire_batch(
        db,
        source_id=9,
        seen_before=datetime.now(timezone.utc),
        dump_complete=True,
        port=fake,
    )
    assert fake.expire_calls[0]["dump_complete"] is True


@pytest.mark.asyncio
async def test_run_source_uses_job_write_port():
    fake = FakeJobWrite()
    source = MagicMock()
    source.id = 5
    source.name = "fake_dump"
    source.last_success_at = None
    source.last_error = None
    source.last_error_at = None

    run = MagicMock()
    run.id = 11
    db = MagicMock()

    def _refresh(obj: Any) -> None:
        obj.id = 11

    db.refresh.side_effect = _refresh

    # Capture CollectionRun assignment via side_effect on constructor path:
    # run_source constructs CollectionRun(...) — patch at module.
    from unittest.mock import patch

    def _make_run(**kwargs: Any) -> MagicMock:
        for k, v in kwargs.items():
            setattr(run, k, v)
        return run

    with (
        patch(
            "app.application.collection.run_source.CollectionRun",
            side_effect=_make_run,
        ),
        patch(
            "app.application.collection.run_source.get_collection_mode",
            return_value="dump",
        ),
    ):
        out = await run_source(
            db,
            source=source,
            collector=DumpCollector(),
            collection_method="scheduled_api",
            job_write=fake,
            phase="dump",
        )

    assert out["run_id"] == 11
    assert out["inserted"] == 1
    assert fake.ingest_calls[0]["collection_method"] == "scheduled_api"
    assert fake.expire_calls[0]["dump_complete"] is True
