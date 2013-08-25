import os
rootdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DEBUG = False
TESTING = False
VERIFY_EMAIL = True
VERIFY_USER = True

#: site
SITE_TITLE = 'June Forum'
SITE_URL = '/'
# SITE_URL = 'http://python-china.org/'
SITE_STYLES = [
    '/static/css/bootstrap.css',
    '/static/css/bootstrap-responsive.css',
    '/static/css/pygments.css',
    '/static/css/site.css',
]
SITE_SCRIPTS = [
    'http://lib.sinaapp.com/js/jquery/1.9.1/jquery-1.9.1.min.js',
    '/static/js/bootstrap.js',
    '/static/js/site.js',
]
#: sidebar is a absolute path
# SITE_SIDEBAR = '/path/to/sidebar.html'
#: about page url
# SITE_ABOUT = '/node/about'
# SITE_ANALYTICS = 'UA-xxx-xxx'

#: session
SESSION_COOKIE_NAME = 'june'
#SESSION_COOKIE_SECURE = True
PERMANENT_SESSION_LIFETIME = 3600 * 24 * 30

#: account
SECRET_KEY = 'secret key'
PASSWORD_SECRET = 'password secret'
GRAVATAR_BASE_URL = 'http://www.gravatar.com/avatar/'
GRAVATAR_EXTRA = ''

#: sqlalchemy
# SQLALCHEMY_DATABASE_URI = 'mysql://user@localhost/dbname
# SQLALCHEMY_POOL_SIZE = 100
# SQLALCHEMY_POOL_TIMEOUT = 10
# SQLALCHEMY_POOL_RECYCEL = 3600

#: email settings
# MAIL_SERVER = 'smtp.gmail.com'
# MAIL_USE_SSL = True
# MAIL_USERNAME = ''
# MAIL_PASSWORD = ''
# MAIL_DEFAULT_SENDER = ('name', 'noreply@email.com')

#: cache settings
# find options on http://pythonhosted.org/Flask-Cache/
# CACHE_TYPE = 'filesystem'
# CACHE_DIR = os.path.join(rootdir, 'data', 'cache')

#: i18n settings
# BABEL_DEFAULT_LOCALE = 'zh'
# BABEL_SUPPORTED_LOCALES = ['zh']
BABEL_DIRNAME = os.path.join(rootdir, 'i18n')

#: storage settings
STORAGE_TYPE = 'local'
STORAGE_LOCAL_URL = '/images/'
STORAGE_LOCAL_ROOT = os.path.join(rootdir, 'data', 'images')
