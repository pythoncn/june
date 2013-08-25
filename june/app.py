#!/usr/bin/env python

import os
import time
import datetime
import logging
from speaklater import _LazyString
from flask import Flask as _Flask
from flask import request, g
from flask.json import JSONEncoder as _JSONEncoder
from flask_mail import Mail
from .helpers import get_current_user
from .models import db, cache, get_site_status


class JSONEncoder(_JSONEncoder):
    def default(self, o):
        if hasattr(o, '__getitem__') and hasattr(o, 'keys'):
            return dict(o)
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(o, _LazyString):
            return unicode(o)
        return _JSONEncoder.default(self, o)


class Flask(_Flask):
    json_encoder = JSONEncoder


def create_app(config=None):
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder=None,
    )
    app.config.from_pyfile('_settings.py')

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
        if g.user and g.user.is_staff:
            g._before_request_time = time.time()

    @app.after_request
    def rendering_time(response):
        if hasattr(g, '_before_request_time'):
            delta = time.time() - g._before_request_time
            response.headers['X-Render-Time'] = delta

        return response

    Mail(app)
    register_babel(app)
    register_routes(app)
    register_logger(app)
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


def register_jinja(app):
    from .markdown import plain_markdown
    from .htmlcompress import HTMLCompress
    from .views.admin import load_sidebar
    from werkzeug.datastructures import ImmutableDict
    from flask.ext.babel import gettext as _

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


def register_logger(app):
    """Track the logger for production mode."""
    if app.debug:
        return
    handler = logging.StreamHandler()
    handler.setLevel(logging.ERROR)
    app.logger.addHandler(handler)
