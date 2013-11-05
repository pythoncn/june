# coding: utf-8
"""
    june._flask
    ~~~~~~~~~~~

    Rewrite the interface of Flask.

    :copyright: (c) 2013 by Hsiaoming Yang.
"""

import datetime
from flask import Flask as _Flask
from flask.json import JSONEncoder as _JSONEncoder


class JSONEncoder(_JSONEncoder):
    def default(self, o):
        if hasattr(o, '__getitem__') and hasattr(o, 'keys'):
            return dict(o)
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        return _JSONEncoder.default(self, o)


class Flask(_Flask):
    json_encoder = JSONEncoder

