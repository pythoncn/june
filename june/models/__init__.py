"""
Member:
    only the basic info of a user

    role:
        staff > 6
        admin > 9
        active > 1
        not verified email = 1
        deactive < 1

    reputation:
        reputation means the value of a member, it affects in topic and
        everything

        1. when user's topic is up voted, reputation increase:
            + n1 * log(user.reputation)

        2. when user's topic is down voted, reputation decrease:
            - n2 * log(user.reputation)


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
import hashlib
from random import choice
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, Text
from tornado.options import options
from june.config import db


def get_current_impact():
    return int(time.time())


def create_token(length=16):
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    salt = ''.join([choice(chars) for i in range(length)])
    return salt


class Member(db.Model):
    username = Column(String(100), unique=True, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password = Column(String(100), nullable=False)
    avatar = Column(String(400))
    website = Column(String(400))

    role = Column(Integer, default=2)
    reputation = Column(Integer, default=20, index=True)
    token = Column(String(16))
    created = Column(DateTime, default=datetime.utcnow)
    last_notify = Column(DateTime, default=datetime.utcnow)

    def __init__(self, email, **kwargs):
        self.email = email.lower()
        self.token = create_token(16)
        if 'username' not in kwargs:
            self.username = self.email.split('@')[0].lower()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_avatar(self, size=48):
        if self.avatar:
            return self.avatar
        md5email = hashlib.md5(self.email).hexdigest()
        query = "%s?s=%s%s" % (md5email, size, options.gravatar_extra)
        return options.gravatar_base_url + query

    @staticmethod
    def create_password(raw):
        salt = create_token(8)
        hsh = hashlib.sha1(salt + raw + options.password_secret).hexdigest()
        return "%s$%s" % (salt, hsh)

    def check_password(self, raw):
        if '$' not in self.password:
            return False
        salt, hsh = self.password.split('$')
        verify = hashlib.sha1(salt + raw + options.password_secret).hexdigest()
        return verify == hsh


class MemberLog(db.Model):
    user_id = Column(Integer, nullable=False, index=True)
    message = Column(String(100))
    time = Column(DateTime, default=datetime.utcnow)
    ip = Column(String(100))


class Social(db.Model):
    user_id = Column(Integer, nullable=False, index=True)
    enabled = Column(String(1), default='y')
    service = Column(String(100))  # twitter, douban etc.
    token = Column(Text)  # use json string


class Notify(db.Model):
    sender = Column(Integer, nullable=False)
    receiver = Column(Integer, nullable=False, index=True)
    content = Column(String(400))
    label = Column(String(200))
    link = Column(String(400))
    type = Column(String(20), default='reply')
    created = Column(DateTime, default=datetime.utcnow)


class Node(db.Model):
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
    user_id = Column(Integer, nullable=False, index=True)
    node_id = Column(Integer, nullable=False, index=True)
    created = Column(DateTime, default=datetime.utcnow)


class Topic(db.Model):
    node_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    title = Column(String(200))
    content = Column(Text)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow,
                      onupdate=datetime.utcnow, index=True)
    status = Column(String(40))
    hits = Column(Integer, default=1)
    ups = Column(Text)  # e.g.  1,2,3,4
    downs = Column(Text)
    impact = Column(Integer, default=get_current_impact, index=True)
    reply_count = Column(Integer, default=0)
    last_reply_by = Column(Integer, default=0)
    last_reply_time = Column(DateTime, default=datetime.utcnow, index=True)

    @property
    def up_users(self):
        if not self.ups:
            return []
        return (int(i) for i in self.ups.split(','))

    @property
    def down_users(self):
        if not self.downs:
            return []
        return (int(i) for i in self.downs.split(','))


class Reply(db.Model):
    topic_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    content = Column(String(2000))
    created = Column(DateTime, default=datetime.utcnow)

    accepted = Column(String(1), default='n')  # accepted by topic owner


class Storage(db.Model):
    """A key-value storage"""
    key = Column(String(100), nullable=False, index=True)
    value = Column(Text)
