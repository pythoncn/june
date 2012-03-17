import hashlib
import math
from datetime import datetime
from tornado.escape import utf8
from tornado.options import options
from tornado.web import UIModule
from june.lib.handler import BaseHandler
from june.lib.decorators import require_user
from june.lib.util import ObjectDict, PageMixin
from june.lib.filters import find_mention
from june.models import Node, Topic, Reply
from june.models import NodeMixin, TopicMixin, MemberMixin, NotifyMixin


class TopicHandler(BaseHandler, TopicMixin, NodeMixin, PageMixin, NotifyMixin):
    def head(self, id):
        pass

    def get(self, id):
        key = 'hit$topic:%s' % str(id)
        count = self.cache.get(key)
        if count is None:
            count = 1
            self.cache.set(key, 1)
        else:
            self.cache.incr(key)
        if count > 10:
            topic = self.db.query(Topic).filter_by(id=id).first()
            if not topic:
                self.send_error(404)
                return
            topic.hits += 10
            topic.impact += 1000
            self.db.add(topic)
            self.db.commit()
            self.cache.set(key, 1)
            self.cache.delete('topic:%s' % str(id))
        else:
            topic = self.get_topic_by_id(id)
            # topic.hits = topic.hits + count
            # don't change hits, server answer 304, reduce bandwidth
            if not topic:
                self.send_error(404)
                return

        node = self.get_node_by_id(topic.node_id)
        topic.creator = self.get_user_by_id(topic.user_id)
        self.render('topic.html', topic=topic, node=node)

    @require_user
    def post(self, id):
        # for topic reply
        content = self.get_argument('content', None)
        if not content:
            self.redirect('/topic/%s' % id)
            return

        topic = self.db.query(Topic).filter_by(id=id).first()
        if not topic:
            self.send_error(404)
            return

        key = hashlib.md5(utf8(content)).hexdigest()
        url = self.cache.get(key)
        # avoid double submit
        if url:
            self.redirect(url)
            return

        reply = Reply(topic_id=id, user_id=self.current_user.id,
                      content=content)

        # impact on topic
        topic.reply_count += 1
        topic.impact += self._calc_impact(topic)

        #TODO impact on creator

        self.db.add(reply)
        self.db.add(topic)

        # notifications
        self.create_notify(topic.user_id, topic, content)
        for username in set(find_mention(content)):
            self.create_mention(username, topic, content)

        self.db.commit()
        url = '/topic/%s' % str(id)
        self.cache.set(key, url, 100)
        #TODO calculate page, delete the right cache
        self.cache.delete('ReplyListModule:%s:1' % str(id))
        self.redirect(url)

    def _calc_impact(self, topic):
        if self.current_user.reputation < 2:
            return 0
        factor = int(options.reply_factor_for_topic)
        time_factor = int(options.reply_time_factor)
        time = datetime.utcnow() - topic.created
        factor += time.days * time_factor
        return factor * int(math.log(self.current_user.reputation))


class NewTopicHandler(BaseHandler, NodeMixin):
    @require_user
    def get(self):
        nodes = self.get_all_nodes()
        self.render("new_topic.html", nodes=nodes)


class CreateTopicHandler(BaseHandler, NodeMixin):
    @require_user
    def get(self, slug):
        node = self.get_node_by_slug(slug)
        if not node:
            self.send_error(404)
            return
        if not self._check_permission(node):
            self.create_message(
                'Warning',
                "You have no permission to create a topic in this node")
            self.render('topic_form.html', topic=None, node=node)
            return
        self.render('topic_form.html', topic=None, node=node)

    @require_user
    def post(self, slug):
        node = self.db.query(Node).filter_by(slug=slug).first()
        if not node:
            self.send_error(404)
            return
        title = self.get_argument('title', None)
        content = self.get_argument('content', None)
        if not (title and content):
            self.create_message('Form Error', 'Please fill the required field')
            self.render('topic_form.html', topic=None, node=node)
            return
        if not self._check_permission(node):
            self.create_message(
                'Warning',
                "You have no permission to create a topic in this node")
            self.render('topic_form.html', topic=None, node=node)
            return

        key = hashlib.md5(utf8(content)).hexdigest()
        url = self.cache.get(key)
        # avoid double submit
        if url:
            self.redirect(url)
            return
        topic = Topic(title=title, content=content)
        topic.node_id = node.id
        topic.user_id = self.current_user.id
        node.topic_count += 1
        self.db.add(topic)
        self.db.add(node)
        self.db.commit()
        url = '/topic/%d' % topic.id
        self.cache.set(key, url, 100)
        key1 = 'TopicListModule:0:1:-impact'
        key2 = 'NodeTopicsModule:%s:1:-impact' % node.id
        key3 = 'UserTopicsModule:%s:1:-impact' % self.current_user.id
        self.cache.delete_multi(['status', key1, key2, key3])
        self.redirect(url)

    def _check_permission(self, node):
        user = self.current_user
        if user.role > 9:
            return True
        if user.reputation < node.limit_reputation:
            return False
        return user.role >= node.limit_role


