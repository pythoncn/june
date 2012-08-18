"""
Topic:
    topic must be in a node

    impact:
        for sorting topic

        1. when user reply a topic, impact increase:
            + (n1 + day_del * n2) * log(user.reputation)

        2. when user up vote a topic, impact increase:
            + n3 * log(user.reputation)

        3. when user down vote a topic, impact decrease:
            - n4 * log(user.reputation)

"""

import time
from datetime import datetime
from june.database import db


def get_current_impact():
    return int(time.time())


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, nullable=False, index=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow,
                      onupdate=datetime.utcnow)
    status = db.Column(db.String(40))
    hits = db.Column(db.Integer, default=1)

    up_count = db.Column(db.Integer, default=0)
    down_count = db.Column(db.Integer, default=0)

    #:TODO delete ups, downs
    #ups = db.Column(db.Text)  # e.g.  1,2,3,4
    #downs = db.Column(db.Text)

    reply_count = db.Column(db.Integer, default=0)
    last_reply_by = db.Column(db.Integer, default=0)
    last_reply_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    impact = db.Column(db.Integer, default=get_current_impact, index=True)


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, nullable=False, index=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    content = db.Column(db.String(2000))
    created = db.Column(db.DateTime, default=datetime.utcnow)

    accepted = db.Column(db.String(1), default='n')  # accepted by topic owner


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    topic_id = db.Column(db.Integer, nullable=False, index=True)
    type = db.Column(db.String(10))


class TopicLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, nullable=False, index=True)
    user_id = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
