#!/usr/bin/env python
# coding: utf-8

import os
from flask_script import Manager
from june.app import create_app


settings = os.path.abspath('./etc/settings.py')
if not os.path.exists(settings):
    settings = os.path.abspath('./etc/dev_config.py')

if 'JUNE_SETTINGS' not in os.environ:
    os.environ['JUNE_SETTINGS'] = settings

app = create_app()
manager = Manager(app)


@manager.command
def runserver(port=5000):
    """Runs a development server."""
    from flask import send_from_directory

    port = int(port)

    @app.route('/static/<path:filename>')
    def static_file(filename):
        datadir = os.path.abspath('public/static')
        return send_from_directory(datadir, filename)

    app.run(port=port)


@manager.command
def createdb():
    """Create database for june."""
    from june.models import db
    db.create_all()


if __name__ == '__main__':
    manager.run()
