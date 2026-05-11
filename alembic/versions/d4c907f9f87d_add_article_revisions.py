"""add_article_revisions

Revision ID: d4c907f9f87d
Revises: 9effeeb8e6fc
Create Date: 2026-05-11 10:00:07.631634

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'd4c907f9f87d'
down_revision: Union[str, Sequence[str], None] = '9effeeb8e6fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'article_revisions',
        sa.Column('id', sqlmodel.AutoString(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('article_id', sqlmodel.AutoString(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('title', sqlmodel.AutoString(), nullable=False),
        sa.Column('content', sa.JSON(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tag_names', sa.JSON(), nullable=True),
        sa.Column('change_type', sqlmodel.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_article_revisions_article_id', 'article_revisions', ['article_id'])
    op.create_index('ix_article_revisions_article_version', 'article_revisions', ['article_id', 'version_number'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_article_revisions_article_version', table_name='article_revisions')
    op.drop_index('ix_article_revisions_article_id', table_name='article_revisions')
    op.drop_table('article_revisions')
