#!/usr/bin/env python

import time
import base64
import hmac
import hashlib
from flask import session
from .models import Member


def get_current_user():
    if 'id' not in session or 'token' not in session:
        return None

    user = Member.query.filter_by(id=session['id']).first()
    if not user:
        return None
    if user.token != session['token']:
        logout()
        return None
    return user


def login(user):
    if not user:
        return
    session.permanent = True
    session['id'] = user.id
    session['token'] = user.token


def logout():
    session.pop('id')
    session.pop('token')
