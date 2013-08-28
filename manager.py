#!/usr/bin/env python
# coding: utf-8

import gevent.monkey
gevent.monkey.patch_all()

import os
import sys
import argparse
from flask_script import Manager, Command
from june.app import create_app


settings = os.path.abspath('./etc/settings.py')
if not os.path.exists(settings):
    settings = os.path.abspath('./etc/dev_config.py')

if 'JUNE_SETTINGS' not in os.environ:
    os.environ['JUNE_SETTINGS'] = settings

app = create_app()
from june.models import db
app.db = db

manager = Manager(app)


@manager.command
def runserver(port=5000, with_profile=False):
    """Runs a development server."""
    from flask import send_from_directory
    from gevent.wsgi import WSGIServer
    from werkzeug.serving import run_with_reloader
    from werkzeug.debug import DebuggedApplication
    from werkzeug.contrib.profiler import ProfilerMiddleware

    port = int(port)

    @app.route('/static/<path:filename>')
    def static_file(filename):
        datadir = os.path.abspath('public/static')
        return send_from_directory(datadir, filename)

    if with_profile:
        f = open('./data/profile.log', 'w')
        wsgi = ProfilerMiddleware(app, f)
    else:
        wsgi = DebuggedApplication(app)

    @run_with_reloader
    def run_server():
        print('start server at: 127.0.0.1:%s' % port)

        http_server = WSGIServer(('', port), wsgi)
        http_server.serve_forever()

    try:
        run_server()
    except (KeyboardInterrupt, TypeError):
        sys.exit()


if __name__ == '__main__':
    manager.run()
