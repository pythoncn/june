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
from june.config import db


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


class Notify(db.Model):
    sender = Column(Integer, nullable=False)
    receiver = Column(Integer, nullable=False, index=True)
    content = Column(String(400))
    label = Column(String(200))
    link = Column(String(400))
    type = Column(String(20), default='reply')
    created = Column(DateTime, default=datetime.utcnow)


class MemberMixin(object):
    def get_user_by_id(self, id):
        return Member.query.filter_by(id=id).first()

    def get_user_by_name(self, name):
        return Member.query.filter_by(username=name).first()

    def get_users(self, id_list):
        return None
        #return get_cache_list(self, Member, id_list, 'member:')

    def create_user(self, email):
        username = email.split('@')[0].lower()
        username = username.replace('.', '').replace('-', '')
        member = self.get_user_by_name(username)
        if member:
            username = username + create_token(5)
        user = Member(email, username=username)
        return user
