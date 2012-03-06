"""
Member:
    only the basic info of a user

    role:
        staff > 6
        admin > 9
        active > 1
        not verified email = 1
        deactive < 1

    reputation:
        reputation means the value of a member, it affects in topic and
        everything

        1. when user's topic is up voted, reputation increase:
            + n1 * log(user.reputation)

        2. when user's topic is down voted, reputation decrease:
            - n2 * log(user.reputation)


Topic:
    topic must be in a node

    impact:
        for sorting topic

        1. when user reply a topic, impact increase:
            + (n1 + day_del * n2) * log(user.reputation)

        2. when user up vote a topic, impact increase:
            + n3 * log(user.reputation)

        3. when user down vote a topic, impact decrease:
            - n4 * log(user.reputation)

"""

import time
import hashlib
from random import choice
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, Text
from tornado.options import options
from june.config import db
from june.lib.decorators import cache
from june.lib.util import ObjectDict


def get_current_impact():
    return int(time.time())


def create_token(length=16):
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    salt = ''.join([choice(chars) for i in range(length)])
    return salt


def get_cache_list(cache, model, id_list, key_prefix, time=600):
    if not id_list:
        return {}
    id_list = set(id_list)
    data = cache.get_multi(id_list, key_prefix=key_prefix)
    missing = id_list - set(data)
    if missing:
        dct = {}
        for item in model.query.filter_by(id__in=missing).all():
            dct[item.id] = item

        cache.set_multi(dct, time=time, key_prefix=key_prefix)
        data.update(dct)

    return data


class Member(db.Model):
    username = Column(String(100), unique=True, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password = Column(String(100), nullable=False)
    avatar = Column(String(400))
    website = Column(String(400))

    role = Column(Integer, default=2)
    reputation = Column(Integer, default=10)
    token = Column(String(16))
    created = Column(DateTime, default=datetime.utcnow)
    last_notify = Column(DateTime, default=datetime.utcnow)

    def __init__(self, email, **kwargs):
        self.email = email.lower()
        self.token = create_token(16)
        if 'username' not in kwargs:
            self.username = self.email.split('@')[0].lower()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_avatar(self, size=48):
        if self.avatar:
            return self.avatar
        md5email = hashlib.md5(self.email).hexdigest()
        url = "http://www.gravatar.com/avatar/%s?s=%s&d=%s"
        if hasattr(options, 'gravatar_secure'):
            url = "https://secure.gravatar.com/avatar/%s?s=%s&d=%s"

        d = ''
        if hasattr(options, 'default_gravatar'):
            d = options.default_gravatar

        return url % (md5email, size, d)

    @staticmethod
    def create_password(raw):
        salt = create_token(8)
        hsh = hashlib.sha1(salt + raw + options.password_secret).hexdigest()
        return "%s$%s" % (salt, hsh)

    def check_password(self, raw):
        salt, hsh = self.password.split('$')
        verify = hashlib.sha1(salt + raw + options.password_secret).hexdigest()
        return verify == hsh


class MemberLog(db.Model):
    user_id = Column(Integer, nullable=False, index=True)
    message = Column(String(100))
    time = Column(DateTime, default=datetime.utcnow)
    ip = Column(String(100))


class MemberMixin(object):
    @cache('member', 600)
    def get_user_by_id(self, id):
        return Member.query.filter_by(id=id).first()

    @cache("member", 600)
    def get_user_by_name(self, name):
        return Member.query.filter_by(username=name).first()

    def get_users(self, id_list):
        return get_cache_list(self.cache, Member, id_list, 'member:')

    def create_user(self, email):
        username = email.split('@')[0].lower()
        member = self.get_user_by_name(username)
        if member:
            username = username + create_token(5)
            user = Member(email, username=username)
        else:
            user = Member(email)
        return user


class Notify(db.Model):
    sender = Column(Integer, nullable=False)
    receiver = Column(Integer, nullable=False, index=True)
    content = Column(String(400))
    label = Column(String(200))
    link = Column(String(400))
    type = Column(String(20), default='reply')
    created = Column(DateTime, default=datetime.utcnow)


class NotifyMixin(object):
    def get_system_status(self):
        status = self.cache.get('status')
        if status is None:
            status = {}
            status['member'] = Member.query.count()
            status['node'] = Node.query.count()
            status['topic'] = Topic.query.count()
            self.cache.set('status', status, 600)
        return ObjectDict(status)

    def create_notify(self, receiver, topic, content, type='reply'):
        if receiver == self.current_user.id:
            return
        link = '/topic/%s' % topic.id
        content = content[:200]
        notify = Notify(sender=self.current_user.id, receiver=receiver,
                         label=topic.title, link=link, content=content)
        notify.type = type
        self.db.add(notify)
        return notify

    def create_mention(self, username, topic, content):
        user = self.cache.get('member:%s' % str(username))
        if user is None:
            user = Member.query.filter_by(username=username).first()
            self.cache.set('member:%s' % str(username), user, 600)

        if user.id == self.current_user.id:
            return

        link = '/topic/%s' % topic.id
        content = content[:200]
        notify = Notify(
            sender=self.current_user.id, receiver=user.id,
            label=topic.title, link=link, content=content)
        notify.type = 'mention'
        self.db.add(notify)
        return notify

    def get_unread_notify(self, user):
        key = 'notify:%s' % user.id
        notify = self.cache.get(key)
        if notify:
            return notify
        q = Notify.query.filter_by(receiver=user.id)
        notify = q.filter_by(created__gt=user.last_notify).count()
        self.cache.set(key, notify, 600)
        return notify


class Node(db.Model):
    title = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False, index=True)
    avatar = Column(String(400))
    description = Column(String(1000))
    fgcolor = Column(String(40))
    bgcolor = Column(String(40))
    header = Column(String(2000))
    sidebar = Column(String(2000))
    footer = Column(String(2000))
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow,
                     onupdate=datetime.utcnow)
    limit_reputation = Column(Integer, default=0)
    limit_role = Column(Integer, default=0)
    topic_count = Column(Integer, default=0)


