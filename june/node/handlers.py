import datetime
import tornado.web
from tornado.web import UIModule
from july import JulyHandler, JulyApp
from june.account.lib import UserHandler
from june.topic.models import Topic
from models import FollowNode, Node


class FollowNodeHandler(UserHandler):
    @tornado.web.authenticated
    def get(self, slug):
        node = self.get_node_by_slug(slug)
        if not node:
            self.send_error(404)
            return
        self.follow_node(node.id)
        self.db.commit()
        self.redirect('/node/%s' % node.slug)


class UnfollowNodeHandler(UserHandler):
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
        key1 = 'TopicListModule:%s:1:-impact' % self.current_user.id
        key2 = 'follownode:%s' % self.current_user.id
        key3 = 'FollowedNodesModule:%s' % self.current_user.id
        self.cache.delete_multi([key1, key2, key3])
        self.redirect('/node/%s' % node.slug)


class NodeListHandler(UserHandler):
    def head(self):
        pass

    def get(self):
        nodes = Node.query.order_by('-updated').all()
        self.render('node_list.html', nodes=nodes)


class NodeFeedHandler(JulyHandler):
    def get(self, slug):
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        node = self.get_node_by_slug(slug)
        if not node:
            self.send_error(404)
            return
        html = self.cache.get('nodefeed:%s' % str(slug))
        if html is not None:
            self.write(html)
            return
        topics = Topic.query.filter_by(node_id=node.id).order_by('-id')[:20]
        user_ids = (topic.user_id for topic in topics)
        users = self.get_users(user_ids)
        now = datetime.datetime.utcnow()
        html = self.render_string('feed.xml', topics=topics, users=users,
                                  node=node, now=now)
        self.cache.set('nodefeed:%s' % str(slug), html, 3600)
        self.write(html)


app_handlers = [
    ('/(\w+)/follow', FollowNodeHandler),
    ('/(\w+)/unfollow', UnfollowNodeHandler),
    ('/(\w+)/feed', NodeFeedHandler),
]


class FollowingNodes(UIModule):
    def render(self, user_id):
        fs = FollowNode.query.filter_by(user_id=user_id).values('node_id')
        node_ids = (f[0] for f in fs)
        nodes = Node.query.filter_by(id__in=node_ids).all()
        return self.render_string('module/node_list.html', nodes=nodes)


class RecentAddNodes(UIModule):
    def render(self):
        nodes = Node.query.order_by('-id')[:20]
        return self.render_string('module/node_list.html', nodes=nodes)


app_modules = {
    'FollowingNodes': FollowingNodes,
    'RecentAddNodes': RecentAddNodes,
}

node_app = JulyApp('node', __name__, handlers=app_handlers,
                   ui_modules=app_modules)
