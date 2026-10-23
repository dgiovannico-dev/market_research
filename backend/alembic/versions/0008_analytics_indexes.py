"""Analytics composite indexes for DSS job_query / skills / ops

Revision ID: 0008_analytics_indexes
Revises: 0007_evidence_tier
Create Date: 2026-10-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008_analytics_indexes"
down_revision: Union[str, None] = "0007_evidence_tier"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

INDEXES: list[tuple[str, str, list[str], dict]] = [
    ("ix_jobs_canonical_published", "jobs", ["is_canonical", "published_at"], {}),
    (
        "ix_jobs_canonical_country_published",
        "jobs",
        ["is_canonical", "country_code", "published_at"],
        {},
    ),
    ("ix_job_skills_job_id", "job_skills", ["job_id"], {}),
    ("ix_job_skills_technology_job", "job_skills", ["technology_id", "job_id"], {}),
    ("ix_job_rates_job_id", "job_rates", ["job_id"], {}),
    (
        "ix_search_queries_kind_enabled_alive",
        "search_queries",
        ["kind", "enabled"],
        {"postgresql_where": sa.text("deleted_at IS NULL")},
    ),
    ("ix_collection_runs_source_started", "collection_runs", ["source_id", "started_at"], {}),
]


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for name, table, cols, kwargs in INDEXES:
        existing = {idx["name"] for idx in inspector.get_indexes(table)}
        if name in existing:
            continue
        op.create_index(name, table, cols, **kwargs)
        # Refresh inspector cache for next table read in same migration.
        inspector = sa.inspect(bind)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for name, table, _cols, _kwargs in reversed(INDEXES):
        existing = {idx["name"] for idx in inspector.get_indexes(table)}
        if name in existing:
            op.drop_index(name, table_name=table)
        inspector = sa.inspect(bind)
