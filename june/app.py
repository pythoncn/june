#!/usr/bin/env python

import os
PROJDIR = os.path.abspath(os.path.dirname(__file__))
ROOTDIR = os.path.split(PROJDIR)[0]
CONFDIR = os.path.join(PROJDIR, '_config')

from flask import Flask
from flask import request
from flask.ext.babel import Babel
from .models import db


app = Flask(
    __name__,
    static_folder='_static',
    template_folder='templates'
)
app.config.from_pyfile(os.path.join(CONFDIR, 'base.py'))

#: prepare for database
db.init_app(app)
db.app = app

#: prepare for babel
babel = Babel(app)


@app.before_request
def load_current_user():
    pass


#@app.errorhandler(404)
#def not_found(error):
#    return render_template('404.html'), 404


@babel.localeselector
def get_locale():
    app.config.setdefault('BABEL_SUPPORTED_LOCALES', ['en', 'zh'])
    match = app.config['BABEL_SUPPORTED_LOCALES']
    default = app.config['BABEL_DEFAULT_LOCALE']
    return request.accept_languages.best_match(match, default)
