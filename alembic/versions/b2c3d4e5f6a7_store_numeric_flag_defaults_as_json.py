"""store flag default values as JSON"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Existing values are strings; to_json preserves them as JSON strings.
    op.alter_column("flags", "default_value", existing_type=sa.String(),
                    type_=sa.JSON(), postgresql_using="to_json(default_value)")


def downgrade() -> None:
    op.alter_column("flags", "default_value", existing_type=sa.JSON(),
                    type_=sa.String(), postgresql_using="default_value::text")
