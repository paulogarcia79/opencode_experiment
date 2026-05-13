"""add_pending_review_status_and_review_actions

Revision ID: 4e84e12654cc
Revises: a1b2c3d4e5f7
Create Date: 2026-05-12 18:42:28.988051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e84e12654cc'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Add submitted_at column if it doesn't already exist
    columns = [c['name'] for c in inspector.get_columns('articles')]
    if 'submitted_at' not in columns:
        op.add_column('articles', sa.Column('submitted_at', sa.DateTime(), nullable=True))

    # Create review_actions table if it doesn't already exist
    tables = inspector.get_table_names()
    if 'review_actions' not in tables:
        op.create_table('review_actions',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('article_id', sa.Uuid(), nullable=False),
            sa.Column('reviewer_id', sa.Uuid(), nullable=True),
            sa.Column('action', sa.String(), nullable=False),
            sa.Column('feedback', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )
    else:
        # Table already exists (e.g. from SQLModel create_all) — fix FKs
        fks = inspector.get_foreign_keys('review_actions')
        for fk in fks:
            if fk['referred_table'] == 'articles' and 'CASCADE' not in (fk.get('options', {}) or {}).get('ondelete', ''):
                op.drop_constraint(fk['name'], 'review_actions', type_='foreignkey')
                op.create_foreign_key(
                    fk['name'],
                    'review_actions', 'articles',
                    ['article_id'], ['id'],
                    ondelete='CASCADE'
                )
            if fk['referred_table'] == 'users' and (fk.get('options', {}) or {}).get('ondelete') != 'SET NULL':
                op.drop_constraint(fk['name'], 'review_actions', type_='foreignkey')
                op.create_foreign_key(
                    fk['name'],
                    'review_actions', 'users',
                    ['reviewer_id'], ['id'],
                    ondelete='SET NULL'
                )
        # Make reviewer_id nullable if it isn't already
        columns = [c['name'] for c in inspector.get_columns('review_actions')]
        col_info = next((c for c in inspector.get_columns('review_actions') if c['name'] == 'reviewer_id'), None)
        if col_info and col_info['nullable'] is False:
            op.alter_column('review_actions', 'reviewer_id', nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    tables = inspector.get_table_names()
    if 'review_actions' in tables:
        op.drop_table('review_actions')

    columns = [c['name'] for c in inspector.get_columns('articles')]
    if 'submitted_at' in columns:
        op.drop_column('articles', 'submitted_at')
