"""init

Revision ID: f08sa66d495
Revises: None
Create Date: 2013-08-25 21:06:51.286996

"""

# revision identifiers, used by Alembic.
revision = 'f08sa66d495'
down_revision = None

from alembic import op
import sqlalchemy as sa


def create_account():
    op.create_table(
        'account',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(40), unique=True, index=True,
                  nullable=False),
        sa.Column('email', sa.String(200), nullable=False, unique=True,
                  index=True),
        sa.Column('password', sa.String(100), nullable=False),

        sa.Column('screen_name', sa.String(80)),
        sa.Column('description', sa.String(400)),
        sa.Column('city', sa.String(200)),
        sa.Column('website', sa.String(400)),

        sa.Column('role', sa.String(10)),
        sa.Column('active', sa.DateTime, index=True),
        sa.Column('created', sa.DateTime),
        sa.Column('token', sa.String(20)),
    )


def create_node():
    op.create_table(
        'node',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('urlname', sa.String(40), unique=True, index=True),
        sa.Column('description', sa.Text),
        sa.Column('topic_count', sa.Integer),
        sa.Column('role', sa.String(10)),
        sa.Column('created', sa.DateTime),
        sa.Column('updated', sa.DateTime, index=True),
    )


def create_node_status():
    op.create_table(
        'node_status',
        sa.Column('node_id', sa.Integer, primary_key=True),
        sa.Column('account_id', sa.Integer, primary_key=True),
        sa.Column('topic_count', sa.Integer),
        sa.Column('reputation', sa.Integer),
        sa.Column('updated', sa.DateTime),
    )


def create_topic():
    op.create_table(
        'topic',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('account_id', sa.Integer, nullable=False, index=True),
        sa.Column('node_id', sa.Integer, nullable=False, index=True),

        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('content', sa.Text),

        sa.Column('hits', sa.Integer),
        sa.Column('reply_count', sa.Integer),

        sa.Column('created', sa.DateTime),
        sa.Column('updated', sa.DateTime, index=True),
    )


def create_reply():
    op.create_table(
        'reply',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('account_id', sa.Integer, nullable=False),
        sa.Column('topic_id', sa.Integer, index=True, nullable=False),
        sa.Column('content', sa.Text),
        sa.Column('created', sa.DateTime),
        sa.Column('flags', sa.Integer),
    )


def upgrade():
    create_account()
    create_node()
    create_node_status()
    create_topic()
    create_reply()


def downgrade():
    op.drop_table('account')
    op.drop_table('node')
    op.drop_table('node_status')
    op.drop_table('topic')
    op.drop_table('reply')
