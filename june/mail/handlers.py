#!/usr/bin/python
# -*- coding: utf-8 -*-

#from tornado.options import options

from .lib import MailHandler


class WelcomeMailHdr(MailHandler):
    # use options to replace
    SEND_INFO = {
        'hostport': 'smtp.gmail.com:587',
        'username': 'test@gmail.com',
        'password': 'test',
        'from_addr': 'test@gmail.com'
    }

    def post(self):
        to_addr = self.get_argument('to_addr')
        self.send(to_addr, 'Hello', 'how are you',
                  self.render_mail('mail/example.html'))


urls = [
    ('/mail/welcome', WelcomeMailHdr)
]
