#!/usr/bin/env python

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


def login(user, password):
    if not user or not user.check_password(password):
        return None
    session.permanent = True
    session['id'] = user.id
    session['token'] = user.token
    return user


def logout():
    session.pop('id')
    session.pop('token')
