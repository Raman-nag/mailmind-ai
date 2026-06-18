"""add demo tracking and feedback

Revision ID: 2a7f9d4c1b80
Revises: 8f3c2d9b6a41
Create Date: 2026-06-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a7f9d4c1b80'
down_revision: Union[str, Sequence[str], None] = '8f3c2d9b6a41'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('demo_started_at', sa.DateTime(), nullable=True)
    )
    op.add_column(
        'users',
        sa.Column(
            'is_demo_expired',
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False
        )
    )
    op.add_column(
        'users',
        sa.Column(
            'feedback_submitted',
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False
        )
    )

    op.create_table(
        'feedback',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('feedback_text', sa.Text(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_feedback_user_id'),
        'feedback',
        ['user_id'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_feedback_user_id'), table_name='feedback')
    op.drop_table('feedback')
    op.drop_column('users', 'feedback_submitted')
    op.drop_column('users', 'is_demo_expired')
    op.drop_column('users', 'demo_started_at')
