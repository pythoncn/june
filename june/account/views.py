from flask import Blueprint
from flask import render_template
from flask import request, redirect, url_for
from flask import flash
from flask import g
from flask.ext.babel import gettext as _
from .forms import SigninForm, SignupForm, SettingForm, EditForm
from .models import Member
from .helpers import login, logout
from .decorators import require_login, require_admin

app = Blueprint('account', __name__)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    next_url = request.args.get('next', '/')
    if g.user:
        return redirect(next_url)
    form = SigninForm()
    if form.validate_on_submit():
        login(form.user)
        return redirect(next_url)
    return render_template('account/signin.html', form=form)


@app.route('/signout')
def signout():
    next_url = request.args.get('next', '/')
    logout()
    return redirect(next_url)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = form.save()
        login(user)
        return redirect(url_for('.setting'))
    return render_template('account/signup.html', form=form)


@app.route('/setting', methods=['GET', 'POST'])
@require_login
def setting():
    form = SettingForm(obj=g.user)
    if form.validate_on_submit():
        form.save()
        flash(_('Account has been updated'), 'info')
        return redirect(url_for('.setting'))
    return render_template('account/setting.html', form=form)


@app.route('/edit/<username>', methods=['GET', 'POST'])
@require_admin
def edit(username):
    user = Member.query.filter_by(username=username).first_or_404()
    form = EditForm(obj=user)
    if form.validate_on_submit():
        form.save(user)
        return redirect(url_for('.edit', username=username))
    return render_template('account/edit.html', form=form)
