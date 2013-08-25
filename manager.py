#!/usr/bin/env python
# coding: utf-8

import gevent.monkey
gevent.monkey.patch_all()

import os
import sys
import argparse
from flask_script import Manager, Command
from alembic.config import CommandLine
from june.app import create_app


class CatchAllParser(object):
    def parse_known_args(self, app_args):
        return argparse.Namespace(), app_args


class AlembicCommand(Command):
    capture_all_args = True

    def create_parser(self, prog):
        return CatchAllParser()

    def run(self, args):
        prog = '%s %s' % (os.path.basename(sys.argv[0]), sys.argv[1])
        return CommandLine(prog=prog).main(argv=args)


settings = os.path.abspath('./etc/settings.py')
if not os.path.exists(settings):
    settings = os.path.abspath('./etc/dev_config.py')

if 'JUNE_SETTINGS' not in os.environ:
    os.environ['JUNE_SETTINGS'] = settings

app = create_app()
from june.models import db
app.db = db

manager = Manager(app)
manager.add_command('migrate', AlembicCommand())


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
