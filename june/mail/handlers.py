#!/usr/bin/python
# -*- coding: utf-8 -*-

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
        self.send(to_addr, 'Hello', 'how are you', self.render_mail('mail_example.html'))


handlers = [
    ('/mail/welcome', WelcomeMailHdr)
]
