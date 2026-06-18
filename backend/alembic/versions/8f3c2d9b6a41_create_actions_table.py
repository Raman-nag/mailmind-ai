"""create actions table

Revision ID: 8f3c2d9b6a41
Revises: 6918c3918d7c
Create Date: 2026-06-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '8f3c2d9b6a41'
down_revision: Union[str, Sequence[str], None] = '6918c3918d7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


action_type = postgresql.ENUM(
    'TASK',
    'DEADLINE',
    'MEETING',
    'FOLLOW_UP',
    'COMMITMENT',
    name='action_type',
    create_type=False
)

action_status = postgresql.ENUM(
    'PENDING',
    'IN_PROGRESS',
    'COMPLETED',
    'DISMISSED',
    name='action_status',
    create_type=False
)

action_priority = postgresql.ENUM(
    'LOW',
    'MEDIUM',
    'HIGH',
    'CRITICAL',
    name='action_priority',
    create_type=False
)


def upgrade() -> None:
    """Upgrade schema."""
    action_type.create(op.get_bind(), checkfirst=True)
    action_status.create(op.get_bind(), checkfirst=True)
    action_priority.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'actions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('email_id', sa.String(), nullable=True),
        sa.Column('action_type', action_type, nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('status', action_status, nullable=False),
        sa.Column('priority', action_priority, nullable=False),
        sa.Column('source_email_subject', sa.String(), nullable=False),
        sa.Column('extraction_confidence', sa.Float(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['email_id'], ['emails.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_actions_action_type'), 'actions', ['action_type'], unique=False)
    op.create_index(op.f('ix_actions_due_date'), 'actions', ['due_date'], unique=False)
    op.create_index(op.f('ix_actions_email_id'), 'actions', ['email_id'], unique=False)
    op.create_index(op.f('ix_actions_priority'), 'actions', ['priority'], unique=False)
    op.create_index(op.f('ix_actions_status'), 'actions', ['status'], unique=False)
    op.create_index(op.f('ix_actions_user_id'), 'actions', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_actions_user_id'), table_name='actions')
    op.drop_index(op.f('ix_actions_status'), table_name='actions')
    op.drop_index(op.f('ix_actions_priority'), table_name='actions')
    op.drop_index(op.f('ix_actions_email_id'), table_name='actions')
    op.drop_index(op.f('ix_actions_due_date'), table_name='actions')
    op.drop_index(op.f('ix_actions_action_type'), table_name='actions')
    op.drop_table('actions')

    action_priority.drop(op.get_bind(), checkfirst=True)
    action_status.drop(op.get_bind(), checkfirst=True)
    action_type.drop(op.get_bind(), checkfirst=True)
