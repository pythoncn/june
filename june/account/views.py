from flask import Blueprint
from flask import render_template
app = Blueprint('account', __name__)


@app.route('/signin')
def signin():
    return 'signin'


@app.route('/signout')
def signout():
    return 'signout'


@app.route('signup', methods=['GET', 'POST'])
def signup():
    return render_template('account/signup.html')
