from flask import Blueprint
from flask import render_template
from flask import request, redirect, url_for
from flask import flash
from flask import g
from flask.ext.babel import gettext as _
from .models import Member
from .forms import SignupForm, SettingForm
from .helpers import login, logout

app = Blueprint('account', __name__)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']
        if '@' in account:
            user = Member.query.filter_by(email=account).first()
        else:
            user = Member.query.filter_by(username=account).first()
        user = login(user, password)
        if user:
            return 'ok'
        else:
            return 'error'
    return render_template('account/signin.html')


@app.route('/signout')
def signout():
    next_url = request.args.get('next') or '/'
    flash('You were signed out')
    logout()
    return redirect(next_url)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        form.save()
        return redirect(url_for('.setting'))
    return render_template('account/signup.html', form=form)


@app.route('/setting', methods=['GET', 'POST'])
def setting():
    form = SettingForm(obj=g.user)
    if form.validate_on_submit():
        form.save()
        flash(_('Account has been updated'))
        return redirect(url_for('.setting'))
    return render_template('account/setting.html', form=form)
