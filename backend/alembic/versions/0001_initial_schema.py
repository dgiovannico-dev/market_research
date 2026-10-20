"""initial schema via metadata create

Revision ID: 0001
Revises:
Create Date: 2026-10-20
"""

from typing import Sequence, Union

from alembic import op

from app.storage.db import Base
from app.storage import models  # noqa: F401

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
