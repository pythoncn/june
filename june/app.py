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
from junetornado import JuneApplication, run_server
_first_run = True

if _first_run:
    options.port = 8000
    options.autoescape = None
    define('master', "sqlite:////tmp/june.sqlite")
    define('slaves', '')
    define('memcache', "127.0.0.1:11211")

    # site config
    define('sitename', 'June')
    define('siteurl', 'http://lepture.com/project/june')
    define('sitefeed', '/feed')
    define('password_secret', '')  # reset it

    options.static_path = os.path.join(PROJDIR, 'static')
    options.template_path = os.path.join(PROJDIR, "templates")

    options.locale_path = os.path.join(PROJDIR, 'locale')
    options.xsrf_cookies = True

    # factor config
    define('reply_factor_for_topic', 600)
    define('reply_time_factor', 1000)
    define('up_factor_for_topic', 1500)
    define('up_factor_for_user', 1)
    define('down_factor_for_topic', 800)
    define('down_factor_for_user', 1)
    define('accept_reply_factor_for_user', 1)
    define('up_max_for_user', 10)
    define('down_max_for_user', 4)
    define('vote_max_for_user', 4)
    define('promote_topic_cost', 100)

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


if __name__ == "__main__":
    run_server(JuneApplication)
