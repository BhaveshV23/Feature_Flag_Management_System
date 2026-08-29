"""create evaluation counts table

Revision ID: a1b2c3d4e5f6
Revises: f2a3b4c5d6e7
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f2a3b4c5d6e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "evaluation_counts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("flag_id", sa.Integer(), nullable=False),
        sa.Column("environment_id", sa.Integer(), nullable=False),
        sa.Column("hour_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("evaluation_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["flag_id"], ["flags.id"]),
        sa.ForeignKeyConstraint(["environment_id"], ["environments.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("flag_id", "environment_id", "hour_start", name="uq_evaluation_count_flag_environment_hour"),
    )
    op.create_index("ix_evaluation_counts_id", "evaluation_counts", ["id"], unique=False)
    op.create_index("ix_evaluation_counts_flag_id", "evaluation_counts", ["flag_id"], unique=False)
    op.create_index("ix_evaluation_counts_environment_id", "evaluation_counts", ["environment_id"], unique=False)
    op.create_index("ix_evaluation_counts_hour_start", "evaluation_counts", ["hour_start"], unique=False)
    op.create_index("ix_evaluation_counts_flag_environment", "evaluation_counts", ["flag_id", "environment_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_evaluation_counts_flag_environment", table_name="evaluation_counts")
    op.drop_index("ix_evaluation_counts_hour_start", table_name="evaluation_counts")
    op.drop_index("ix_evaluation_counts_environment_id", table_name="evaluation_counts")
    op.drop_index("ix_evaluation_counts_flag_id", table_name="evaluation_counts")
    op.drop_index("ix_evaluation_counts_id", table_name="evaluation_counts")
    op.drop_table("evaluation_counts")
