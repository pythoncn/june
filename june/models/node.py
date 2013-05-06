# coding: utf-8

from datetime import datetime
from werkzeug import cached_property
from ._base import db, JuneQuery, SessionMixin

__all__ = ['Node', 'NodeStatus']


class Node(db.Model, SessionMixin):
    query_class = JuneQuery

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    urlname = db.Column(db.String(40), unique=True, index=True)

    description = db.Column(db.Text)
    role = db.Column(db.Integer, default=1)

    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __str__(self):
        return self.title

    def __repr__(self):
        return '<Node: %s>' % self.urlname

    @cached_property
    def html(self):
        #TODO
        return self.description


class NodeStatus(db.Model, SessionMixin):
    """
    People's status in a Node
    """

    query_class = JuneQuery

    node_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, primary_key=True)

    updated = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
