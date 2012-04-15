#!/usr/bin/env python
# -*- coding: utf-8 -*-

import memcache

from tornado.options import options
from junetornado.database import SQLAlchemy

if options.master.startswith('mysql'):
    db = SQLAlchemy(options.master, pool_recycle=3600, echo=options.debug)
else:
    db = SQLAlchemy(options.master, echo=options.debug)

cache = memcache.Client(options.memcache.split(), debug=options.debug)
app_list = [
    ('account', 'june.account'),
    ('node', 'june.node'),
    ('topic', 'june.topic'),
    ('admin', 'june.dashboard'),
    ('mail', 'june.mail'),
]
