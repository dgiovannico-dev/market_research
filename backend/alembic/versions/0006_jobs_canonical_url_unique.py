"""Partial unique index: one canonical job per canonical_url

Revision ID: 0006_jobs_canonical_url_unique
Revises: 0005_crawler_ticks
Create Date: 2026-10-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_jobs_canonical_url_unique"
down_revision: Union[str, None] = "0005_crawler_ticks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

INDEX_NAME = "uq_jobs_canonical_url_when_canonical"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {idx["name"] for idx in inspector.get_indexes("jobs")}
    if INDEX_NAME not in existing:
        op.create_index(
            INDEX_NAME,
            "jobs",
            ["canonical_url"],
            unique=True,
            postgresql_where=sa.text("is_canonical IS TRUE"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {idx["name"] for idx in inspector.get_indexes("jobs")}
    if INDEX_NAME in existing:
        op.drop_index(INDEX_NAME, table_name="jobs")
