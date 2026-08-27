"""add targeting rule is_active

Revision ID: f2a3b4c5d6e7
Revises: e1a2b3c4d5e6
Create Date: 2026-08-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2a3b4c5d6e7"
down_revision: Union[str, Sequence[str], None] = "e1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Legacy enabled=false represented an inactive rule. Preserve that behavior
    # while allowing newly-created rules to be active by default.
    op.add_column("targeting_rules", sa.Column("is_active", sa.Boolean(), nullable=True))
    op.execute("UPDATE targeting_rules SET is_active = enabled")
    op.alter_column("targeting_rules", "is_active", existing_type=sa.Boolean(), nullable=False, server_default=sa.true())


def downgrade() -> None:
    op.drop_column("targeting_rules", "is_active")
