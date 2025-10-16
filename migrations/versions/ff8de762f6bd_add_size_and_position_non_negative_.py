"""add size and position non-negative check constraint

Revision ID: ff8de762f6bd
Revises: 9e74d5b851a1
Create Date: 2025-10-15 22:55:03.343133

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff8de762f6bd'
down_revision: Union[str, Sequence[str], None] = '9e74d5b851a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "check_size_x_non_negative",
        "probes",
        "size_x >= 0"
    )
    op.create_check_constraint(
        "check_size_y_non_negative",
        "probes",
        "size_y >= 0"
    )
    op.create_check_constraint(
        "check_x_non_negative",
        "probes",
        "x >= 0"
    )
    op.create_check_constraint(
        "check_y_non_negative",
        "probes",
        "y >= 0"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("check_size_x_non_negative", "probes", type_="check")
    op.drop_constraint("check_size_y_non_negative", "probes", type_="check")
    op.drop_constraint("check_x_non_negative", "probes", type_="check")
    op.drop_constraint("check_y_non_negative", "probes", type_="check")
