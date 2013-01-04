# coding: utf-8

from flask.ext.script import Manager

from june.app import app

manager = Manager(app)


@manager.command
def runserver(port=5000):
    """Run a development server"""
    from gevent.wsgi import WSGIServer
    from werkzeug.server import run_with_reloader
    from werkzeug.debug import DebuggerApplication

    port = int(port)

    @run_with_reloader
    def run_server():
        print('start server at: 127.0.0.1:%s' % port)
        http_server = WSGIServer(('', port), DebuggerApplication(app))
        http_server.serve_forever()

    run_server()


if __name__ == '__main__':
    manager.run()
