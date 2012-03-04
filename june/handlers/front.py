from june.lib.handler import BaseHandler
from june.lib.decorators import require_user
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
        self.render('node.html', node=node, topics=topics, users=users)


class FollowNodeHandler(BaseHandler, NodeMixin):
    @require_user
    def get(self, slug):
        node = self.get_node_by_slug(slug)
        if not node:
            self.send_error(404)
            return
        self.follow_node(node.id)
        self.db.commit()
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
    ('/preview', PreviewHandler),
]
