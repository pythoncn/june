# coding: utf-8

from datetime import datetime
from werkzeug import cached_property
from ._base import db, JuneQuery, SessionMixin

__all__ = ['Topic']


class Topic(db.Model, SessionMixin):
    query_class = JuneQuery

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, nullable=False)

    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text)

    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __str__(self):
        return self.urlname

    def __repr__(self):
        return '<Node: %s>' % self.urlname

    @cached_property
    def html(self):
        #TODO
        return self.body
