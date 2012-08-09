#!/usr/bin/env python

import os
CONF = os.path.join(os.path.abspath(os.path.dirname(__file__)), '_config')

from flask import Flask
from flask import g
from flask import request
from flask import render_template
from flask.ext.babel import Babel
from account.helpers import get_current_user
from utils import import_object

app = Flask(
    __name__,
    static_folder='_static',
    template_folder='templates'
)
app.config.from_pyfile(os.path.join(CONF, 'base.py'))
babel = Babel(app)


@app.before_request
def load_current_user():
    g.user = get_current_user()


#@app.errorhandler(404)
#def not_found(error):
#    return render_template('404.html'), 404


@babel.localeselector
def get_locale():
    #return request.accept_languages.best_match(['en', 'zh'])
    return 'zh'


def register(blueprint):
    """blueprint structure:

        {{blueprint}}/
            __init__.py
            models.py
            views.py
    """
    if __name__ == '__main__':
        prefix = blueprint
    else:
        prefix = 'june.%s' % blueprint
    models = import_object('%s.models' % prefix)
    models.db.init_app(app)
    models.db.app = app
    views = import_object('%s.views' % prefix)
    app.register_blueprint(views.app, url_prefix='/%s' % blueprint)
    return app


def prepare_app():
    #: int account blueprint
    register('account')
    register('node')

    #: init topic blueprint
    return app


@app.route('/')
def hello():
    return render_template('index.html')


if __name__ == '__main__':
    app.config.from_pyfile(os.path.join(CONF, 'development.py'))
    prepare_app()
    app.run()
