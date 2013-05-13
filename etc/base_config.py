DEBUG = False
TESTING = False
VERIFY_EMAIL = True

#: site
SITE_TITLE = 'June Forum'
SITE_URL = '/'
SITE_STYLES = [
    '/_static/css/bootstrap.css',
    '/_static/css/bootstrap-responsive.css',
    '/_static/css/site.css',
]
SITE_SCRIPTS = [
    'http://lib.sinaapp.com/js/jquery/1.9.1/jquery-1.9.1.min.js',
    '/_static/js/bootstrap.js',
    '/_static/js/site.js',
]

#: session
SESSION_COOKIE_NAME = 'june'
#SESSION_COOKIE_SECURE = True
PERMANENT_SESSION_LIFETIME = 3600 * 24 * 30

#: account
PASSWORD_SECRET = 'password-secret'
GRAVATAR_BASE_URL = 'http://www.gravatar.com/avatar/'
GRAVATAR_EXTRA = ''

#: sqlalchemy
# SQLALCHEMY_POOL_SIZE = 100
# SQLALCHEMY_POOL_TIMEOUT = 10
# SQLALCHEMY_POOL_RECYCEL = 3600

#: cache
# find options on http://pythonhosted.org/Flask-Cache/
