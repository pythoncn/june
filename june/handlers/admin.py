# coding: utf-8

import os
from flask import Blueprint, request, current_app, flash
from flask import render_template, abort, redirect, url_for
from wtforms import TextField, SelectField
from flask.ext.wtf.html5 import EmailField
from wtforms.validators import DataRequired, Email, Length, Regexp

from flask.ext.babel import lazy_gettext as _
from ..helpers import force_int
from ..models import Account
from ..forms import SettingForm
from ..utils.user import require_staff, require_admin


__all__ = ['bp', 'load_sidebar']

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
        _('Role'),
        choices=[
            ('spam', _('Spam')),
            ('user', _('User')),
            ('staff', _('Staff')),
            ('admin', _('Admin'))
        ],
        default='user',
    )


@bp.route('/', methods=['GET', 'POST'])
@require_staff
def dashboard():
    """
    The dashboard page of admin site.
    """
    if request.method == 'POST':
        save_sidebar(request.form.get('content', None))
        return redirect(url_for('.dashboard'))

    page = force_int(request.args.get('page', 1), 0)
    if not page:
        return abort(404)

    sidebar = load_sidebar()
    paginator = Account.query.order_by(Account.id.desc()).paginate(page)
    return render_template(
        'admin/dashboard.html',
        paginator=paginator,
        sidebar=sidebar,
    )


@bp.route('/user/<int:uid>', methods=['GET', 'POST'])
@require_admin
def user(uid):
    """
    Edit a specified user.
    """
    user = Account.query.get_or_404(uid)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        user.save()
        return redirect(url_for('.user', uid=uid))
    return render_template('admin/user.html', form=form, user=user)


def load_sidebar():
    filepath = current_app.config.get('SITE_SIDEBAR')
    if not filepath:
        return None
    if not os.path.exists(filepath):
        return ''
    with open(filepath) as f:
        content = f.read()
        return content.decode('utf-8')


def save_sidebar(content):
    filepath = current_app.config.get('SITE_SIDEBAR')
    if not filepath:
        flash('Config your site with SITE_SIDEBAR', 'warn')
        return

    dirname = os.path.dirname(filepath)
    if not os.path.exists(dirname):
        os.makdirs(dirname)

    with open(filepath, 'wb') as f:
        content = content.encode('utf-8')
        f.write(content)
