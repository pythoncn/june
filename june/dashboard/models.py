from sqlalchemy import Column
from sqlalchemy import String, Text
from july.database import db


class Storage(db.Model):
    """A key-value storage"""
    key = Column(String(100), nullable=False, index=True)
    value = Column(Text)
