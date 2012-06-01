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
from july.app import JulyApplication
from july.web import run_server

define('debug', True, type=bool)
define('autoescape', None)

# site config
define('sitename', 'June', type=str)
define('version', '0.9.0', type=str)
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
define('image_backend', 'june.front.backends.LocalBackend')


def create_application():
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
    #: init application
    application = JulyApplication(**settings)

    #: register account app
    application.register_app(
        'june.account.handlers.app',
        url_prefix='/account'
    )
    application.register_app('june.account.service.app', url_prefix='/social')
    application.add_handler(
        ('/members', 'june.account.handlers.MembersHandler')
    )
    application.add_handler(
        ('/city/(.*)', 'june.account.handlers.CityMembersHandler')
    )

    #: register node app
    application.register_app('june.node.handlers.app', url_prefix='/node')

    from june.node.handlers import NodeListHandler
    application.add_handler(('/nodes', NodeListHandler))

    #: register topic app
    application.register_app('june.topic.handlers.app', url_prefix='/topic')

    from june.topic.handlers import CreateNodeTopicHandler
    from june.topic.handlers import ReplyHandler
    application.add_handler(('/node/(\w+)/create', CreateNodeTopicHandler))
    application.add_handler(('/reply/(\d+)', ReplyHandler))

    #: register dashboard app
    application.register_app(
        'june.dashboard.handlers.app',
        url_prefix='/dashboard'
    )

    #: register mail service
    application.register_app('july.ext.mail.handlers.app', url_prefix='/mail')

    #: register front app
    application.register_app('june.front.handlers.app', url_prefix='')

    #: register feedback app
    application.register_app('june.feedback.handlers.app', url_prefix='/feedback')

    for key in ['sitename', 'siteurl', 'sitefeed', 'version', 'ga']:
        application.register_context(key, options[key].value())

    import datetime
    application.register_context('now', datetime.datetime.utcnow)

    from june.filters import markdown, xmldatetime, localtime, timesince
    from june.filters import topiclink, normal_markdown
    application.register_filter('markdown', markdown)
    application.register_filter('normal_markdown', normal_markdown)
    application.register_filter('xmldatetime', xmldatetime)
    application.register_filter('localtime', localtime)
    application.register_filter('timesince', timesince)
    application.register_filter('topiclink', topiclink)

    return application


def main():
    from july.util import parse_config_file
    from tornado.options import parse_command_line
    parse_command_line()
    if options.settings:
        parse_config_file(options.settings)

    application = create_application()
    run_server(application)


if __name__ == "__main__":
    main()
