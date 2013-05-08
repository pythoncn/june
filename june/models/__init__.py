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


def fill_topics(items, user=None, node=None):
    if user:
        items = map(lambda o: _attach_user(o, user), items)
    else:
        uids = set(map(lambda o: o.account_id, items))
        users = get_users(uids)
        items = map(lambda o: _attach_user(o, users[o.account_id]), items)
    if node:
        items = map(lambda o: _attach_node(o, node), items)
    else:
        uids = set(map(lambda o: o.node_id, items))
        nodes = get_nodes(uids)
        items = map(lambda o: _attach_node(o, nodes[o.node_id]), items)
    return items


def get_users(uids):
    return get_by_ids(Account, uids)


def get_nodes(uids):
    return get_by_ids(Node, uids)


def get_by_ids(model, uids):
    if len(uids) == 1:
        data = model.query.get(uids.pop())
        return {data.id: data}

    data = model.query.filter_by(model.id.in_(uids)).all()
    ret = {}
    for item in data:
        ret[item.id] = item
    return ret


def _attach_user(item, user):
    item.user = user
    return item

def _attach_node(item, node):
    item.node = node
    return item


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
            node.topic_count += 1
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
            node.topic_count -= 1
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
