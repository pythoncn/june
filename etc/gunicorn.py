#!/usr/bin/env python

import gevent.monkey
gevent.monkey.patch_all()
import multiprocessing

#bind = 'unix:/path/to/june.sock'
bind = '127.0.0.1:8000'
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'egg:gunicorn#gevent'

# you should change this
user = 'lepture'

# maybe you like error
accesslog = '-'
loglevel = 'warning'
errorlog = '-'

secure_scheme_headers = {
    'X-SCHEME': 'https',
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on',
}
x_forwarded_for_header = 'X-FORWARDED-FOR'
