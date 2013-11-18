# coding: utf-8

from flask import current_app, url_for, render_template
from flask.ext.babel import gettext as _
from flask_mail import Message
from .user import create_auth_token


def send_mail(app, msg):
    mail = app.extensions['mail']
    if not mail.default_sender:
        return
    mail.send(msg)


def signup_mail(user, path=None):
    config = current_app.config
    msg = Message(
        _("Signup for %(site)s", site=config['SITE_TITLE']),
        recipients=[user.email],
    )
    reply_to = config.get('MAIL_REPLY_TO', None)
    if reply_to:
        msg.reply_to = reply_to

    host = config.get('SITE_URL', '')
    dct = {
        'host': host.rstrip('/'),
        'token': create_auth_token(user)
    }
    if path:
        dct['path'] = path
    else:
        dct['path'] = url_for('account.signup')
    link = '%(host)s%(path)s?token=%(token)s' % dct
    html = render_template('email/signup.html', user=user, link=link)
    msg.html = html
    send_mail(current_app, msg)
    return msg


def find_mail(user):
    config = current_app.config
    msg = Message(
        _("Find password for %(site)s", site=config['SITE_TITLE']),
        recipients=[user.email],
    )
    reply_to = config.get('MAIL_REPLY_TO', None)
    if reply_to:
        msg.reply_to = reply_to
    host = config.get('SITE_URL', '')
    dct = {
        'host': host.rstrip('/'),
        'path': url_for('account.reset'),
        'token': create_auth_token(user)
    }
    link = '%(host)s%(path)s?token=%(token)s' % dct
    html = render_template('email/find.html', user=user, link=link)
    msg.html = html
    send_mail(current_app, msg)
    return msg
