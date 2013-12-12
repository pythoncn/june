# coding: utf-8

from datetime import datetime
from ._base import db
from .account import Account
from .node import Node, NodeStatus


__all__ = ['Topic', 'Reply', 'LikeTopic']


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, nullable=False, index=True)
    node_id = db.Column(db.Integer, nullable=False, index=True)

    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)

    hits = db.Column(db.Integer, default=0)
    reply_count = db.Column(db.Integer, default=0)

    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        index=True,
    )

    def __str__(self):
        return self.title

    def __repr__(self):
        return '<Topic: %s>' % self.id

    def save(self, user=None, node=None):
        if self.id:
            # update topic
            db.session.add(self)
            db.session.commit()
            return self

        # insert a topic
        if user:
            self.account_id = user.id
            user.active = datetime.utcnow()
            db.session.add(user)
        if node:
            self.node_id = node.id
            node.topic_count += 1
            db.session.add(node)

            ns = NodeStatus.query.filter_by(
                node_id=self.node_id, account_id=self.account_id
            ).first()
            if not ns:
                ns = NodeStatus(
                    node_id=self.node_id,
                    account_id=self.account_id,
                    topic_count=0,
                )
            ns.topic_count += 1
            db.session.add(ns)

        db.session.add(self)
        db.session.commit()
        return self

    def move(self, node=None):
        if self.node_id == node.id:
            return self

        # clear status in pre node
        node1 = Node.query.get(self.node_id)
        node1.topic_count -= 1
        db.session.add(node1)

        ns1 = NodeStatus.query.filter_by(
            node_id=self.node_id, account_id=self.account_id
        ).first()
        ns1.topic_count -= 1
        db.session.add(ns1)

        # increase status in post node
        node.topic_count += 1
        db.session.add(node)
        ns = NodeStatus.query.filter_by(
            node_id=node.id, account_id=self.account_id
        ).first()
        if not ns:
            ns = NodeStatus(
                node_id=node.id,
                account_id=self.account_id,
                topic_count=0,
            )
        ns.topic_count += 1
        db.session.add(ns)

        self.node_id = node.id
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self, user=None, node=None):
        if not user:
            user = Account.query.get(self.account_id)
        if not node:
            node = Node.query.get(self.node_id)

        user.active = datetime.utcnow()
        db.session.add(user)

        node.topic_count -= 1
        db.session.add(node)

        ns = NodeStatus.query.filter_by(
            node_id=self.node_id, account_id=self.account_id
        ).first()
        if ns and ns.topic_count:
            ns.topic_count -= 1
            db.session.add(ns)
        db.session.delete(self)
        db.session.commit()
        return self


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, nullable=False)
    topic_id = db.Column(db.Integer, index=True, nullable=False)
    content = db.Column(db.Text)

    created = db.Column(db.DateTime, default=datetime.utcnow)
    flags = db.Column(db.Integer, default=0)

    def __str__(self):
        return self.content

    def save(self, user=None, topic=None):
        if self.id:
            # update
            db.session.add(self)
            db.session.commit()
            return self

        if user:
            self.account_id = user.id
            user.active = datetime.utcnow()
            db.session.add(user)
        if topic:
            self.topic_id = topic.id
            topic.reply_count += 1
            topic.updated = datetime.utcnow()
            db.session.add(topic)

        db.session.add(self)
        db.session.commit()
        return self

    def delete(self, user=None, topic=None):
        if not topic:
            topic = Topic.query.get(self.topic_id)

        topic.reply_count -= 1
        db.session.add(topic)
        db.session.delete(self)
        db.session.commit()
        return self


class LikeTopic(db.Model):
    __table_args__ = (
        db.UniqueConstraint(
            'account_id', 'topic_id', name='uc_account_like_topic'
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, nullable=False)
    topic_id = db.Column(db.Integer, index=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
