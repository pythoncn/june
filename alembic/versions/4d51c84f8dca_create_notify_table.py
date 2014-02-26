"""create notify table

Revision ID: 4d51c84f8dca
Revises: 4ad568a7a84e
Create Date: 2014-02-26 13:26:20.556780

"""

# revision identifiers, used by Alembic.
revision = '4d51c84f8dca'
down_revision = '4ad568a7a84e'

from datetime import datetime
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'notify',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('account_id', sa.Integer, nullable=False),
        sa.Column('topic_id', sa.Integer, index=True, nullable=False),
        sa.Column('reason', sa.String(100), nullable=False),
        sa.Column('is_viewed', sa.String(100), default=0, nullable=False),
        sa.Column('created', sa.DateTime, default=datetime.utcnow),
    )
    op.add_column('account', sa.Column('notify_count', sa.Integer, default=0))


def downgrade():
    op.drop_table('notify')
    op.drop_column('account', 'notify_count')
