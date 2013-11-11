# coding: utf-8

from datetime import datetime
from werkzeug import cached_property
from ._base import db, SessionMixin
from ..utils.markdown import markdown

__all__ = ['Node', 'NodeStatus']


class Node(db.Model, SessionMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    urlname = db.Column(db.String(40), unique=True, index=True)

    description = db.Column(db.Text)
    topic_count = db.Column(db.Integer, default=0)
    role = db.Column(db.String(10), default=u'user')

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

    @cached_property
    def html(self):
        if self.description is None:
            return ''
        return markdown(self.description)


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
