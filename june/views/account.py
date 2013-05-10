# coding: utf-8

from flask import Blueprint
from flask import g, request, flash, current_app
from flask import render_template, redirect, url_for
from flask.ext.babel import gettext as _
from ..models import Account
from ..helpers import login_user, logout_user, require_login
from ..helpers import verify_auth_token
from ..forms import SignupForm, SigninForm, SettingForm
from ..forms import FindForm, ResetForm
from ..tasks import signup_mail, find_mail

__all__ = ['bp']

bp = Blueprint('account', __name__)


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    next_url = request.args.get('next', url_for('.setting'))
    token = request.args.get('token')
    if token:
        user = verify_auth_token(token, 1)
        if not user:
            flash(_('Invalid or expired token.'), 'error')
            return redirect(next_url)
        user.role = 'user'
        user.save()
        login_user(user)
        flash(_('This account is verified.'), 'info')
        return redirect(next_url)

    form = SignupForm()
    if form.validate_on_submit():
        user = form.save()
        login_user(user)
        # send signup mail to user
        msg = signup_mail(user)
        if current_app.debug:
            return msg.html
        flash(_('We have sent you an activate email, check your inbox.'),
              'info')
        return redirect(next_url)
    return render_template('account/signup.html', form=form)


@bp.route('/signin', methods=['GET', 'POST'])
def signin():
    next_url = request.args.get('next', '/')
    if g.user:
        return redirect(next_url)
    form = SigninForm()
    if form.validate_on_submit():
        login_user(form.user, form.permanent.data)
        return redirect(next_url)
    return render_template('account/signin.html', form=form)


@bp.route('/signout')
def signout():
    next_url = request.args.get('next', '/')
    logout_user()
    return redirect(next_url)


@bp.route('/setting', methods=['GET', 'POST'])
@require_login
def setting():
    form = SettingForm(obj=g.user)
    next_url = request.args.get('next', url_for('.setting'))
    if form.validate_on_submit():
        user = Account.query.get(g.user.id)
        form.populate_obj(user)
        user.save()
        return redirect(next_url)
    return render_template('account/setting.html', form=form)


@bp.route('/find', methods=['GET', 'POST'])
def find():
    if g.user:
        return redirect('/')
    form = FindForm()
    if form.validate_on_submit():
        msg = find_mail(form.user)
        if current_app.debug:
            return msg.html
        flash(_('We have sent you an email, check your inbox.'), 'info')
        return redirect(url_for('.find'))
    return render_template('account/find.html', form=form)


@bp.route('/reset', methods=['GET', 'POST'])
def reset():
    if g.user:
        return redirect('/')
    token = request.values.get('token')
    if not token:
        flash(_('Token is missing.'), 'error')
        return redirect('/')
    user = verify_auth_token(token, expires=1)
    if not user:
        flash(_('Invalid or expired token.'), 'error')
        return redirect(url_for('.find'))
    form = ResetForm()
    if form.validate_on_submit():
        user.change_password(form.password.data).save()
        login_user(user)
        flash(_('Your password is updated.'), 'info')
        return redirect(url_for('.setting'))
    return render_template('account/reset.html', form=form, token=token)
