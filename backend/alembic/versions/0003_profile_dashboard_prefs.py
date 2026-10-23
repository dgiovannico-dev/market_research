"""user_profiles.dashboard_prefs JSON

Revision ID: 0003_profile_dashboard_prefs
Revises: 0002_source_verification
Create Date: 2026-10-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_profile_dashboard_prefs"
down_revision: Union[str, None] = "0002_source_verification"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_profiles",
        sa.Column("dashboard_prefs", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_profiles", "dashboard_prefs")
