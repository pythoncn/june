import tornado.web
from june.lib.handler import BaseHandler
from june.lib.util import ObjectDict
from june.models import Node, Topic
from june.models import NodeMixin
from june.filters import safe_markdown


class HomeHandler(BaseHandler, NodeMixin):
    def get(self):
        topics = Topic.query.order_by('-impact')[:20]
        user_ids = []
        node_ids = []
        for topic in topics:
            user_ids.append(topic.user_id)
            node_ids.append(topic.node_id)
        users = self.get_users(user_ids)
        nodes = self.get_nodes(node_ids)
        self.render('home.html', topics=topics, users=users, nodes=nodes)


class StreamHandler(BaseHandler, NodeMixin):
    def get(self):
        if not self.current_user:
            self.redirect('/')
            return
        node_ids = self.get_user_follow_nodes(self.current_user.id)
        if not node_ids:
            msg = ObjectDict(header='Notify',
                             body='You need follow some nodes')
            self._context.message.append(msg)
            self.render('home.html', topics=[], users={}, nodes={})
            return
        nodes = self.get_nodes(node_ids)
        q = Topic.query.filter_by(node_id__in=set(node_ids))
        topics = q.order_by('-impact')[:20]
        user_ids = [topic.user_id for topic in topics]
        users = self.get_users(user_ids)
        self.render('home.html', topics=topics, users=users, nodes=nodes)


class NodeHandler(BaseHandler, NodeMixin):
    def get(self, slug):
        node = self.get_node_by_slug(slug)
        if not node:
            self.send_error(404)
            return
        q = Topic.query.filter_by(node_id=node.id)
        topics = q.order_by('-impact')[:20]
        user_ids = (topic.user_id for topic in topics)
        users = self.get_users(user_ids)
        if self.current_user:
            is_following = self.is_user_follow_node(
                self.current_user.id, node.id)
        else:
            is_following = False
        self.render('node.html', node=node, topics=topics,
                    users=users, is_following=is_following)


class FollowNodeHandler(BaseHandler, NodeMixin):
    @tornado.web.authenticated
    def get(self, slug):
        node = self.get_node_by_slug(slug)
        if not node:
            self.send_error(404)
            return
        self.follow_node(node.id)
        self.db.commit()
        self.redirect('/node/%s' % node.slug)


class UnfollowNodeHandler(BaseHandler, NodeMixin):
    @tornado.web.authenticated
    def get(self, slug):
        node = self.get_node_by_slug(slug)
        if not node:
            self.send_error(404)
            return
        sql = 'delete from follownode where user_id=%s and node_id=%s' % \
                (self.current_user.id, node.id)
        self.db.execute(sql)
        self.db.commit()
        self.cache.delete('follownode:%s' % self.current_user.id)
        self.redirect('/node/%s' % node.slug)


class NodeListHandler(BaseHandler, NodeMixin):
    def get(self):
        nodes = Node.query.all()
        self.render('node_list.html', nodes=nodes)


class PreviewHandler(BaseHandler):
    def post(self):
        text = self.get_argument('text', '')
        self.write(safe_markdown(text))


handlers = [
    ('/', HomeHandler),
    ('/stream', StreamHandler),
    ('/nodes', NodeListHandler),
    ('/node/(\w+)', NodeHandler),
    ('/node/(\w+)/follow', FollowNodeHandler),
    ('/node/(\w+)/unfollow', UnfollowNodeHandler),
    ('/preview', PreviewHandler),
]
