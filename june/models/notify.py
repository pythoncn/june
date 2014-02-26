# coding: utf-8

from datetime import datetime
from ._base import db, SessionMixin

__all__ = ['Notify']


class Notify(db.Model, SessionMixin):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, nullable=False)
    topic_id = db.Column(db.Integer, index=True, nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    is_viewed = db.Column(db.String(100), default=0, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __str__(self):
        return self.id

    def __repr__(self):
        return '<Notify: %s>' % self.id
