"""crawl_one merges CollectorResult.meta into CollectionRun.summary."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from app.collectors.base import BaseCollector, CollectorResult, RawJob
from app.scheduler.crawl_run import crawl_one


@dataclass
class MetaCollector(BaseCollector):
    name: str = "Meta"
    source_key: str = "jobbank_ca"
    collection_mode: str = "dump"
    meta: dict[str, Any] = field(default_factory=dict)

    async def collect(self, query: str | None = None) -> CollectorResult:
        return CollectorResult(
            records=[
                RawJob(
                    source_job_id="1",
                    url="https://example.com/j/1",
                    title="dev",
                )
            ],
            pages_scanned=1,
            meta=dict(self.meta),
        )


@pytest.mark.asyncio
async def test_crawl_one_sets_summary_from_collector_meta():
    source = MagicMock()
    source.id = 42
    source.name = "jobbank_ca"
    source.last_success_at = None
    source.last_error = None
    source.last_error_at = None

    run = SimpleNamespace(
        id=7,
        completed_at=None,
        status="running",
        pages_scanned=0,
        records_received=0,
        records_inserted=0,
        records_updated=0,
        duplicates_detected=0,
        errors_count=0,
        error_summary=None,
        duration_seconds=None,
        summary=None,
    )
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock(side_effect=lambda obj: setattr(obj, "id", 7))
    db.rollback = MagicMock()

    # Replace CollectionRun construction so we capture the run object.
    def _make_run(**kwargs):
        for k, v in kwargs.items():
            setattr(run, k, v)
        return run

    collector = MetaCollector(
        meta={
            "source": "jobbank_ca",
            "ckan": {
                "name": "EN CSV",
                "url": "https://example.com/en.csv",
                "package_id": "pkg-1",
                "last_modified": "2026-09-15T12:00:00",
            },
            "records": 1,
            "mode": "open_data_csv",
        }
    )

    _uc = "app.application.collection.run_source"
    with (
        patch(f"{_uc}.CollectionRun", side_effect=_make_run),
        patch(
            f"{_uc}.ingest_batch",
            return_value={"inserted": 1, "updated": 0, "duplicates": 0, "errors": 0},
        ),
        patch(
            f"{_uc}.soft_expire_batch",
            return_value={
                "closed_stale_aged": 0,
                "closed_stale_unseen": 0,
                "dump_complete": False,
                "stale_after_days": 45,
            },
        ),
        patch(f"{_uc}.get_collection_mode", return_value="dump"),
    ):
        out = await crawl_one(
            db,
            source=source,
            collector=collector,
            query=None,
            query_id=None,
            phase="dump",
        )

    assert out["run_id"] == 7
    assert run.status == "succeeded"
    assert run.summary is not None
    assert run.summary["source"] == "jobbank_ca"
    assert run.summary["mode"] == "open_data_csv"
    assert run.summary["records"] == 1
    assert run.summary["ckan"]["package_id"] == "pkg-1"
    assert run.summary["ckan"]["url"] == "https://example.com/en.csv"
    assert run.summary["inserted"] == 1
    assert run.summary["updated"] == 0
    assert run.summary["duplicates"] == 0
    assert run.summary["errors"] == 0
    assert run.summary["closed_stale_aged"] == 0
    assert run.summary["dump_complete"] is False


@pytest.mark.asyncio
async def test_crawl_one_skips_summary_without_meta():
    source = MagicMock()
    source.id = 1
    source.name = "remotive"
    source.last_success_at = None
    source.last_error = None
    source.last_error_at = None

    run = SimpleNamespace(
        id=3,
        completed_at=None,
        status="running",
        pages_scanned=0,
        records_received=0,
        records_inserted=0,
        records_updated=0,
        duplicates_detected=0,
        errors_count=0,
        error_summary=None,
        duration_seconds=None,
        summary=None,
    )

    def _make_run(**kwargs):
        for k, v in kwargs.items():
            setattr(run, k, v)
        return run

    collector = MetaCollector(source_key="remotive", meta={})

    _uc = "app.application.collection.run_source"
    with (
        patch(f"{_uc}.CollectionRun", side_effect=_make_run),
        patch(
            f"{_uc}.ingest_batch",
            return_value={"inserted": 0, "updated": 0, "duplicates": 0, "errors": 0},
        ),
        patch(
            f"{_uc}.soft_expire_batch",
            return_value={},
        ),
        patch(f"{_uc}.get_collection_mode", return_value="dump"),
    ):
        await crawl_one(
            MagicMock(),
            source=source,
            collector=collector,
            query=None,
            query_id=None,
            phase="dump",
        )

    assert run.summary is None
