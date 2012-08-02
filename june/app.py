#!/usr/bin/env python

import os
CONF = os.path.join(os.path.abspath(os.path.dirname(__file__)), '_config')

from flask import Flask, render_template
from utils import import_object

app = Flask(
    __name__,
    static_folder='_static',
    template_folder='_templates'
)
app.config.from_pyfile(os.path.join(CONF, 'base.py'))


def register(app, blueprint):
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


def prepare_app(app):
    #: int account blueprint
    register(app, 'account')
    register(app, 'node')

    #: init topic blueprint
    return app


def dev_app():
    app.config.from_pyfile(os.path.join(CONF, 'development.py'))

    prepare_app(app)
    return app


@app.route('/')
def hello():
    return render_template('index.html')


if __name__ == '__main__':
    dev_app()
    app.run()
