#!/usr/bin/env python

import os
PROJDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFDIR = os.path.join(PROJDIR, 'etc')

import datetime
from flask import Flask
from flask import request, g
from .helpers import get_current_user
from .models import db
from .views import admin


def create_app(config=None):
    app = Flask(
        __name__,
        static_url_path='/_static',
        static_folder=os.path.join(PROJDIR, 'static'),
        template_folder='templates'
    )
    app.config.from_pyfile(os.path.join(CONFDIR, 'base_config.py'))

    if 'JUNE_SETTINGS' in os.environ:
        app.config.from_envvar('JUNE_SETTINGS')

    if isinstance(config, dict):
        app.config.update(config)
    else:
        app.config.from_pyfile(config)

    app.config.update({'SITE_TIME': datetime.datetime.utcnow()})

    #: prepare for database
    db.init_app(app)
    db.app = app

    @app.before_request
    def load_current_user():
        g.user = get_current_user()

    init_babel(app)

    admin.admin.init_app(app)
    register_routes(app)
    return app


def register_routes(app):
    from .views import front, account, node
    app.register_blueprint(node.bp, url_prefix='/node')
    app.register_blueprint(account.bp, url_prefix='/account')
    app.register_blueprint(front.bp, url_prefix='')
    return app


def init_babel(app):
    from flask.ext.babel import Babel

    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        app.config.setdefault('BABEL_SUPPORTED_LOCALES', ['en', 'zh'])
        app.config.setdefault('BABEL_DEFAULT_LOCALE', 'en')
        match = app.config['BABEL_SUPPORTED_LOCALES']
        default = app.config['BABEL_DEFAULT_LOCALE']
        return request.accept_languages.best_match(match, default)
