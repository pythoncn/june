#!/usr/bin/env python

import gevent.monkey
gevent.monkey.patch_all()

import multiprocessing

bind = 'unix:/home/{{user}}/var/run/june.sock'

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'egg:gunicorn#gevent'

# you should change this
user = '{{user}}'

# maybe you like error
loglevel = 'warning'
errorlog = '-'

secure_scheme_headers = {
    'X-SCHEME': 'https',
}
x_forwarded_for_header = 'X-FORWARDED-FOR'
