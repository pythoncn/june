#!/usr/bin/env python

import time
import base64
import hmac
import hashlib
from flask import request
from .models import Member
from flask import current_app


def get_current_user(app, name, max_age_days=31):
    value = request.cookies.get(name)
    if not value:
        return None
    secret = app.config.setdefault('COOKIE_SECRET', 'cookie-secret')
    value = decode_signed_value(secret, name, value, max_age_days)
    try:
        uid, token = value.split('/')
    except:
        return None
    user = Member.query.filter_by(id=uid).first()
    if not user:
        return None
    if user.token != token:
        return None
    return user


if str is unicode:
    b = lambda s: s.encode('latin1')
else:
    b = lambda s: s


def utf8(value):
    """Converts a string argument to a byte string.

    If the argument is already a byte string or None, it is returned unchanged.
    Otherwise it must be a unicode string and is encoded as utf8.
    """
    if isinstance(value, (bytes, type(None))):
        return value
    assert isinstance(value, unicode)
    return value.encode("utf-8")


def _time_independent_equals(a, b):
    if len(a) != len(b):
        return False
    result = 0
    if type(a[0]) is int:  # python3 byte strings
        for x, y in zip(a, b):
            result |= x ^ y
    else:  # python2
        for x, y in zip(a, b):
            result |= ord(x) ^ ord(y)
    return result == 0


def create_signed_value(secret, name, value):
    timestamp = utf8(str(int(time.time())))
    value = base64.b64encode(utf8(value))
    signature = _create_signature(secret, name, value, timestamp)
    value = b("|").join([value, timestamp, signature])
    return value


def decode_signed_value(secret, name, value, max_age_days=31):
    if not value:
        return None
    parts = utf8(value).split(b("|"))
    if len(parts) != 3:
        return None

    logging = current_app.logger
    signature = _create_signature(secret, name, parts[0], parts[1])
    if not _time_independent_equals(parts[2], signature):
        logging.warning("Invalid cookie signature %r", value)
        return None
    timestamp = int(parts[1])
    if timestamp < time.time() - max_age_days * 86400:
        logging.warning("Expired cookie %r", value)
        return None
    if timestamp > time.time() + 31 * 86400:
        # _cookie_signature does not hash a delimiter between the
        # parts of the cookie, so an attacker could transfer trailing
        # digits from the payload to the timestamp without altering the
        # signature.  For backwards compatibility, sanity-check timestamp
        # here instead of modifying _cookie_signature.
        logging.warning(
            "Cookie timestamp in future; possible tampering %r", value
        )
        return None
    if parts[1].startswith(b("0")):
        logging.warning("Tampered cookie %r", value)
    try:
        return base64.b64decode(parts[0])
    except Exception:
        return None


def _create_signature(secret, *parts):
    hash = hmac.new(utf8(secret), digestmod=hashlib.sha1)
    for part in parts:
        hash.update(utf8(part))
    return utf8(hash.hexdigest())
