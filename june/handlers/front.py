from june.lib.handler import BaseHandler
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


class NodeHandler(BaseHandler):
    def get(self, slug):
        node = Node.query.filter_by(slug=slug).first()
        if not node:
            self.send_error(404)
            return
        topics = Topic.query.order_by('-impact')[:20]
        user_ids = [topic.user_id for topic in topics]
        users = self.get_users(user_ids)
        self.render('node.html', node=node, topics=topics, users=users)


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
    ('/nodes', NodeListHandler),
    ('/node/(\w+)', NodeHandler),
    ('/preview', PreviewHandler),
]
