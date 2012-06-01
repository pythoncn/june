import time
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, Text
from july.database import db

class Feedback(db.Model):
    id = Column(Integer, primary_key=True)
    sender = Column(Integer, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow,
                      onupdate=datetime.utcnow)

    # TODO/FIXME:
    # Actually I'm very tempted to change the 'readed' column in
    # Notification to 'unread' as well. However I will wait until we
    # have DB migration. :-)
    unread = Column(String(1), default='y')
