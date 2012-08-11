from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Node(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, index=True, unique=True)
    avatar = db.Column(db.String(400))
    description = db.Column(db.String(1000))
    fgcolor = db.Column(db.String(40))
    bgcolor = db.Column(db.String(40))
    header = db.Column(db.String(2000))
    sidebar = db.Column(db.String(2000))
    footer = db.Column(db.String(2000))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow,
                     onupdate=datetime.utcnow)
    limit_reputation = db.Column(db.Integer, default=0)
    limit_role = db.Column(db.Integer, default=2)
    topic_count = db.Column(db.Integer, default=0)


class FollowNode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    node_id = db.Column(db.Integer, nullable=False, index=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
