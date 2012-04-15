#!/usr/bin/python
# -*- coding: utf-8 -*-

#import logging
#import urllib
#import tornado.web
#from datetime import datetime
#from tornado.auth import httpclient
#from tornado.options import options
#from tornado.auth import GoogleMixin

from .lib import MailHandler


class WelcomeMailHdr(MailHandler):
    # use options to replace
    SEND_INFO = {
        'hostport': 'smtp.gmail.com:587',
        'username': 'reorx.xiao@gmail.com',
        'password': 'mx320lf2',
        'from_addr': 'reorx.xiao@gmail.com'
    }

    def post(self):
        to_addrs = self.get_argument('to_addrs').split(',')
        # self.send(to_addrs, self.render_mail('mail/hello.html'))
        self.send(to_addrs, 'hello')


handlers = [
    ('/mail/welcome', WelcomeMailHdr)
]
