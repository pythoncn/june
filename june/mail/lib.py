#!/usr/bin/python
# -*- coding: utf-8 -*-

import smtplib
from junetornado import JuneHandler


class MailHandler(JuneHandler):
    """
    Usage:

    >>> class WelcomeMailHandler(MailHandler):
    >>>     SEND_INFO = {
    ...         'hostport': 'smtp.gmail.com:587',
    ...         'username': 'test@gmail.com',
    ...         'password'; 'test',
    ...         'from_addr': 'test@gmail.com'
    ...     }
    ...
    >>>     def post(self):
    >>>         to_addrs = self.get_argument('to_addrs').split(',')
    >>>         self.send(to_addrs, self.render_mail('mail/hello.html'))
    """
    SEND_INFO = {}

    def send(self, to_addrs, body):
        """
        basic mail sending method
        """
        self._connect_smtp()

        if isinstance(to_addrs, str):
            to_addrs = [to_addrs, ]
        assert isinstance(to_addrs, list), 'to_addrs argument must be a list'

        self.client.sendmail(self.SEND_INFO['from_addr'], to_addrs, body)

    def _connect_smtp(self):
        client = smtplib.SMTP(self.SEND_INFO['hostport'])
        client.ehlo()
        client.starttls()
        client.login(self.SEND_INFO['username'], self.SEND_INFO['password'])
        self.client = client

    def render_mail(self, template_name, context={}):
        """
        render a mail from template and context data
        """
        return self.render_string(template_name, **context)
