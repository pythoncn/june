#!/usr/bin/env python

import os
os.environ['TZ'] = 'UTC'
os.environ["PYTHON_EGG_CACHE"] = "/tmp/egg"

PROJDIR = os.path.abspath(os.path.dirname(__file__))
ROOTDIR = os.path.split(PROJDIR)[0]
try:
    import june
    print('Start june version: %s' % june.__version__)
except ImportError:
    import site
    site.addsitedir(ROOTDIR)
    print('Development of june')

import tornado.options
import tornado.locale
from tornado.options import define, options
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado import web
from june.lib.util import parse_config_file


class Application(web.Application):
    def __init__(self):
        from june.config import db, cache  # init db
        from june.urls import handlers, ui_modules
        if hasattr(options, 'template_path') and options.template_path:
            template_path = options.template_path
        else:
            template_path = os.path.join(PROJDIR, "templates")
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
        if hasattr(options, 'locale_path') and options.locale_path:
            locale_path = options.locale_path
        else:
            locale_path = os.path.join(PROJDIR, 'locale')
        tornado.locale.load_translations(locale_path)


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
