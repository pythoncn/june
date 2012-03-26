import datetime
import hashlib
import tornado.web
from tornado.util import import_object
from tornado.options import options
from june.lib.handler import BaseHandler
from june.lib.filters import safe_markdown
from june.lib.decorators import require_user
from june.models import Topic, Member, Node, Reply
from june.models.mixin import NodeMixin


class HomeHandler(BaseHandler, NodeMixin):
    def head(self):
        pass

    def get(self):
        # recent join
        members = Member.query.order_by('-id').all()[:5]
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


class SearchHandler(BaseHandler):
    def get(self):
        query = self.get_argument('q', '')
        self.render('search.html', query=query)


class UploadHandler(BaseHandler):
    @require_user
    @tornado.web.asynchronous
    def post(self):
        image = self.request.files.get('image', None)
        if not image:
            self.write('{"stat": "fail", "msg": "no image"}')
            return
        image = image[0]
        content_type = image.get('content_type', '')
        if content_type not in ('image/png', 'image/jpeg'):
            self.write('{"stat": "fail", "msg": "filetype not supported"}')
            return
        body = image.get('body', '')
        filename = hashlib.md5(body).hexdigest()
        if content_type == 'image/png':
            filename += '.png'
        else:
            filename += '.jpg'

        backend = import_object(options.backend)()
        backend.save(body, filename, self._on_post)

    def _on_post(self, result):
        if result:
            self.write('{"stat":"ok", "url":"%s"}' % result)
        else:
            self.write('{"stat":"fail", "msg": "server error"}')
        self.finish()


handlers = [
    ('/', HomeHandler),
    ('/subscription', SubscriptionHandler),
    ('/preview', PreviewHandler),
    ('/feed', SiteFeedHandler),
    ('/search', SearchHandler),
    ('/upload', UploadHandler),
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