class FollowNode(db.Model):
    user_id = Column(Integer, nullable=False, index=True)
    node_id = Column(Integer, nullable=False, index=True)
    created = Column(DateTime, default=datetime.utcnow)


class NodeMixin(object):
    @cache('node', 600)
    def get_node_by_id(self, id):
        return Node.query.filter_by(id=id).first()

    @cache('node', 600)
    def get_node_by_slug(self, slug):
        return Node.query.filter_by(slug=slug).first()

    def get_nodes(self, id_list):
        return get_cache_list(self.cache, Node, id_list, 'node:')

    def follow_node(self, node_id):
        if not self.current_user:
            return 0
        nodes = self.get_user_follow_nodes(self.current_user.id)
        if node_id in nodes:
            return node_id
        nodes.append(node_id)
        user = self.current_user
        self.cache.set('follownode:%s' % user.id, nodes, 6000)
        f = FollowNode(user_id=user.id, node_id=node_id)
        self.db.add(f)
        return node_id

    @cache('follownode', 6000)
    def get_user_follow_nodes(self, user_id):
        q = FollowNode.query.filter_by(user_id=user_id).values('node_id')
        nodes = []
        for values in q:
            nodes.append(values[0])
        return nodes

    def is_user_follow_node(self, user_id, node_id):
        # should query again ?
        return node_id in self.get_user_follow_nodes(user_id)


class Topic(db.Model):
    node_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    title = Column(String(200))
    content = Column(Text)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow,
                      onupdate=datetime.utcnow)
    hits = Column(Integer, default=1)
    ups = Column(Text)  # e.g.  1,2,3,4
    downs = Column(Text)
    impact = Column(Integer, default=get_current_impact)
    reply_count = Column(Integer, default=0)

    @property
    def up_users(self):
        if not self.ups:
            return []
        return (int(i) for i in self.ups.split(','))

    @property
    def down_users(self):
        if not self.downs:
            return []
        return (int(i) for i in self.downs.split(','))


class TopicMixin(object):
    @cache('topic', 600)
    def get_topic_by_id(self, id):
        return Topic.query.filter_by(id=id).first()


class Reply(db.Model):
    topic_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    content = Column(String(2000))
    created = Column(DateTime, default=datetime.utcnow)

    ups = Column(Text)
    downs = Column(Text)

    @property
    def up_users(self):
        if not self.ups:
            return []
        return (int(i) for i in self.ups.split(','))

    @property
    def down_users(self):
        if not self.downs:
            return []
        return (int(i) for i in self.downs.split(','))
