# coding: utf-8

from flask import Blueprint, request
from flask import render_template, abort, redirect, url_for
from flask.ext.wtf import TextField, SelectField
from flask.ext.wtf.html5 import EmailField
from flask.ext.wtf import DataRequired, Email, Length, Regexp
from flask.ext.babel import lazy_gettext as _
from ..helpers import force_int, require_admin
from ..models import Account
from ..forms import SettingForm


__all__ = ['bp']

bp = Blueprint('admin', __name__)


class UserForm(SettingForm):
    username = TextField(
        _('Username'), validators=[
            DataRequired(), Length(min=3, max=20),
            Regexp(r'^[a-z0-9A-Z]+$')
        ], description=_('English Characters Only.'),
    )
    email = EmailField(
        _('Email'), validators=[DataRequired(), Email()]
    )
    role = SelectField(
        description=_('Role'),
        choices=[
            ('spam', _('Spam')),
            ('user', _('User')),
            ('staff', _('Staff')),
            ('admin', _('Admin'))
        ],
        default='user',
    )


@bp.route('/')
@require_admin
def dashboard():
    """
    The user list page.
    """
    page = force_int(request.args.get('page', 1), 0)
    if not page:
        return abort(404)
    paginator = Account.query.order_by(Account.id.desc()).paginate(page)
    return render_template(
        'admin/dashboard.html',
        paginator=paginator,
    )


@bp.route('/user/<int:uid>', methods=['GET', 'POST'])
@require_admin
def user(uid):
    user = Account.query.get_or_404(uid)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        user.save()
        return redirect(url_for('.user', uid=uid))
    return render_template('admin/user.html', form=form, user=user)
