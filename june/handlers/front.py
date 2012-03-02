import hashlib
from tornado.escape import utf8
from june.lib.handler import BaseHandler
from june.lib.decorators import require_user
from june.models import Node, Topic, Reply
from june.models import MemberMixin, NodeMixin


class HomeHandler(BaseHandler, MemberMixin, NodeMixin):
    def get(self):
        topics = Topic.query.order_by('-impact')[:20]
        user_ids = [topic.user_id for topic in topics]
        users = self.get_users(user_ids)
        nodes = self.get_nodes()
        self.render('home.html', topics=topics, users=users, nodes=nodes)


class NodeHandler(BaseHandler):
    def get(self, slug):
        node = Node.query.filter_by(slug=slug).first()
        if not node:
            self.send_error(404)
            return
        self.render('node.html', node=node)


class CreateTopicHandler(BaseHandler):
    @require_user
    def get(self, slug):
        node = Node.query.filter_by(slug=slug).first()
        if not node:
            self.send_error(404)
            return
        self.render('topic_form.html', node=node, topic=None)

    @require_user
    def post(self, slug):
        node = self.db.query(Node).filter_by(slug=slug).first()
        if not node:
            self.send_error(404)
            return
        title = self.get_argument('title', None)
        content = self.get_argument('content', None)
        if not (title and content):
            self.render('topic_form.html', message='Please Fill the form')
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
        self.redirect(url)


class TopicHandler(BaseHandler, MemberMixin):
    def get(self, id):
        topic = Topic.query.filter_by(id=id).first()
        if not topic:
            self.send_error(404)
            return
        node = Node.query.filter_by(id=id).first()
        replies = Reply.query.filter_by(topic_id=id).all()
        user_ids = [o.user_id for o in replies]
        user_ids.append(topic.user_id)
        users = self.get_users(user_ids)
        html = self.render_string(
            'snippet/topic.html', topic=topic,
            node=node, replies=replies, users=users)
        if self.is_ajax():
            self.write(html)
            return
        self.render('topic.html', topic=topic, html=html)

    @require_user
    def post(self, id):
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

        reply = Reply(content=content)
        reply.topic_id = id
        reply.user_id = self.current_user.id
        topic.reply_count += 1
        topic.impact += self.current_user.reputation
        self.db.add(reply)
        self.db.add(topic)
        self.db.commit()
        url = '/topic/%s' % id
        self.cache.set(key, url, 100)
        self.redirect(url)


handlers = [
    ('/', HomeHandler),
    ('/node/(\w+)', NodeHandler),
    ('/node/(\w+)/topic', CreateTopicHandler),
    ('/topic/(\d+)', TopicHandler),
]
