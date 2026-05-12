"""add_author_id_to_articles_and_revisions

Revision ID: a1b2c3d4e5f7
Revises: c1a2b3d4e5f6
Create Date: 2026-05-12 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f7'
down_revision: Union[str, None] = 'c1a2b3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('articles', sa.Column('author_id', sa.Uuid(), nullable=True))
    op.create_foreign_key('fk_articles_author_id_users', 'articles', 'users', ['author_id'], ['id'])

    op.add_column('article_revisions', sa.Column('author_id', sa.Uuid(), nullable=True))
    op.create_foreign_key('fk_article_revisions_author_id_users', 'article_revisions', 'users', ['author_id'], ['id'])

    op.execute("""
        UPDATE articles
        SET author_id = (SELECT id FROM users ORDER BY created_at LIMIT 1)
        WHERE author_id IS NULL
    """)


def downgrade() -> None:
    op.drop_constraint('fk_article_revisions_author_id_users', 'article_revisions', type_='foreignkey')
    op.drop_column('article_revisions', 'author_id')

    op.drop_constraint('fk_articles_author_id_users', 'articles', type_='foreignkey')
    op.drop_column('articles', 'author_id')
