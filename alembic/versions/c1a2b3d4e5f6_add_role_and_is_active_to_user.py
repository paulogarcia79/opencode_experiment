"""add_role_and_is_active_to_user

Revision ID: c1a2b3d4e5f6
Revises: bbf20d8f774f
Create Date: 2026-05-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c1a2b3d4e5f6'
down_revision: Union[str, None] = 'bbf20d8f774f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('role', sa.String(), nullable=False, server_default='contributor'))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))

    op.execute("UPDATE users SET role = 'admin' WHERE is_admin = true")
    op.execute("UPDATE users SET role = 'contributor' WHERE is_admin = false")

    op.drop_column('users', 'is_admin')


def downgrade() -> None:
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))

    op.execute("UPDATE users SET is_admin = true WHERE role = 'admin'")
    op.execute("UPDATE users SET is_admin = false WHERE role != 'admin'")

    op.drop_column('users', 'role')
    op.drop_column('users', 'is_active')
