#!/usr/bin/env python

import os
PROJDIR = os.path.abspath(os.path.dirname(__file__))
ROOTDIR = os.path.split(PROJDIR)[0]
CONFDIR = os.path.join(PROJDIR, '_config')

from flask import Flask
from flask import g
from flask import request
from flask import render_template
from flask.ext.babel import Babel
try:
    import june
    print('Start june version: %s' % june.__version__)
except ImportError:
    import site
    site.addsitedir(ROOTDIR)

from june.account.helpers import get_current_user
from june.utils import import_object
from june.database import db

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
    g.user = get_current_user()


#@app.errorhandler(404)
#def not_found(error):
#    return render_template('404.html'), 404


@babel.localeselector
def get_locale():
    app.config.setdefault('BABEL_SUPPORTED_LOCALES', ['en', 'zh'])
    match = app.config['BABEL_SUPPORTED_LOCALES']
    default = app.config['BABEL_DEFAULT_LOCALE']
    return request.accept_languages.best_match(match, default)


def register(blueprint):
    """blueprint structure:

        {{blueprint}}/
            __init__.py
            models.py
            views.py
    """
    #models = import_object('june.%s.models' % blueprint)
    #models.db.init_app(app)
    #models.db.app = app

    views = import_object('june.%s.views' % blueprint)
    app.register_blueprint(views.app, url_prefix='/%s' % blueprint)
    return app


def prepare_app():
    register('account')
    register('node')
    register('topic')

    return app


@app.route('/')
def hello():
    return render_template('index.html')


if __name__ == '__main__':
    app.config.from_pyfile(os.path.join(CONFDIR, 'development.py'))
    prepare_app()
    app.run(host='0.0.0.0')
