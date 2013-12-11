import os

DEBUG = False
TESTING = False
VERIFY_EMAIL = True
VERIFY_USER = True

ROOT_FOLDER = os.path.dirname(os.path.abspath(__file__))
if os.path.exists('public/static'):
    STATIC_FOLDER = os.path.join(os.getcwd(), 'public', 'static')
else:
    STATIC_FOLDER = os.path.join(ROOT_FOLDER, 'public', 'static')

#: site
SITE_TITLE = 'Python China'
SITE_URL = '/'
# SITE_URL = 'http://python-china.org/'

#: sidebar is a absolute path
# SITE_SIDEBAR = '/path/to/sidebar.html'

#: about page url
# SITE_ABOUT = '/node/about'

# SITE_ANALYTICS = 'UA-xxx-xxx'

#: session
SESSION_COOKIE_NAME = '_s'
#SESSION_COOKIE_SECURE = True
PERMANENT_SESSION_LIFETIME = 3600 * 24 * 30

#: account
SECRET_KEY = 'secret key'
PASSWORD_SECRET = 'password secret'
GRAVATAR_BASE_URL = 'http://www.gravatar.com/avatar/'
GRAVATAR_EXTRA = ''

#: sqlalchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % os.path.join(
    os.getcwd(), 'db.sqlite'
)
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
# CACHE_TYPE = 'simple'

#: i18n settings
# BABEL_DEFAULT_LOCALE = 'zh'
# BABEL_SUPPORTED_LOCALES = ['zh']
