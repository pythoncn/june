import datetime
import tornado.web
from june.lib.handler import BaseHandler
from june.lib.util import ObjectDict, PageMixin
from june.models import Topic, Member
from june.models import NodeMixin
from june.filters import safe_markdown


class HomeHandler(BaseHandler, NodeMixin, PageMixin):
    def head(self):
        pass

    def get(self):
        key = 'homepage:%s:%s' % (self._get_order(), self._get_page())
        page = self.cache.get(key)
        if page is None:
            page = self._get_pagination(
                Topic.query.order_by(self._get_order()),
                self._context.status.topic)
            self.cache.set(key, page, 60)
        page = ObjectDict(page)
        user_ids = []
        node_ids = []
        for topic in page.datalist:
            user_ids.append(topic.user_id)
            node_ids.append(topic.node_id)
        users = self.get_users(user_ids)
        nodes = self.get_nodes(node_ids)
        # recent join
        members = Member.query.order_by('-id')[:5]
        self.render('home.html', page=page, users=users,
                    members=members, nodes=nodes)


class SubscriptionHandler(BaseHandler, NodeMixin, PageMixin):
    @tornado.web.authenticated
    def get(self):
        node_ids = self.get_user_follow_nodes(self.current_user.id)
        if not node_ids:
            msg = ObjectDict(header='Notify',
                             body='You need follow some nodes')
            self._context.message.append(msg)
            self.render('subscription.html', page=None, users={}, nodes={})
            return
        nodes = self.get_nodes(node_ids)
        key = 'subscription:%s:%s:%s' % (self._get_order(), self._get_page(),
                                  self.current_user.id)
        page = self.cache.get(key)
        if page is None:
            q = Topic.query.filter_by(node_id__in=set(node_ids))
            page = self._get_pagination(q.order_by(self._get_order()))
            self.cache.set(key, page, 60)
        page = ObjectDict(page)

        user_ids = (topic.user_id for topic in page.datalist)
        users = self.get_users(user_ids)
        self.render('subscription.html', page=page, users=users, nodes=nodes)


class SiteFeedHandler(BaseHandler):
    def get(self):
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        html = self.cache.get('sitefeed')
        if html is not None:
            self.write(html)
            return
        topics = Topic.query.order_by('-id')[:20]
        user_ids = (topic.user_id for topic in topics)
        users = self.get_users(user_ids)
        now = datetime.datetime.utcnow()
        html = self.render_string('feed.xml', topics=topics, users=users,
                                  node=None, now=now)
        self.cache.set('sitefeed', html, 600)
        self.write(html)


class PreviewHandler(BaseHandler):
    def post(self):
        text = self.get_argument('text', '')
        self.write(safe_markdown(text))


handlers = [
    ('/', HomeHandler),
    ('/subscription', SubscriptionHandler),
    ('/preview', PreviewHandler),
    ('/feed', SiteFeedHandler),
]
