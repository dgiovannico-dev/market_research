"""Add jobs.evidence_tier and jobs.source_snapshot_at

Revision ID: 0007_evidence_tier
Revises: 0006_jobs_canonical_url_unique
Create Date: 2026-10-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_evidence_tier"
down_revision: Union[str, None] = "0006_jobs_canonical_url_unique"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column(
            "evidence_tier",
            sa.String(length=16),
            nullable=False,
            server_default="standard",
        ),
    )
    op.add_column(
        "jobs",
        sa.Column("source_snapshot_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_jobs_evidence_tier", "jobs", ["evidence_tier"])


def downgrade() -> None:
    op.drop_index("ix_jobs_evidence_tier", table_name="jobs")
    op.drop_column("jobs", "source_snapshot_at")
    op.drop_column("jobs", "evidence_tier")
