"""add user cleanup_after_at

Revision ID: 9b1c4e8d2f31
Revises: 2a7f9d4c1b80
Create Date: 2026-06-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b1c4e8d2f31'
down_revision: Union[str, Sequence[str], None] = '2a7f9d4c1b80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('cleanup_after_at', sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'cleanup_after_at')
