"""certifications + job_certifications

Revision ID: 0011_certifications
Revises: 0010_source_credentials
Create Date: 2026-10-24
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011_certifications"
down_revision: Union[str, None] = "0010_source_credentials"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "certifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=256), nullable=False),
        sa.Column("aliases", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("slug", name="uq_cert_slug"),
    )
    op.create_table(
        "job_certifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column(
            "certification_id",
            sa.Integer(),
            sa.ForeignKey("certifications.id"),
            nullable=False,
        ),
        sa.Column("importance", sa.String(length=32), server_default="mentioned"),
        sa.Column("extraction_method", sa.String(length=32), server_default="rules"),
        sa.Column("evidence_span", sa.Text(), nullable=True),
        sa.UniqueConstraint(
            "job_id",
            "certification_id",
            "importance",
            name="uq_job_cert",
        ),
    )
    op.create_index("ix_job_certifications_job_id", "job_certifications", ["job_id"])
    op.create_index(
        "ix_job_certifications_certification_id",
        "job_certifications",
        ["certification_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_job_certifications_certification_id", table_name="job_certifications")
    op.drop_index("ix_job_certifications_job_id", table_name="job_certifications")
    op.drop_table("job_certifications")
    op.drop_table("certifications")
