from sqlalchemy import Column
from sqlalchemy import Integer, String, Text
from july.database import db


class Social(db.Model):
    user_id = Column(Integer, nullable=False, index=True)
    enabled = Column(String(1), default='y')
    service = Column(String(100))  # twitter, douban etc.
    token = Column(Text)  # use json string
