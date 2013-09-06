"""add profile

Revision ID: 3b4e4bcf4a8d
Revises: f08sa66d495
Create Date: 2013-08-25 22:02:24.770275

"""

# revision identifiers, used by Alembic.
revision = '3b4e4bcf4a8d'
down_revision = 'f08sa66d495'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'profile',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('company', sa.String(120)),
    )


def downgrade():
    op.drop_table('profile')
