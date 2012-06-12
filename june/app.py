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
from tornado.options import options
from july.util import reset_option
from july.app import JulyApplication
from july.web import init_options, run_server

reset_option('debug', True, type=bool)
reset_option('autoescape', None)

# site config
reset_option('sitename', 'June', type=str)
reset_option('version', '0.9.0', type=str)
reset_option('siteurl', 'http://lepture.com/project/june/')
reset_option('sitefeed', '/feed')

reset_option('static_path', os.path.join(PROJDIR, '_static'))
reset_option('static_url_prefix', '/static/', type=str)
reset_option('template_path', os.path.join(PROJDIR, "_templates"))

reset_option('locale_path', os.path.join(PROJDIR, '_locale'))
reset_option('login_url', '/account/signin', type=str)

# factor config
reset_option('reply_factor_for_topic', 600, type=int)
reset_option('reply_time_factor', 1000, type=int)
reset_option('up_factor_for_topic', 1500, type=int)
reset_option('up_factor_for_user', 1, type=int)
reset_option('down_factor_for_topic', 800, type=int)
reset_option('down_factor_for_user', 1, type=int)
reset_option('accept_reply_factor_for_user', 1, type=int)
reset_option('up_max_for_user', 10, type=int)
reset_option('down_max_for_user', 4, type=int)
reset_option('vote_max_for_user', 4, type=int)
reset_option('promote_topic_cost', 100, type=int)

# third party support config
reset_option('gravatar_base_url', "http://www.gravatar.com/avatar/")
reset_option('gravatar_extra', '')
reset_option('recaptcha_key', '')
reset_option('recaptcha_secret', '')
reset_option('recaptcha_theme', 'clean')
reset_option('emoji_url', '')
reset_option('ga', '')  # google analytics
reset_option('gcse', '')  # google custom search

# image backend
reset_option('image_backend', 'june.front.backends.LocalBackend')


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
    # application.register_app('june.feedback.handlers.app')

    for key in ['sitename', 'siteurl', 'sitefeed', 'version', 'ga', 'gcse']:
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
    init_options()
    application = create_application()
    run_server(application)


if __name__ == "__main__":
    main()
