import datetime
import tornado.web
from june.lib.handler import BaseHandler
from june.models import Topic, Member, Node
from june.models import NodeMixin
from june.filters import safe_markdown


class HomeHandler(BaseHandler, NodeMixin):
    def head(self):
        pass

    def get(self):
        # recent join
        members = Member.query.order_by('-id')[:5]
        self.render('home.html', members=members)


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


handlers = [
    ('/', HomeHandler),
    ('/subscription', SubscriptionHandler),
    ('/preview', PreviewHandler),
    ('/feed', SiteFeedHandler),
]


class SystemStatusModule(tornado.web.UIModule):
    def render(self):
        status = self.handler.cache.get('ui$status')
        if status is None:
            status = {}
            status['node'] = Node.query.count()
            status['topic'] = Topic.query.count()
            status['member'] = Member.query.count()
            self.handler.cache.set('ui$status', status, 600)
        _ = self.handler.locale.translate
        html = '%s:%s %s:%s %s:%s' % (
            _("Node"), status['node'], _("Topic"), status['topic'],
            _("Member"), status['member'])
        return html


ui_modules = {
    'SystemStatusModule': SystemStatusModule,
}
