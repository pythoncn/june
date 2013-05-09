#!/usr/bin/env python

import os
PROJDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFDIR = os.path.join(PROJDIR, 'etc')

import datetime
from flask import Flask
from flask import request, g
from flask.ext.babel import gettext as _
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
    register_filters(app)

    admin.admin.init_app(app)
    register_routes(app)

    if app.debug:
        register_static(app)
    return app


def register_routes(app):
    from .views import front, account, node, topic
    app.register_blueprint(node.bp, url_prefix='/node')
    app.register_blueprint(topic.bp, url_prefix='/topic')
    app.register_blueprint(account.bp, url_prefix='/account')
    app.register_blueprint(front.bp, url_prefix='')
    return app


def register_static(app):
    from flask import send_file

    def _register(name):
        func = lambda: send_file(os.path.join(PROJDIR, 'static', name))
        return app.add_url_rule('/%s' % name, name, view_func=func)

    _register('robots.txt')
    _register('humans.txt')
    return app


def register_filters(app):

    @app.template_filter('timesince')
    def timesince(value):
        now = datetime.datetime.utcnow()
        delta = now - value
        if delta.days > 365:
            return _('%(num)i years ago' % {'num': delta.days / 365})
        if delta.days > 30:
            return _('%(num)i months ago' % {'num': delta.days / 30})
        if delta.days > 0:
            return _('%(num)i days ago' % {'num': delta.days})
        if delta.seconds > 3600:
            return _('%(num)i hours ago' % {'num': delta.seconds / 3600})
        if delta.seconds > 60:
            return _('%(num)i minutes ago' % {'num': delta.seconds / 60})
        return _('just now')

    @app.template_filter('xmldatetime')
    def xmldatetime(value):
        if not isinstance(value, datetime.datetime):
            return value
        return value.strftime('%Y-%m-%dT%H:%M:%SZ')


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
