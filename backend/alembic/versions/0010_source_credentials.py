"""Add source_credentials for encrypted connector secrets

Revision ID: 0010_source_credentials
Revises: 0009_collection_run_summary
Create Date: 2026-10-22
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0010_source_credentials"
down_revision: Union[str, None] = "0009_collection_run_summary"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "source_credentials" in inspector.get_table_names():
        return
    op.create_table(
        "source_credentials",
        sa.Column("connector_key", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("ciphertext", sa.LargeBinary(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "source_credentials" in inspector.get_table_names():
        op.drop_table("source_credentials")
