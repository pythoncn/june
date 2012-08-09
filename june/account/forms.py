from flask import g
from flask.ext.wtf import Form
from flask.ext.wtf import TextField, PasswordField
from flask.ext.wtf import Required, Email, URL, Optional
from flask.ext.wtf.html5 import EmailField, URLField
from flask.ext.babel import lazy_gettext as _
from .models import db, Member


class SignupForm(Form):
    username = TextField(
        _('Username'), validators=[Required()]
    )
    email = EmailField(
        _('Email'), validators=[Required(), Email()]
    )
    password = PasswordField(
        _('Password'), validators=[Required()]
    )

    def save(self):
        user = Member(
            username=self.username.data,
            email=self.email.data,
            password=self.password.data
        )
        db.session.add(user)
        db.session.commit()
        return user


class SettingForm(Form):
    username = TextField(
        _('Username'), validators=[Required()]
    )
    password = PasswordField(
        _('Password'), validators=[Required()]
    )
    website = URLField(
        _('Website'), validators=[Optional(), URL()]
    )

    def save(self):
        user = g.user
        user.username = self.username.data
        user.website = self.website.data
        db.session.add(user)
        db.session.commit()
        return user
