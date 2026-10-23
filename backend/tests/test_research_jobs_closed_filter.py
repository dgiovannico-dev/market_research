"""Research jobs list excludes closed statuses by default."""

from __future__ import annotations

from unittest.mock import MagicMock

from sqlalchemy.dialects import postgresql

from app.research.jobs_search import search_research_jobs


def _compile(stmt) -> str:
    return str(
        stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": False})
    )


def test_search_research_jobs_include_closed_toggle():
    db = MagicMock()
    db.scalar.return_value = 0
    db.scalars.return_value.unique.return_value.all.return_value = []

    search_research_jobs(db, limit=1, include_closed=False)
    closed_stmt = db.scalars.call_args[0][0]
    sql_closed = _compile(closed_stmt)
    assert "status" in sql_closed.lower()

    db.scalars.reset_mock()
    search_research_jobs(db, limit=1, include_closed=True)
    open_stmt = db.scalars.call_args[0][0]
    sql_open = _compile(open_stmt)
    assert sql_open.count("status") < sql_closed.count("status")