class EditTopicHandler(BaseHandler, TopicMixin, NodeMixin):
    @require_user
    def get(self, id):
        topic = self.get_topic_by_id(id)
        if not topic:
            self.send_error(404)
            return
        if not self._check_permission(topic):
            self.send_error(403)
            return
        node = self.get_node_by_id(topic.node_id)
        self.render('topic_form.html', topic=topic, node=node)

    @require_user
    def post(self, id):
        topic = self.db.query(Topic).filter_by(id=id).first()
        if not topic:
            self.send_error(404)
            return
        if self._check_permission(topic) != 1:
            self.redirect('/topic/%s' % id)
            return

        title = self.get_argument('title', None)
        content = self.get_argument('content', None)
        if not (title and content):
            self.create_message('Form Error', 'Please fill the required field')
            self.render('topic_form.html')
            return
        topic.title = title
        topic.content = content
        self.db.add(topic)
        self.db.commit()
        self.cache.delete('topic:%s' % topic.id)
        self.redirect('/topic/%s' % topic.id)

    def _check_permission(self, topic):
        if self.current_user.role > 9:
            return 1
        if not self.is_owner_of(topic):
            self.send_error(403)
            return 0
        timedel = datetime.utcnow() - topic.created
        if timedel.days:
            # user can only edit a topic in 10 minutes
            self.create_message('Warning', "You can't edit this topic now")
            return 2
        return 1


handlers = [
    ('/node/(\w+)/topic', CreateTopicHandler),
    ('/topic', NewTopicHandler),
    ('/topic/(\d+)', TopicHandler),
    ('/topic/(\d+)/edit', EditTopicHandler),
]


class ReplyListModule(UIModule, PageMixin, MemberMixin):
    def render(self, topic, tpl='module/reply_list.html'):
        p = self._get_page()
        key = 'ReplyListModule:%s:%s' % (topic.id, p)
        html = self.handler.cache.get(key)
        if html is not None:
            return html
        page = self._get_pagination(
            Reply.query.filter_by(topic_id=topic.id),
            perpage=30)
        page = ObjectDict(page)
        user_ids = [o.user_id for o in page.datalist]
        users = self.get_users(user_ids)
        html = self.render_string(tpl, page=page, users=users)
        self.handler.cache.set(key, html, 600)
        return html


class TopicListModule(UIModule, MemberMixin, NodeMixin, PageMixin):
    def render(self, user_id=0, tpl='module/topic_list.html'):
        order = self._get_order()
        p = self._get_page()
        key = 'TopicListModule:%s:%s:%s' % (user_id, p, order)
        html = self.handler.cache.get(key)
        if html is not None:
            return html

        if user_id:
            node_ids = self.get_user_follow_nodes(self.current_user.id)
            if not node_ids:
                msg = self.handler.locale.translate(
                    "You need follow some nodes")
                return '<div class="cell">%s</div>' % msg

            if len(node_ids) == 1:
                # for better performance
                q = Topic.query.filter_by(node_id=node_ids[0]).order_by(order)
            else:
                q = Topic.query.filter_by(node_id__in=set(node_ids))\
                        .order_by(order)
        else:
            q = Topic.query.order_by(self._get_order())

        page = ObjectDict(self._get_pagination(q))

        user_ids = []
        node_ids = []
        for topic in page.datalist:
            user_ids.append(topic.user_id)
            node_ids.append(topic.node_id)
        users = self.get_users(user_ids)
        nodes = self.get_nodes(node_ids)
        html = self.render_string(tpl, page=page, users=users, nodes=nodes)
        self.handler.cache.set(key, html, 60)
        return html


class NodeTopicsModule(UIModule, MemberMixin, PageMixin):
    def render(self, node_id, tpl='module/topic_list.html'):
        order = self._get_order()
        p = self._get_page()
        key = 'NodeTopicsModule:%s:%s:%s' % (node_id, p, order)
        html = self.handler.cache.get(key)
        if html is not None:
            return html

        q = Topic.query.filter_by(node_id=node_id).order_by(order)
        page = ObjectDict(self._get_pagination(q))

        user_ids = []
        for topic in page.datalist:
            user_ids.append(topic.user_id)
        users = self.get_users(user_ids)
        html = self.render_string(tpl, page=page, users=users, nodes=None)
        self.handler.cache.set(key, html, 600)
        return html


class UserTopicsModule(UIModule, NodeMixin, PageMixin):
    def render(self, user_id, tpl='module/user_topic_list.html'):
        order = self._get_order()
        p = self._get_page()
        key = 'UserTopicsModule:%s:%s:%s' % (user_id, p, order)
        html = self.handler.cache.get(key)
        if html is not None:
            return html

        q = Topic.query.filter_by(user_id=user_id).order_by(order)
        page = ObjectDict(self._get_pagination(q))
        nodes = self.get_nodes((topic.node_id for topic in page.datalist))
        html = self.render_string(tpl, page=page, nodes=nodes)
        self.handler.cache.set(key, html, 600)
        return html


ui_modules = {
    'ReplyListModule': ReplyListModule,
    'TopicListModule': TopicListModule,
    'NodeTopicsModule': NodeTopicsModule,
    'UserTopicsModule': UserTopicsModule,
}
