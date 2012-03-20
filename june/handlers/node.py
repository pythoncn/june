import datetime
import tornado.web
from june.lib.handler import BaseHandler
from june.lib.util import PageMixin
from june.models import Topic, FollowNode
from june.models.mixin import NodeMixin, MemberMixin


class NodeHandler(BaseHandler, NodeMixin, PageMixin):
    def head(self, slug):
        pass

    def get(self, slug):
        node = self.get_node_by_slug(slug)
        if not node:
            self.send_error(404)
            return

        if self.current_user:
            is_following = self.is_user_follow_node(
                self.current_user.id, node.id)
        else:
            is_following = False
        self.render('node.html', node=node, is_following=is_following)


class FollowNodeHandler(BaseHandler, NodeMixin):
    @tornado.web.authenticated
    def get(self, slug):
        node = self.get_node_by_slug(slug)
        if not node:
            self.send_error(404)
            return
        self.follow_node(node.id)
        self.db.commit()
        key1 = 'TopicListModule:%s:1:-impact' % self.current_user.id
        key2 = 'follownode:%s' % self.current_user.id
        key3 = 'FollowedNodesModule:%s' % self.current_user.id
        self.cache.delete_multi([key1, key2, key3])
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
        key1 = 'TopicListModule:%s:1:-impact' % self.current_user.id
        key2 = 'follownode:%s' % self.current_user.id
        key3 = 'FollowedNodesModule:%s' % self.current_user.id
        self.cache.delete_multi([key1, key2, key3])
        self.redirect('/node/%s' % node.slug)


class NodeListHandler(BaseHandler, NodeMixin):
    def head(self):
        pass

    def get(self):
        nodes = self.get_all_nodes()
        self.render('node_list.html', nodes=nodes)


class NodeFeedHandler(BaseHandler, NodeMixin):
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


handlers = [
    ('/nodes', NodeListHandler),
    ('/node/(\w+)', NodeHandler),
    ('/node/(\w+)/follow', FollowNodeHandler),
    ('/node/(\w+)/unfollow', UnfollowNodeHandler),
    ('/node/(\w+)/feed', NodeFeedHandler),
]


class FollowedNodesModule(tornado.web.UIModule, NodeMixin):
    def render(self, user_id, tpl="module/node_list.html"):
        #TODO: node_list tpl
        key = 'FollowedNodesModule:%s' % str(user_id)
        html = self.handler.cache.get(key)
        if html is not None:
            return html
        node_ids = self.get_user_follow_nodes(user_id)
        if not node_ids:
            return ''
        nodes = self.get_nodes(node_ids)
        html = self.render_string(tpl, nodes=nodes.itervalues())
        self.handler.cache.set(key, html, 600)
        return html


class NodeFollowersModule(tornado.web.UIModule, MemberMixin):
    def render(self, node_id, tpl='module/member_list.html'):
        key = 'NodeFollowersModule:%s' % node_id
        html = self.handler.cache.get(key)
        if html is not None:
            return html
        q = FollowNode.query.filter_by(node_id=node_id).limit(5)\
                .values('user_id')
        #TODO limit number
        user_ids = (values[0] for values in q)
        users = self.get_users(user_ids)
        html = self.render_string(tpl, users=users.itervalues())
        self.handler.cache.set(key, html, 600)
        return html


ui_modules = {
    'FollowedNodesModule': FollowedNodesModule,
    'NodeFollowersModule': NodeFollowersModule,
}
