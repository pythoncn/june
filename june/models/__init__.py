# coding: utf-8
# flake8: noqa

from ._base import *
from .account import *
from .node import *
from .topic import *
from flask.ext.sqlalchemy import models_committed


def fill_topics(items, user=None, node=None):
    if user:
        items = map(lambda o: _attach_user(o, user), items)
    else:
        items = fill_with_users(items)
    if node:
        items = map(lambda o: _attach_node(o, node), items)
    else:
        items = fill_with_nodes(items)
    return items


def fill_with_users(items):
    uids = set(map(lambda o: o.account_id, items))
    users = Account.query.filter_in(Account.id, uids)
    items = map(lambda o: _attach_user(o, users.get(o.account_id)), items)
    return items


def fill_with_nodes(items):
    uids = set(map(lambda o: o.node_id, items))
    nodes = Node.query.filter_in(Node.id, uids)
    items = map(lambda o: _attach_node(o, nodes[o.node_id]), items)
    return items


def get_by_ids(model, uids):
    if not len(uids):
        return {}

    if len(uids) == 1:
        data = model.query.get(uids.pop())
        return {data.id: data}

    data = model.query.filter(model.id.in_(uids)).all()
    ret = {}
    for item in data:
        ret[item.id] = item
    return ret


def get_site_status():
    account, node, topic, reply = cache.get_many(
        'status-account', 'status-node', 'status-topic', 'status-reply'
    )
    if not account:
        account = Account.query.count()
        cache.set('status-account', account)
    if not node:
        node = Node.query.count()
        cache.set('status-node', node)
    if not topic:
        topic = Topic.query.count()
        cache.set('status-topic', topic)
    if not reply:
        reply = Reply.query.count()
        cache.set('status-reply', reply)
    return dict(
        account=account,
        node=node,
        topic=topic,
        reply=reply,
    )


def _attach_user(item, user):
    if not user:
        item.user = NonAccount()
    else:
        item.user = user
    return item


def _attach_node(item, node):
    item.node = node
    return item


def _clear_cache(sender, changes):
    for model, operation in changes:
        if isinstance(model, Account) and operation != 'update':
            cache.delete('status-account')
        if isinstance(model, Node) and operation != 'update':
            cache.delete('status-node')
        if isinstance(model, Topic) and operation != 'update':
            cache.delete('status-topic')
        if isinstance(model, Reply) and operation != 'update':
            cache.delete('status-reply')


models_committed.connect(_clear_cache)
