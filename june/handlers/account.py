# coding: utf-8

from flask import Blueprint
from flask import g, request, flash, current_app
from flask import render_template, redirect, url_for
from flask.ext.babel import gettext as _
from ..models import Account
from ..forms import SignupForm, SigninForm, SettingForm
from ..forms import FindForm, ResetForm
from ..utils.mail import signup_mail, find_mail
from ..utils.user import login_user, logout_user
from ..utils.user import require_login, verify_auth_token

__all__ = ['bp']

bp = Blueprint('account', __name__)


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Sign up page. If the request has an token arguments, it is not
    for registeration, it is for verifying the token.
    """
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
        flash(_('This account is verified.'), 'success')
        return redirect(next_url)

    form = SignupForm()
    if form.validate_on_submit():
        verify_email = current_app.config.get('VERIFY_EMAIL', True)
        if not verify_email:
            # if no need for verify email
            # we should save the role as user
            user = form.save('user')
            login_user(user)
            return redirect(next_url)
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
    """Sign in page."""
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
    """Sign out, and redirect."""
    next_url = request.args.get('next', '/')
    logout_user()
    return redirect(next_url)


@bp.route('/setting', methods=['GET', 'POST'])
@require_login
def setting():
    """Settings page of current user."""
    user = g.user
    form = SettingForm(obj=user)
    next_url = request.args.get('next', url_for('.setting'))
    if form.validate_on_submit():
        user = Account.query.get(g.user.id)
        form.populate_obj(user)
        user.save()
        flash(_('Your profile is updated.'), 'info')
        return redirect(next_url)
    return render_template('account/setting.html', form=form)


@bp.route('/find', methods=['GET', 'POST'])
def find():
    """Find password page, when user forgot his password, he can
    find the password via email."""
    if g.user:
        return redirect('/')
    form = FindForm()
    if form.validate_on_submit():
        msg = find_mail(form.user)
        if current_app.debug or current_app.testing:
            return msg.html
        flash(_('We have sent you an email, check your inbox.'), 'info')
        return redirect(url_for('.find'))
    return render_template('account/find.html', form=form)


@bp.route('/reset', methods=['GET', 'POST'])
def reset():
    """Reset password page. User launch this page via the link in
    the find password email."""
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


@bp.route('/delete', methods=['GET', 'POST'])
@require_login
def delete():
    """Delete the account. This will not delete the data related to
    the user, such as topics and replies."""
    return 'not ready'


@bp.route('/notification')
@require_login
def notification():
    """Show notifications of a user."""
    # 1. read from cache, these notifications are unreaded
    # 2. read from database, these notifications are readed
    # 3. flush the notifications from cache to database
    return 'not ready'
