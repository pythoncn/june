#!/usr/bin/env python

import os
import time
import datetime
import logging
import hashlib
from flask import request, g
from flask_mail import Mail
from ._flask import Flask
from .models import db, cache, get_site_status


def create_app(config=None):
    app = Flask(
        __name__,
        template_folder='templates',
    )
    app.config.from_pyfile('_settings.py')

    if 'JUNE_SETTINGS' in os.environ:
        app.config.from_envvar('JUNE_SETTINGS')

    if isinstance(config, dict):
        app.config.update(config)
    elif config:
        app.config.from_pyfile(os.path.abspath(config))

    app.static_folder = app.config.get('STATIC_FOLDER')
    app.config.update({'SITE_TIME': datetime.datetime.utcnow()})

    register_hooks(app)
    register_jinja(app)
    register_database(app)

    Mail(app)
    register_babel(app)
    register_routes(app)
    register_logger(app)
    return app


def register_database(app):
    """Database related configuration."""
    #: prepare for database
    db.init_app(app)
    db.app = app
    #: prepare for cache
    cache.init_app(app)


def register_hooks(app):
    """Hooks for request."""
    from .utils.user import get_current_user

    @app.before_request
    def load_current_user():
        g.user = get_current_user()
        if g.user and g.user.is_staff:
            g._before_request_time = time.time()

    @app.after_request
    def rendering_time(response):
        if hasattr(g, '_before_request_time'):
            delta = time.time() - g._before_request_time
            response.headers['X-Render-Time'] = delta * 1000
        return response


def register_routes(app):
    from .handlers import front, account, node, topic, user, admin
    app.register_blueprint(account.bp, url_prefix='/account')
    app.register_blueprint(node.bp, url_prefix='/node')
    app.register_blueprint(topic.bp, url_prefix='/topic')
    app.register_blueprint(user.bp, url_prefix='/user')
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(front.bp, url_prefix='')
    return app


def register_jinja(app):
    from . import filters
    from .handlers.admin import load_sidebar

    if not hasattr(app, '_static_hash'):
        app._static_hash = {}

    def static_url(filename):
        if app.testing:
            return filename

        if filename in app._static_hash:
            return app._static_hash[filename]

        with open(os.path.join(app.static_folder, filename), 'r') as f:
            content = f.read()
            hsh = hashlib.md5(content).hexdigest()

        app.logger.info('Generate %s md5sum: %s' % (filename, hsh))
        prefix = app.config.get('SITE_STATIC_PREFIX', '/static/')
        value = '%s%s?v=%s' % (prefix, filename, hsh[:5])
        app._static_hash[filename] = value
        return value

    @app.context_processor
    def register_context():
        return dict(
            static_url=static_url,
            db=dict(
                site_status=get_site_status,
                site_sidebar=load_sidebar,
            ),
        )

    app.jinja_env.filters['markdown'] = filters.markdown
    app.jinja_env.filters['timesince'] = filters.timesince
    app.jinja_env.filters['xmldatetime'] = filters.xmldatetime


def register_babel(app):
    """Configure Babel for internationality."""
    from flask_babel import Babel

    babel = Babel(app)
    supported = app.config.get('BABEL_SUPPORTED_LOCALES', ['en', 'zh'])
    default = app.config.get('BABEL_DEFAULT_LOCALE', 'en')

    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(supported, default)


def register_logger(app):
    """Track the logger for production mode."""
    if app.debug:
        return
    handler = logging.StreamHandler()
    handler.setLevel(logging.ERROR)
    app.logger.addHandler(handler)
