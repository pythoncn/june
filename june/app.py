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

# server config
define('port', 8000)
define('debug', True)
define('master', "sqlite:////tmp/june.sqlite")
define('slaves', '')
define('memcache', "127.0.0.1:11211")

# site config
define('sitename', 'June')
define('siteurl', 'http://lepture.com/project/june')
define('sitefeed', '/feed')
define('password_secret', '')  # reset it
define('static_path', os.path.join(PROJDIR, 'static'))
define('static_url_prefix', "/static/")
define('login_url', "/account/signin")
define('template_path', os.path.join(PROJDIR, "templates"))
define('dashboard_template_path',
       os.path.join(PROJDIR, "dashboard", "templates"))
define('locale_path', os.path.join(PROJDIR, 'locale'))
define('default_locale', 'en_US')
define('xsrf_cookies', True)
define('cookie_secret', '')  # reset it

# factor config
define('reply_factor_for_topic', 800)
define('reply_time_factor', 400)
define('up_factor_for_topic', 1000)
define('up_factor_for_user', 2)
define('down_factor_for_topic', 800)
define('down_factor_for_user', 1)
define('vote_reply_factor_for_topic', 500)
define('vote_reply_factor_for_user', 2)

# third party support config
define('gravatar_base_url', "http://www.gravatar.com/avatar/")
define('default_gravatar', '')
define('recaptcha_key', '')
define('recaptcha_secret', '')
define('recaptcha_theme', 'clean')
define('emoji_url', '')
define('ga', '')


class Application(web.Application):
    def __init__(self):
        from june.config import db, cache  # init db
        from june.urls import handlers, ui_modules
        settings = dict(
            debug=options.debug,
            autoescape=None,
            cookie_secret=options.cookie_secret,
            xsrf_cookies=options.xsrf_cookies,
            login_url=options.login_url,

            template_path=options.template_path,
            static_path=options.static_path,
            static_url_prefix=options.static_url_prefix,

            ui_modules=ui_modules,
        )
        super(Application, self).__init__(handlers, **settings)
        Application.db = db.session
        Application.cache = cache
        tornado.locale.load_translations(options.locale_path)
        tornado.locale.set_default_locale(options.default_locale)


def run_server():
    define('config', '')
    tornado.options.parse_command_line()
    parse_config_file(options.config)
    server = HTTPServer(Application(), xheaders=True)
    server.listen(int(options.port))
    IOLoop.instance().start()


if __name__ == "__main__":
    run_server()
