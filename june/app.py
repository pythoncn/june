#!/usr/bin/env python
import os

PROJDIR = os.path.abspath(os.path.dirname(__file__))
ROOTDIR = os.path.split(PROJDIR)[0]
try:
    import june
    print('Start june version: %s' % june.__version__)
except ImportError:
    import site
    site.addsitedir(ROOTDIR)
    print('Development of june')
from tornado.options import define, options
from july import JulyApplication, run_server

_first_run = True
if _first_run:
    options.debug = True
    options.autoescape = None

    # site config
    define('sitename', 'June', type=str)
    define('version', '1.1.0', type=str)
    define('siteurl', 'http://lepture.com/project/june/')
    define('sitefeed', '/feed')

    define('static_path', os.path.join(PROJDIR, '_static'))
    define('static_url_prefix', '/static/', type=str)
    define('template_path', os.path.join(PROJDIR, "_templates"))

    options.locale_path = os.path.join(PROJDIR, '_locale')
    define('login_url', '/account/signin', type=str)

    # factor config
    define('reply_factor_for_topic', 600, type=int)
    define('reply_time_factor', 1000, type=int)
    define('up_factor_for_topic', 1500, type=int)
    define('up_factor_for_user', 1, type=int)
    define('down_factor_for_topic', 800, type=int)
    define('down_factor_for_user', 1, type=int)
    define('accept_reply_factor_for_user', 1, type=int)
    define('up_max_for_user', 10, type=int)
    define('down_max_for_user', 4, type=int)
    define('vote_max_for_user', 4, type=int)
    define('promote_topic_cost', 100, type=int)

    # third party support config
    define('gravatar_base_url', "http://www.gravatar.com/avatar/")
    define('gravatar_extra', '')
    define('recaptcha_key', '')
    define('recaptcha_secret', '')
    define('recaptcha_theme', 'clean')
    define('emoji_url', '')
    define('ga', '')  # google analytics
    define('gcse', '')  # google custom search

    # image backend
    define('backend', 'june.backend.local.LocalBackend')

    _first_run = False


def main():
    from july.util import parse_config_file
    from tornado.options import parse_command_line
    parse_command_line()
    if options.settings:
        parse_config_file(options.settings)

    settings = dict(
        debug=options.debug,
        autoescape=options.autoescape,
        cookie_secret=options.cookie_secret,
        xsrf_cookies=True,
        login_url=options.login_url,

        template_path=options.template_path,
        static_path=options.static_path,
        static_url_prefix=options.static_url_prefix,
    )
    application = JulyApplication(handlers=[], **settings)

    from june.account.handlers import account_app
    application.register_app(account_app, url_prefix='/account')

    from june.node.handlers import node_app
    application.register_app(node_app, url_prefix='/node')

    from june.topic.handlers import topic_app
    application.register_app(topic_app, url_prefix='/topic')

    from june.dashboard.handlers import dashboard_app
    application.register_app(dashboard_app, url_prefix='/dashboard')

    application.register_context('sitename', options.sitename)
    application.register_context('version', options.version)

    run_server(application)

if __name__ == "__main__":
    main()
