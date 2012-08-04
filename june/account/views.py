from flask import Blueprint
from flask import render_template
from flask import request
from .models import db, Member
from .helpers import login, logout, get_current_user

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
    logout()
    return render_template('index.html')


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

@app.route('/setting', methods=['GET', 'POST'])
def setting():
    if request.method == 'POST':
        username = request.form['username']
        website = request.form['website']
        city = request.form['city']
        description = request.form['description']
        user = get_current_user()
        if user:
            user.username = username
            user.website = website
            user.city = city
            user.description = description
            db.session.commit()
    user = get_current_user()
    if user: 
        username = user.username
        website = user.website
        city = user.city
        description = user.description
    return render_template('account/setting.html', username = username, website = website, city = city, description = description)
