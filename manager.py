# coding: utf-8

import gevent.monkey
gevent.monkey.patch_all()

from flask.ext.script import Manager
from june.app import create_app

CONFIG = '_config/development.py'

manager = Manager(create_app())


@manager.command
def runserver(port=5000, config=CONFIG):
    """Runs a development server."""
    from gevent.wsgi import WSGIServer
    from werkzeug.serving import run_with_reloader
    from werkzeug.debug import DebuggedApplication

    port = int(port)
    app = create_app(config)

    @run_with_reloader
    def run_server():
        print('start server at: 127.0.0.1:%s' % port)
        http_server = WSGIServer(('', port), DebuggedApplication(app))
        http_server.serve_forever()

    run_server()


@manager.command
def createdb(config=CONFIG):
    """Create a database."""
    from june.models import db
    create_app(config)
    db.create_all()


if __name__ == '__main__':
    manager.run()
