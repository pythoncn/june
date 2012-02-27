#!/usr/bin/env python
# -*- coding: utf-8 -*-

import memcache

from tornado.options import options
from june.lib.database import SQLAlchemy

if options.database.startswith('mysql'):
    db = SQLAlchemy(options.database, pool_recycle=3600, echo=options.debug)
else:
    db = SQLAlchemy(options.database, echo=options.debug)
cache = memcache.Client(options.memcache.split(), debug=options.debug)
