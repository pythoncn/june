from flask import Blueprint


app = Blueprint('account', __name__, template_folder='templates')


@app.route('/signin')
def signin():
    return 'signin'


@app.route('/signout')
def signout():
    return 'signout'


@app.route('signup')
def signup():
    return 'signup'
