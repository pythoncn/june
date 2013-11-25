# coding: utf-8

import datetime
from flask.ext.sqlalchemy import SQLAlchemy, BaseQuery
from flask.ext.cache import Cache

__all__ = [
    'db', 'cache', 'JuneQuery', 'SessionMixin',
]


class JuneQuery(BaseQuery):
    def filter_in(self, ids, key='id'):
        ids = set(ids)
        if len(ids) == 0:
            return {}
        if len(ids) == 1:
            ident = ids.pop()
            rv = self.get(ident)
            if not rv:
                return {}
            return {ident: rv}
        query = getattr(self, key)
        items = self.filter(query.in_(ids))
        dct = {}
        for item in items:
            dct[getattr(item, key)] = item
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


db = SQLAlchemy()
cache = Cache()
db.Model.query_class = JuneQuery
