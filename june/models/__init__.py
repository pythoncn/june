# coding: utf-8
# flake8: noqa

from ._base import *
from .account import *
from .node import *
from .topic import *
import datetime

from flask.ext.sqlalchemy import models_committed

def _committed(model, operation):
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
