#!/usr/bin/env python

import os
rootdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# site inform
SITE_TITLE = 'Python China'
SITE_SIDEBAR = os.path.join(rootdir, 'data', 'sidebar.html')
SITE_ABOUT = '/node/about'
# SITE_ANALYTICS = 'UA-xxx-xxx'


# This is a config file for development
DEBUG = True
SECRET_KEY = 'secret-key-for-development'

# cache
CACHE_TYPE = 'filesystem'
CACHE_DIR = os.path.join(rootdir, 'data', 'cache')

# babel settings
BABEL_DEFAULT_LOCALE = 'zh'
BABEL_SUPPORTED_LOCALES = ['zh']
