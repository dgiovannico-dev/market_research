"""Add collection_runs.summary JSON for collector run metadata

Revision ID: 0009_collection_run_summary
Revises: 0008_analytics_indexes
Create Date: 2026-10-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009_collection_run_summary"
down_revision: Union[str, None] = "0008_analytics_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("collection_runs", sa.Column("summary", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("collection_runs", "summary")
