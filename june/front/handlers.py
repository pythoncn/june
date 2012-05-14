import os.path
import hashlib
import tornado.web
from tornado.options import options
from july import JulyHandler
from july.util import import_object
from july.cache import cache
from june.account.lib import UserHandler
from june.account.decorators import require_user
from june.node.models import FollowNode, Node
from june.topic.models import Topic
from june.topic.lib import get_full_topics
from june.typo import markdown
from june.util import Pagination


class PageHandler(UserHandler):
    def get_page(self):
        page = self.get_argument('p', 1)
        try:
            page = int(page)
        except:
            return None
        if page < 0:
            return None
        return page


class LatestHandler(PageHandler):
    def head(self):
        pass

    def get(self):
        title = 'Latest'

        page = self.get_page()
        if not page:
            self.send_error(404)
            return
        total = Topic.query.count()
        perpage = 30

        p = Pagination(page, perpage, total)
        if p.page > p.page_count:
            self.send_error(404)
            return

        q = Topic.query.order_by('-last_reply_time')[p.start:p.end]
        p.datalist = get_full_topics(q)
        self.render('topic_list.html', title=title, pagination=p)


class PopularHandler(PageHandler):
    def head(self):
        pass

    def get(self):
        title = 'Popular'

        page = self.get_page()
        if not page:
            self.send_error(404)
            return
        total = Topic.query.count()
        perpage = 30

        p = Pagination(page, perpage, total)
        if p.page > p.page_count:
            self.send_error(404)
            return

        q = Topic.query.order_by('-impact')[p.start:p.end]
        p.datalist = get_full_topics(q)
        self.render('topic_list.html', title=title, pagination=p)


class FollowingHandler(PageHandler):
    @tornado.web.authenticated
    def get(self):
        title = 'Popular'

        page = self.get_page()
        if not page:
            self.send_error(404)
            return

        user_id = self.current_user.id
        fs = FollowNode.query.filter_by(user_id=user_id).values('node_id')
        node_ids = (f[0] for f in fs)
        q = Topic.query.filter_by(node_id__in=node_ids)

        total = q.count()
        perpage = 30

        p = Pagination(page, perpage, total)
        if p.page > p.page_count:
            self.send_error(404)
            return

        q = q.order_by('-impact')[p.start:p.end]
        p.datalist = get_full_topics(q)
        self.render('topic_list.html', title=title, pagination=p)


class NodeHandler(PageHandler):
    def head(self, slug):
        pass

    def get(self, slug):
        page = self.get_page()
        if not page:
            self.send_error(404)
            return
        node = Node.query.get_first(slug=slug)
        if not node:
            self.send_error(404)
            return

        q = Topic.query.filter_by(node_id=node.id)
        total = q.count()
        perpage = 30

        p = Pagination(page, perpage, total)
        if p.page > p.page_count:
            self.send_error(404)
            return

        q = q.order_by('-impact')[p.start:p.end]
        p.datalist = get_full_topics(q)
        self.render('node.html', p=p, node=node)


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
        self.write(markdown(text))


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
    ('/', LatestHandler),
    ('/following', FollowingHandler),
    ('/popular', PopularHandler),
    ('/preview', PreviewHandler),
    ('/feed', SiteFeedHandler),
    ('/search', SearchHandler),
    ('/upload', UploadHandler),
    ('/node/(\w+)', NodeHandler),
]
