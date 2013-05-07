# coding: utf-8

from datetime import datetime
from werkzeug import cached_property
from ._base import db, JuneQuery, SessionMixin

__all__ = ['Topic', 'Reply']


class Topic(db.Model, SessionMixin):
    query_class = JuneQuery

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, nullable=False, index=True)

    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)

    hits = db.Column(db.Integer, default=0)

    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __str__(self):
        return self.title

    def __repr__(self):
        return '<Topic: %s>' % self.id

    @cached_property
    def html(self):
        #TODO
        return self.content


class Reply(db.Model, SessionMixin):
    query_class = JuneQuery

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, nullable=False)
    topic_id = db.Column(db.Integer, index=True)
    content = db.Column(db.Text)

    created = db.Column(db.DateTime, default=datetime.utcnow)
    # attitude: like, hate
    attitude = db.Column(db.String(10))
    flags = db.Column(db.Integer, default=0)

    def __str__(self):
        return self.content

    @cached_property
    def html(self):
        #TODO
        return self.content
