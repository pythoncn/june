"""LikeTopic

Revision ID: 4ad568a7a84e
Revises: 43a5cdca0a62
Create Date: 2013-12-12 12:35:12.253544

"""

# revision identifiers, used by Alembic.
revision = '4ad568a7a84e'
down_revision = '43a5cdca0a62'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'like_topic',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'account_id', 'topic_id', name='uc_account_like_topic'
        )
    )


def downgrade():
    op.drop_table('like_topic')
