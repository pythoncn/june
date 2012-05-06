import os.path
import hashlib
import tornado.web
from tornado.options import options
from july import JulyHandler
from july.util import import_object
from july.cache import cache
from july.database import db
from june.account.lib import UserHandler
from june.account.models import Member
from june.account.decorators import require_user
#from june.node.models import Node
from june.topic.models import Topic
from june.util import safe_markdown, emoji


class HomeHandler(UserHandler):
    def head(self):
        pass

    def get(self):
        members = Member.query.order_by('-id')[:5]
        topics = Topic.query.order_by('-impact')[:20]
        self.render('home.html', members=members, topics=topics)


class SubscriptionHandler(UserHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('subscription.html')


class SiteFeedHandler(JulyHandler):
    def get_template_path(self):
        return os.path.join(os.path.dirname(__file__), '_templates')

    def get(self):
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        html = cache.get('sitefeed')
        if html is not None:
            self.write(html)
            return
        topics = Topic.query.order_by('-id')[:20]
        #user_ids = (topic.user_id for topic in topics)
        #users = self.get_users(user_ids)
        html = self.render_string('feed.xml', topics=topics, node=None)
        cache.set('sitefeed', html, 1800)
        self.write(html)


class PreviewHandler(UserHandler):
    def post(self):
        text = self.get_argument('text', '')
        self.write(emoji(safe_markdown(text)))


class SearchHandler(UserHandler):
    def get(self):
        query = self.get_argument('q', '')
        self.render('search.html', query=query)


class UploadHandler(UserHandler):
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
