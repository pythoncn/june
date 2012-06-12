from datetime import datetime
from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime
from july.database import db


class Node(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False, index=True)
    avatar = Column(String(400))
    description = Column(String(1000))
    fgcolor = Column(String(40))
    bgcolor = Column(String(40))
    header = Column(String(2000))
    sidebar = Column(String(2000))
    footer = Column(String(2000))
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow,
                     onupdate=datetime.utcnow)
    limit_reputation = Column(Integer, default=0)
    limit_role = Column(Integer, default=2)
    topic_count = Column(Integer, default=0)


class FollowNode(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    node_id = Column(Integer, nullable=False, index=True)
    created = Column(DateTime, default=datetime.utcnow)
