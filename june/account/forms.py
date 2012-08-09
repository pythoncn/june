from flask.ext.wtf import Form
from flask.ext.wtf import TextField, PasswordField
from flask.ext.wtf import Required, Email
from flask.ext.wtf.html5 import EmailField
from flask.ext.babel import lazy_gettext as _


class SignupForm(Form):
    username = TextField(_('Username'), validators=[Required()])
    email = EmailField(_('Email'), validators=[Required(), Email()])
    password = PasswordField(_('Password'), validators=[Required()])
