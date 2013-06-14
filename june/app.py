#!/usr/bin/env python

import os
PROJDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFDIR = os.path.join(PROJDIR, 'etc')

import datetime
import logging
from flask import Flask
from flask import request, g
from flask.ext.babel import gettext as _
from .helpers import get_current_user
from .models import db, cache, get_site_status


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
    elif config:
        app.config.from_pyfile(config)

    app.config.update({'SITE_TIME': datetime.datetime.utcnow()})
    register_jinja(app)

    #: prepare for database
    db.init_app(app)
    db.app = app

    #: prepare for cache
    cache.init_app(app)

    @app.before_request
    def load_current_user():
        g.user = get_current_user()

    register_babel(app)
    register_routes(app)
    register_storage(app)
    register_logger(app)

    if app.debug:
        register_static(app)
    return app


def register_routes(app):
    from .views import front, account, node, topic, user, admin
    app.register_blueprint(account.bp, url_prefix='/account')
    app.register_blueprint(node.bp, url_prefix='/node')
    app.register_blueprint(topic.bp, url_prefix='/topic')
    app.register_blueprint(user.bp, url_prefix='/user')
    app.register_blueprint(admin.bp, url_prefix='/admin')
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


def register_jinja(app):
    from .markdown import plain_markdown
    from .htmlcompress import HTMLCompress
    from .views.admin import load_sidebar
    from werkzeug.datastructures import ImmutableDict

    app.jinja_options = ImmutableDict(
        extensions=[
            'jinja2.ext.autoescape', 'jinja2.ext.with_', HTMLCompress
        ]
    )

    app.jinja_env.filters['markdown'] = plain_markdown

    @app.context_processor
    def register_context():
        return dict(
            get_site_status=get_site_status,
            get_site_sidebar=load_sidebar,
        )

    @app.template_filter('timesince')
    def timesince(value):
        now = datetime.datetime.utcnow()
        delta = now - value
        if delta.days > 365:
            return _('%(num)i years ago', num=delta.days / 365)
        if delta.days > 30:
            return _('%(num)i months ago', num=delta.days / 30)
        if delta.days > 0:
            return _('%(num)i days ago', num=delta.days)
        if delta.seconds > 3600:
            return _('%(num)i hours ago', num=delta.seconds / 3600)
        if delta.seconds > 60:
            return _('%(num)i minutes ago', num=delta.seconds / 60)
        return _('just now')

    @app.template_filter('xmldatetime')
    def xmldatetime(value):
        if not isinstance(value, datetime.datetime):
            return value
        return value.strftime('%Y-%m-%dT%H:%M:%SZ')


def register_babel(app):
    from flask.ext.babel import Babel

    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        app.config.setdefault('BABEL_SUPPORTED_LOCALES', ['en', 'zh'])
        app.config.setdefault('BABEL_DEFAULT_LOCALE', 'en')
        match = app.config['BABEL_SUPPORTED_LOCALES']
        default = app.config['BABEL_DEFAULT_LOCALE']
        return request.accept_languages.best_match(match, default)


def register_storage(app):
    from flask.ext.storage import Storage

    type = app.config.get('STORAGE_TYPE')
    s = Storage(app)
    backend = s.create_backend(type, 'june', None, app.config)
    app.storage = backend

    # for debug
    if app.debug and type == 'local':
        from flask import send_from_directory
        url_path = app.config.get('STORAGE_LOCAL_URL')
        root = app.config.get('STORAGE_LOCAL_ROOT')
        app.add_url_rule(
            url_path + '/<path:filename>',
            endpoint='image',
            view_func=lambda filename: send_from_directory(root, filename)
        )
    return app


def register_logger(app):
    """Track the logger for production mode."""
    if app.debug:
        return
    handler = logging.StreamHandler()
    handler.setLevel(logging.ERROR)
    app.logger.addHandler(handler)
