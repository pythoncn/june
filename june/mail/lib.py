#!/usr/bin/python
# -*- coding: utf-8 -*-

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from july import JulyHandler
from june.lib import validators


class MailHandler(JulyHandler):
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
    ...         to_addr = self.get_argument('to_addr')
    ...         self.send(to_addr, 'Hello', 'how are you', self.render_mail('mail_example.html'))
    """
    SEND_INFO = {}

    def initialize(self):
        client = smtplib.SMTP(self.SEND_INFO['hostport'])
        client.ehlo()
        client.starttls()
        client.login(self.SEND_INFO['username'], self.SEND_INFO['password'])
        self.client = client

    def finish(self, *args, **kwgs):
        super(MailHandler, self).finish(*args, **kwgs)
        self.client.quit()

    def generate_message(self, to_addr, subject, text, html=None):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.SEND_INFO['from_addr']
        msg['To'] = to_addr

        # validate address before sending
        if not validators.email(msg['From'])\
            or not validators.email(msg['To']):
            raise ValueError('Email address format invalid: %s, %s' %\
                             (msg['From'], msg['To']))

        # According to RFC 2046, the last part of a multipart message,
        # in this case
        # the HTML message, is best and preferred.
        msg.attach(MIMEText(text, 'plain'))
        if html:
            msg.attach(MIMEText(html, 'html'))

        return msg.as_string()

    def render_mail(self, template_name, context={}):
        """
        render a mail from template and context data
        """
        return self.render_string(template_name, **context)

    def send(self, to_addr, subject, text, html=None):
        """
        basic mail sending method, only send to one address
        """
        msg = self.generate_message(to_addr, subject, text, html)
        self.client.sendmail(self.SEND_INFO['from_addr'], to_addr, msg)
