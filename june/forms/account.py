# coding: utf-8

from flask import current_app
from wtforms import TextField, PasswordField, BooleanField
from wtforms import TextAreaField
from wtforms.fields.html5 import EmailField, URLField
from wtforms.validators import DataRequired, Email, Length, Regexp
from wtforms.validators import Optional, URL
from flask_babel import lazy_gettext as _

from ._base import BaseForm
from ..models import Account


__all__ = [
    'SignupForm', 'SigninForm', 'SettingForm',
    'FindForm', 'ResetForm',
]


RESERVED_WORDS = [
    'root', 'admin', 'bot', 'robot', 'master', 'webmaster',
    'account', 'people', 'user', 'users', 'project', 'projects',
    'search', 'action', 'favorite', 'like', 'love', 'none',
    'team', 'teams', 'group', 'groups', 'organization',
    'organizations', 'package', 'packages', 'org', 'com', 'net',
    'help', 'doc', 'docs', 'document', 'documentation', 'blog',
    'bbs', 'forum', 'forums', 'static', 'assets', 'repository',

    'public', 'private',
    'mac', 'windows', 'ios', 'lab',
]


class SignupForm(BaseForm):
    username = TextField(
        _('Username'), validators=[
            DataRequired(), Length(min=3, max=20),
            Regexp(r'^[a-z0-9A-Z]+$')
        ], description=_('English Characters Only.'),
    )
    email = EmailField(
        _('Email'), validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        _('Password'), validators=[DataRequired()]
    )

    def validate_username(self, field):
        data = field.data.lower()
        if data in RESERVED_WORDS:
            raise ValueError(_('This name is a reserved name.'))
        if data in current_app.config.get('RESERVED_WORDS', []):
            raise ValueError(_('This name is a reserved name.'))
        if Account.query.filter_by(username=data).count():
            raise ValueError(_('This name has been registered.'))

    def validate_email(self, field):
        if Account.query.filter_by(email=field.data.lower()).count():
            raise ValueError(_('This email has been registered.'))

    def save(self, role=None):
        user = Account(**self.data)
        if role:
            user.role = role
        user.save()
        return user


class SigninForm(BaseForm):
    account = TextField(
        _('Account'),
        validators=[DataRequired(), Length(min=3, max=200)],
        description=_('Username or Email')
    )
    password = PasswordField(
        _('Password'), validators=[DataRequired()]
    )
    permanent = BooleanField(_('Remember me for a month.'))

    def validate_password(self, field):
        account = self.account.data
        if '@' in account:
            user = Account.query.filter_by(email=account).first()
        else:
            user = Account.query.filter_by(username=account).first()

        if not user:
            raise ValueError(_('Wrong account or password'))
        if user.check_password(field.data):
            self.user = user
            return user
        raise ValueError(_('Wrong account or password'))


class SettingForm(BaseForm):
    screen_name = TextField(_('Display Name'), validators=[Length(max=80)])
    website = URLField(_('Website'), validators=[URL(), Optional()])
    city = TextField(_('City'), description=_('Where are you living'))
    description = TextAreaField(
        _('Description'), validators=[Optional(), Length(max=400)],
        description=_('Markdown is supported.')
    )
    title = TextField(_('Job Title'))


class FindForm(BaseForm):
    account = TextField(
        _('Account'), validators=[DataRequired()],
        description=_('Username or Email')
    )

    def validate_account(self, field):
        account = field.data
        if '@' in account:
            user = Account.query.filter_by(email=account).first()
        else:
            user = Account.query.filter_by(username=account).first()
        if not user:
            raise ValueError(_('This account does not exist.'))
        self.user = user


class ResetForm(BaseForm):
    password = PasswordField(
        _('Password'), validators=[DataRequired()],
        description=_('Remember your password')
    )
    confirm = PasswordField(
        _('Confirm'), validators=[DataRequired()],
        description=_('Confirm your password')
    )

    def validate_confirm(self, field):
        if field.data != self.password.data:
            raise ValueError(_("Passwords don't match."))
