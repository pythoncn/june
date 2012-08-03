#!/usr/bin/env python

import time
import base64
import hmac
import hashlib
from flask import session
from .models import Member


def get_current_user(max_age_days=31):
    if 'id' not in session:
        return None
    user = Member.query.filter_by(id=session['id']).first()
    if not user:
        return None
    #TODO verify token
    return user
