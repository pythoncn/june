#!/usr/bin/env python

import os
os.environ['TZ'] = 'UTC'
os.environ["PYTHON_EGG_CACHE"] = "/tmp/egg"

ROOT = os.path.abspath(os.path.dirname(__file__))
try:
    import june
    print('Start june version: %s' % june.__version__)
except ImportError:
    import site
    site.addsitedir(os.path.split(ROOT)[0])
    print('Development of june')

import tornado.options
import tornado.locale
from tornado.options import define, options
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado import web


class Application(web.Application):
    def __init__(self):
        from june.config import db, cache  # init db
        from june.urls import handlers, ui_modules, sub_handlers
        if hasattr(options, 'template_path'):
            template_path = options.template_path
        else:
            template_path = os.path.join(ROOT, "templates")
        settings = dict(
            debug=options.debug,
            autoescape=None,
            cookie_secret=options.cookie_secret,
            xsrf_cookies=options.xsrf_cookies,
            login_url=options.login_url,

            template_path=template_path,
            static_path=options.static_path,
            static_url_prefix=options.static_url_prefix,

            ui_modules=ui_modules,
        )
        super(Application, self).__init__(handlers, **settings)
        Application.db = db.session
        Application.cache = cache
        tornado.locale.load_translations(os.path.join(ROOT, "locale"))

        for sub_handler in sub_handlers:
            self.add_handlers(sub_handler[0], sub_handler[1])


def parse_config_file(path):
    config = {}
    exec(compile(open(path).read(), path, 'exec'), config, config)
    for name in config:
        if name in options:
            options[name].set(config[name])
        else:
            define(name, config[name])


def run_server():
    define('config', '')
    define('port', '8000')
    tornado.options.parse_command_line()
    parse_config_file(options.config)
    server = HTTPServer(Application(), xheaders=True)
    server.bind(int(options.port))
    server.start(int(options.num_processes))
    IOLoop.instance().start()


if __name__ == "__main__":
    run_server()
