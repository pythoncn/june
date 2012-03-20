import datetime
import tornado.web
from june.lib.handler import BaseHandler
from june.lib.filters import safe_markdown
from june.models import Topic, Member, Node, Reply
from june.models.mixin import NodeMixin


class HomeHandler(BaseHandler, NodeMixin):
    def head(self):
        pass

    def get(self):
        # recent join
        self.render('home.html')


class SubscriptionHandler(BaseHandler, NodeMixin):
    @tornado.web.authenticated
    def get(self):
        self.render('subscription.html')


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
        self.cache.set('sitefeed', html, 1800)
        self.write(html)


class PreviewHandler(BaseHandler):
    def post(self):
        text = self.get_argument('text', '')
        self.write(safe_markdown(text))


class SearchHandler(BaseHandler):
    def get(self):
        query = self.get_argument('q', '')
        self.render('search.html', query=query)


handlers = [
    ('/', HomeHandler),
    ('/subscription', SubscriptionHandler),
    ('/preview', PreviewHandler),
    ('/feed', SiteFeedHandler),
    ('/search', SearchHandler),
]


class SystemStatusModule(tornado.web.UIModule):
    def render(self, tpl="module/status.html"):
        status = self.handler.cache.get('status')
        if status is None:
            status = {}
            status['node'] = Node.query.count()
            status['topic'] = Topic.query.count()
            status['member'] = Member.query.count()
            status['reply'] = Reply.query.count()
            self.handler.cache.set('status', status, 600)
        return self.render_string(tpl, status=status)


ui_modules = {
    'SystemStatusModule': SystemStatusModule,
}
