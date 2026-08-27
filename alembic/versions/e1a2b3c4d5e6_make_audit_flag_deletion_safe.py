"""make audit flag deletion safe

Revision ID: e1a2b3c4d5e6
Revises: 7c1d2e4f8a90
Create Date: 2026-08-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "7c1d2e4f8a90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("audit_logs_flag_id_fkey", "audit_logs", type_="foreignkey")
    op.alter_column("audit_logs", "flag_id", existing_type=sa.Integer(), nullable=True)
    op.create_foreign_key("audit_logs_flag_id_fkey", "audit_logs", "flags", ["flag_id"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    op.drop_constraint("audit_logs_flag_id_fkey", "audit_logs", type_="foreignkey")
    op.alter_column("audit_logs", "flag_id", existing_type=sa.Integer(), nullable=False)
    op.create_foreign_key("audit_logs_flag_id_fkey", "audit_logs", "flags", ["flag_id"], ["id"])
