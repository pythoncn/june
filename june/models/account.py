# coding: utf-8

import hashlib
import random
from datetime import datetime
from werkzeug import cached_property, security
from flask.ext.principal import Permission, UserNeed, RoleNeed
from ._base import db, JuneQuery, SessionMixin

__all__ = ['Account']


class Account(db.Model, SessionMixin):
    query_class = JuneQuery

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, index=True,
                         nullable=False)
    email = db.Column(db.String(200), unique=True, index=True)
    password = db.Column(db.String(100))

    screen_name = db.Column(db.String(80))
    description = db.Column(db.String(400))
    city = db.Column(db.String(200))
    website = db.Column(db.String(400))

    # for user: 1 - not verified, 2 - verified, > 20 staff > 40 admin
    role = db.Column(db.Integer, default=1)
    active = db.Column(db.DateTime, default=datetime.utcnow)

    created = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(20))

    def __init__(self, **kwargs):
        self.token = self.create_token(16)

        if 'password' in kwargs:
            raw = kwargs.pop('password')
            self.password = self.create_password(raw)

        if 'username' in kwargs:
            username = kwargs.pop('username')
            self.username = username.lower()

        if 'email' in kwargs:
            email = kwargs.pop('email')
            self.email = email.lower()

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return self.screen_name or self.username

    def __repr__(self):
        return '<Account: %s>' % self.username

    def avatar(self, size=48):
        md5email = hashlib.md5(self.email).hexdigest()
        query = "%s?s=%s%s" % (md5email, size, db.app.config['GRAVATAR_EXTRA'])
        return db.app.config['GRAVATAR_BASE_URL'] + query

    @cached_property
    def permission_write(self):
        return Permission(UserNeed(self.id), RoleNeed('admin'))

    @cached_property
    def permission_admin(self):
        return Permission(RoleNeed('admin'))

    @staticmethod
    def create_password(raw):
        passwd = '%s%s' % (raw, db.app.config['PASSWORD_SECRET'])
        return security.generate_password_hash(passwd)

    @staticmethod
    def create_token(length=16):
        return security.gen_salt(length)

    def check_password(self, raw):
        passwd = '%s%s' % (raw, db.app.config['PASSWORD_SECRET'])
        return security.check_password_hash(self.password, passwd)
