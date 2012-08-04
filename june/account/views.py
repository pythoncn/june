from flask import Blueprint
from flask import render_template
from flask import request, redirect
from flask import flash
from .models import db, Member
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
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = Member(email=email, username=username, password=password)
        db.session.add(user)
        db.session.commit()
    return render_template('account/signup.html')
