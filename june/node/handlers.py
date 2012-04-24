import datetime
import tornado.web
from july import JulyHandler
from june.account.lib import UserHandler
from june.topic.models import Topic


class NodeHandler(UserHandler):
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
        nodes = self.get_all_nodes()
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


handlers = [
    #('/all', NodeListHandler),
    ('/(\w+)', NodeHandler),
    ('/(\w+)/follow', FollowNodeHandler),
    ('/(\w+)/unfollow', UnfollowNodeHandler),
    ('/(\w+)/feed', NodeFeedHandler),
]
