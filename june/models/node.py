# coding: utf-8

from datetime import datetime
from ._base import db, SessionMixin

__all__ = ['Node', 'NodeStatus']


class Node(db.Model, SessionMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    urlname = db.Column(db.String(40), unique=True, index=True)

    description = db.Column(db.Text)
    topic_count = db.Column(db.Integer, default=0)
    role = db.Column(db.String(10), default=u'user')

    # topics will show on homepage ?
    on_home = db.Column(db.Boolean, default=True)
    # a mayor can delete a topic in this node, can change description
    mayor = db.Column(db.Integer, default=0)

    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        index=True,
    )

    def __str__(self):
        return self.title

    def __repr__(self):
        return '<Node: %s>' % self.urlname


class NodeStatus(db.Model, SessionMixin):
    """
    People's status in a Node
    """
    node_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, primary_key=True)

    topic_count = db.Column(db.Integer, default=0)
    reputation = db.Column(db.Integer, default=0)

    updated = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
