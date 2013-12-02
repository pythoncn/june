# coding: utf-8

import hashlib
from datetime import datetime
from werkzeug import security
from ._base import db, SessionMixin

__all__ = ('Account', 'NonAccount')


class Account(db.Model, SessionMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, index=True,
                         nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True, index=True)
    password = db.Column(db.String(100), nullable=False)

    screen_name = db.Column(db.String(80))
    description = db.Column(db.String(400))
    city = db.Column(db.String(200))
    website = db.Column(db.String(400))

    role = db.Column(db.String(10), default='new')
    active = db.Column(db.DateTime, default=datetime.utcnow, index=True)

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

    @staticmethod
    def create_password(raw):
        passwd = '%s%s' % (raw, db.app.config['PASSWORD_SECRET'])
        return security.generate_password_hash(passwd)

    @staticmethod
    def create_token(length=16):
        return security.gen_salt(length)

    @property
    def is_staff(self):
        if self.id == 1:
            return True
        return self.role == 'staff' or self.role == 'admin'

    @property
    def is_admin(self):
        return self.id == 1 or self.role == 'admin'

    def check_password(self, raw):
        passwd = '%s%s' % (raw, db.app.config['PASSWORD_SECRET'])
        return security.check_password_hash(self.password, passwd)

    def change_password(self, raw):
        self.password = self.create_password(raw)
        self.token = self.create_token()
        return self


class NonAccount(object):
    """Non Account is a model designed for the deleted account.
    Since the account is deleted, the topics and replies will has no
    account related to them, in such cases, a `NonAccount` is used."""

    username = 'none'
    is_staff = False
    is_admin = False

    def __str__(self):
        return 'none'

    def __repr__(self):
        return '<NonAccount: none>'
