# coding: utf-8

import datetime
from flask.signals import Namespace
from flask.ext.sqlalchemy import SQLAlchemy, BaseQuery

__all__ = [
    'db', 'JuneQuery', 'SessionMixin',
]

signals = Namespace()

db = SQLAlchemy()


class JuneQuery(BaseQuery):
    def filter_in(self, key, ids):
        ids = set(ids)
        if len(ids) == 0:
            return {}
        if len(ids) == 1:
            ident = ids.pop()
            rv = self.get(ident)
            if not rv:
                return {}
            return {ident: rv}
        items = self.filter(key.in_(ids))
        dct = {}
        for u in items:
            dct[u.id] = u
        return dct

    def as_list(self, *columns):
        columns = map(db.defer, columns)
        return self.options(map(db.defer, columns))


class SessionMixin(object):
    def to_dict(self, *columns):
        dct = {}
        for col in columns:
            value = getattr(self, col)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            dct[col] = value
        return dct

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self
