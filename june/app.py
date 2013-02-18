#!/usr/bin/env python

import os
PROJDIR = os.path.abspath(os.path.dirname(__file__))
ROOTDIR = os.path.split(PROJDIR)[0]
CONFDIR = os.path.join(PROJDIR, '_config')

from flask import Flask
from flask import request, g
from flask.ext.babel import Babel
from flask.ext.principal import Principal, Identity, identity_loaded
from flask.ext.principal import UserNeed, RoleNeed
from .helpers import get_current_user
from .models import db
from .views import front, account, admin


def create_app(config=None):
    app = Flask(
        __name__,
        static_folder='_static',
        template_folder='templates'
    )
    app.config.from_pyfile(os.path.join(CONFDIR, 'base.py'))
    if config and isinstance(config, dict):
        app.config.update(config)
    elif config:
        app.config.from_pyfile(config)

    #: prepare for database
    db.init_app(app)
    db.app = app

    admin.admin.init_app(app)

    #: register blueprints
    app.register_blueprint(account.bp, url_prefix='/account')
    app.register_blueprint(front.bp, url_prefix='')

    @app.before_request
    def load_current_user():
        g.user = get_current_user()

    #: prepare for babel
    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        app.config.setdefault('BABEL_SUPPORTED_LOCALES', ['en', 'zh'])
        app.config.setdefault('BABEL_DEFAULT_LOCALE', 'en')
        match = app.config['BABEL_SUPPORTED_LOCALES']
        default = app.config['BABEL_DEFAULT_LOCALE']
        return request.accept_languages.best_match(match, default)

    princi = Principal(app)

    @princi.identity_loader
    def load_identity():
        return Identity('june')

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        identity.user = g.user
        if not g.user:
            return
        identity.provides.add(UserNeed(g.user.id))
        if g.user.id == 1:
            identity.provides.add(RoleNeed('superuser'))
            identity.provides.add(RoleNeed('admin'))
            identity.provides.add(RoleNeed('staff'))
            identity.provides.add(RoleNeed('member'))

        if g.user.role > 2:
            identity.provides.add(RoleNeed('member'))

        if g.user.role > 10:
            identity.provides.add(RoleNeed('staff'))

        if g.user.role > 20:
            identity.provides.add(RoleNeed('admin'))
    return app
