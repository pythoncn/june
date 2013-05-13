# coding: utf-8

import gevent.monkey
gevent.monkey.patch_all()

import os
from flask.ext.script import Manager
from june.app import create_app

CONFIG = os.path.abspath('./etc/dev_config.py')

app = create_app(CONFIG)
manager = Manager(app)


@manager.command
def runserver(port=5000, with_profile=False):
    """Runs a development server."""
    from gevent.wsgi import WSGIServer
    from werkzeug.serving import run_with_reloader
    from werkzeug.debug import DebuggedApplication
    from werkzeug.contrib.profiler import ProfilerMiddleware

    port = int(port)

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

    run_server()


@manager.command
def createdb():
    """Create a database."""
    from june.models import db
    db.create_all()


if __name__ == '__main__':
    manager.run()
