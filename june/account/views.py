from flask import Blueprint
from flask import render_template
from flask import request
from .models import db, Member

app = Blueprint('account', __name__)


@app.route('/signin')
def signin():
    return 'signin'


@app.route('/signout')
def signout():
    return 'signout'


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
