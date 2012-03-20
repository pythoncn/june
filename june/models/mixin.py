from june.lib.decorators import cache
from june.models import create_token
from june.models import Member, Social, Notify
from june.models import Node, FollowNode
from june.models import Topic
from june.models import Storage


def get_cache_list(handler, model, id_list, key_prefix, time=600):
    if hasattr(handler, 'cache'):
        cache = handler.cache
    else:
        cache = handler.handler.cache
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


class MemberMixin(object):
    @cache('member', 600)
    def get_user_by_id(self, id):
        return Member.query.filter_by(id=id).first()

    @cache("member", 600)
    def get_user_by_name(self, name):
        return Member.query.filter_by(username=name).first()

    def get_users(self, id_list):
        return get_cache_list(self, Member, id_list, 'member:')

    def create_user(self, email):
        username = email.split('@')[0].lower()
        username = username.replace('.', '').replace('-', '')
        member = self.get_user_by_name(username)
        if member:
            username = username + create_token(5)
        user = Member(email, username=username)
        return user

    @cache('social', 6000)
    def get_user_social(self, user_id):
        dct = {}
        for net in Social.query.filter_by(user_id=user_id):
            dct[net.service] = {'token': net.token, 'enabled': net.enabled}
        return dct


class NotifyMixin(object):
    def create_notify(self, receiver, topic, content, type='reply'):
        if receiver == self.current_user.id:
            return
        link = '/topic/%s#reply-%s' % (topic.id, topic.reply_count)
        content = content[:200]
        notify = Notify(sender=self.current_user.id, receiver=receiver,
                         label=topic.title, link=link, content=content)
        notify.type = type
        self.db.add(notify)
        if not hasattr(self, 'cache'):
            self.cache = self.handler.cache
        self.cache.delete('notify:%s' % receiver)
        return notify

    def create_mention(self, username, topic, content):
        user = self.cache.get('member:%s' % str(username))
        if user is None:
            user = Member.query.filter_by(username=username).first()
            self.cache.set('member:%s' % str(username), user, 600)

        if not user:
            return

        if user.id == self.current_user.id:
            return

        if user.id == topic.user_id:
            #avoid double notify
            return

        link = '/topic/%s#reply-%s' % (topic.id, topic.reply_count)
        content = content[:200]
        notify = Notify(
            sender=self.current_user.id, receiver=user.id,
            label=topic.title, link=link, content=content)
        notify.type = 'mention'
        self.db.add(notify)

        if not hasattr(self, 'cache'):
            self.cache = self.handler.cache
        self.cache.delete('notify:%s' % user.id)
        return notify


class NodeMixin(object):
    @cache('node', 600)
    def get_node_by_id(self, id):
        return Node.query.filter_by(id=id).first()

    @cache('node', 600)
    def get_node_by_slug(self, slug):
        return Node.query.filter_by(slug=slug).first()

    @cache('allnodes', 600)
    def get_all_nodes(self):
        nodes = Node.query.all()
        nodes = sorted(nodes, key=lambda o: o.updated, reverse=True)
        return nodes

    def get_nodes(self, id_list):
        return get_cache_list(self, Node, id_list, 'node:')

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


class TopicMixin(object):
    @cache('topic', 600)
    def get_topic_by_id(self, id):
        return Topic.query.filter_by(id=id).first()


class StorageMixin(object):
    @cache('storage', 0)
    def get_storage(self, key):
        data = Storage.query.filter_by(key=key).first()
        if data:
            return data.value
        return None

    def set_storage(self, key, value):
        data = self.db.query(Storage).filter_by(key=key).first()
        if not data:
            data = Storage(key=key, value=value)
        else:
            data.value = value
            self.cache.delete('storage:%s' % key)
        self.db.add(data)
        return data
