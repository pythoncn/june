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

"""

import hashlib
from random import choice
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime
from tornado.options import options
from july.database import db


class Member(db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password = Column(String(100), nullable=False)
    avatar = Column(String(400))
    website = Column(String(400))

    role = Column(Integer, default=1)
    # 0: registered,  1: username
    reputation = Column(Integer, default=20, index=True)
    token = Column(String(16))
    created = Column(DateTime, default=datetime.utcnow)
    last_notify = Column(DateTime, default=datetime.utcnow)

    def __init__(self, email, **kwargs):
        self.email = email.lower()
        self.token = self.create_token(16)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_avatar(self, size=48):
        if self.avatar:
            return self.avatar
        md5email = hashlib.md5(self.email).hexdigest()
        query = "%s?s=%s%s" % (md5email, size, options.gravatar_extra)
        return options.gravatar_base_url + query

    def to_json(self):
        data = (
            '{"username":"%s", "avatar":"%s", "website":"%s",'
            '"reputation":%s, "role":%s}'
        ) % (self.username, self.get_avatar(), self.website or "",
             self.reputation, self.role)
        return data

    @staticmethod
    def create_password(raw):
        salt = Member.create_token(8)
        hsh = hashlib.sha1(salt + raw + options.password_secret).hexdigest()
        return "%s$%s" % (salt, hsh)

    @staticmethod
    def create_token(length=16):
        chars = ('0123456789'
                 'abcdefghijklmnopqrstuvwxyz'
                 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        salt = ''.join([choice(chars) for i in range(length)])
        return salt

    def check_password(self, raw):
        if '$' not in self.password:
            return False
        salt, hsh = self.password.split('$')
        verify = hashlib.sha1(salt + raw + options.password_secret).hexdigest()
        return verify == hsh

    @property
    def is_staff(self):
        return self.role > 6

    @property
    def is_admin(self):
        return self.role > 9


class MemberLog(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    message = Column(String(100))
    time = Column(DateTime, default=datetime.utcnow)
    ip = Column(String(100))


class Notification(db.Model):
    id = Column(Integer, primary_key=True)
    sender = Column(Integer, nullable=False)
    receiver = Column(Integer, nullable=False, index=True)

    content = Column(String(400))
    refer = Column(String(600))

    type = Column(String(20), default='reply')
    created = Column(DateTime, default=datetime.utcnow)
