#!/usr/bin/env python
# -*- coding: utf-8 -*-

import memcache

from tornado.options import options
from june.lib.database import SQLAlchemy

if options.master.startswith('mysql'):
    master = options.master
    slaves = options.slaves.split()
    db = SQLAlchemy(master, slaves, pool_recycle=3600, echo=options.debug)
else:
    master = options.master
    slaves = options.slaves.split()
    db = SQLAlchemy(master, slaves, echo=options.debug)
cache = memcache.Client(options.memcache.split(), debug=options.debug)
