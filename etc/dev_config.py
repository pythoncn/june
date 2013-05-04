#!/usr/bin/env python

import os
database = os.path.join(os.getcwd(), 'data', 'development.sqlite')

# site inform
SITE_TITLE = 'Python China'

# This is a config file for development
DEBUG = True
SECRET_KEY = 'secret-key-for-development'

SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % database

# babel settings
BABEL_DEFAULT_LOCALE = 'zh'
BABEL_SUPPORTED_LOCALES = ['zh']
