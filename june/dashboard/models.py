from sqlalchemy import Column, String, Text, Integer, DateTime
from july.database import db
from datetime import datetime


class Storage(db.Model):
    """A key-value storage"""
    id = Column(Integer, primary_key=True)
    key = Column(String(100), nullable=False, index=True)
    value = Column(Text)

    @classmethod
    def get(cls, key):
        model = cls.query.filter_by(key=key).first()
        if model:
            return model.value
        return None

    @classmethod
    def set(cls, key, value):
        model = cls.query.filter_by(key=key).first()
        if model:
            model.value = value
        else:
            model = cls(key=key, value=value)

        db.session.add(model)
        db.session.commit()
        return value


class Document(db.Model):
    id = Column(Integer, primary_key=True)

    slug = Column(String(200), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)

    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow,
                     onupdate=datetime.utcnow)
