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
        db.session.add(user)
        if operation == 'insert':
            # node count increase
            node = Node.query.get(model.node_id)
            node.count += 1
            db.session.add(node)

            # user status in this node
            ns = NodeStatus.query.filter_by(
                node_id=model.node_id, account_id=model.account_id
            ).first()
            if not ns:
                ns = NodeStatus(
                    node_id=model.node_id,
                    account_id=model.account_id,
                    topic_count=0,
                )
            ns.topic_count += 1
            db.session.add(ns)

        elif operation == 'delete':
            node = Node.query.get(model.node_id)
            node.count -= 1
            db.session.add(node)

            ns = NodeStatus.query.filter_by(
                node_id=model.node_id, account_id=model.account_id
            ).first()
            if ns and ns.topic_count:
                ns.topic_count -= 1
                db.session.add(ns)

        db.session.commit()

    elif isinstance(model, Reply):
        pass

models_committed.connect(_committed)
