"""Country comparison must use the same open-job corpus as DSS analytics."""

from __future__ import annotations

from pathlib import Path

from app.analytics.job_query import CLOSED_JOB_STATUSES
from app.storage.enums import JobStatus


def test_closed_job_statuses_include_stale():
    assert JobStatus.closed_stale.value in CLOSED_JOB_STATUSES
    assert JobStatus.closed.value in CLOSED_JOB_STATUSES
    assert JobStatus.removed_from_source.value in CLOSED_JOB_STATUSES


def test_countries_module_filters_closed_corpus():
    import app.analytics.countries as countries

    src = Path(countries.__file__).read_text(encoding="utf-8")
    assert "CLOSED_JOB_STATUSES" in src
    assert "notin_" in src
