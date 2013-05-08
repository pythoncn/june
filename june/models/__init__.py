# coding: utf-8
# flake8: noqa

import gevent
import datetime
from ._base import *
from .account import *
from .node import *
from .topic import *
from flask import Flask, current_app
from flask.ext.sqlalchemy import models_committed


def _committed(sender, changes):
    def _run(config):
        app = Flask('june')
        app.config = config
        with app.test_request_context():
            map(lambda o: _listen(*o), changes)

    gevent.spawn(_run, current_app.config)


def _listen(model, operation):
    if isinstance(model, Topic):
        # update user's last active time
        user = Account.query.get(model.account_id)
        user.active = datetime.datetime.utcnow()
        user.save()
        if operation == 'insert':
            # node count increase
            node = Node.query.get(model.node_id)
            node.count += 1
            node.save()
        elif operation == 'delete':
            node = Node.query.get(model.node_id)
            node.count -= 1
            node.save()

    elif isinstance(model, Reply):
        pass

models_committed.connect(_committed)
