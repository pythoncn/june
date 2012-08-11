import hashlib
from datetime import datetime
from random import choice
from june.database import db


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, index=True)
    email = db.Column(db.String(200), unique=True, nullable=False, index=True)
    password = db.Column(db.String(100), nullable=False)
    #avatar = db.Column(db.String(400))
    website = db.Column(db.String(400))

    role = db.Column(db.Integer, default=1)
    # 0: registered,  1: username
    reputation = db.Column(db.Integer, default=20, index=True)
    token = db.Column(db.String(16))
    created = db.Column(db.DateTime, default=datetime.utcnow)

    city = db.Column(db.String(200))
    edit_username_count = db.Column(db.Integer, default=2)
    description = db.Column(db.Text)

    def __init__(self, email, **kwargs):
        self.email = email.lower()
        self.token = self.create_token(16)

        if 'password' in kwargs:
            raw = kwargs.pop('password')
            self.password = self.create_password(raw)

        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_avatar(self, size=48):
        if self.avatar:
            return self.avatar
        md5email = hashlib.md5(self.email).hexdigest()
        query = "%s?s=%s%s" % (md5email, size, db.app.config['GRAVATAR_EXTRA'])
        return db.app.config['GRAVATAR_BASE_URL'] + query

    @staticmethod
    def create_password(raw):
        salt = Member.create_token(8)
        passwd = '%s%s%s' % (salt, raw, db.app.config['PASSWORD_SECRET'])
        hsh = hashlib.sha1(passwd).hexdigest()
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
        passwd = '%s%s%s' % (salt, raw, db.app.config['PASSWORD_SECRET'])
        verify = hashlib.sha1(passwd).hexdigest()
        return verify == hsh
