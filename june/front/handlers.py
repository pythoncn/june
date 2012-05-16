import os.path
import hashlib
import tornado.web
from tornado.options import options
from july.web import JulyHandler
from july.util import import_object
from july.cache import cache
from june.account.models import Member
from june.account.lib import UserHandler
from june.account.decorators import require_user
from june.node.models import FollowNode, Node
from june.topic.models import Topic, Reply, Vote
from june.topic.lib import get_full_topics
from june.typo import markdown
from june.util import Pagination


class PageHandler(UserHandler):
    def get_page(self, arg='p'):
        page = self.get_argument(arg, 1)
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
        self.render('node.html', pagination=p, node=node)


class MemberHandler(PageHandler):
    def get(self, username):
        perpage = 10

        topic_page = self.get_page('tp')
        fav_page = self.get_page('fp')
        if not (topic_page and fav_page):
            self.send_error(404)
            return

        user = Member.query.get_first(username=username)
        if not user:
            self.send_error(404)
            return

        #: user's topics pagination {{{
        tq = Topic.query.filter_by(user_id=user.id)
        total = tq.count()
        tp = Pagination(topic_page, perpage, total)
        if tp.page > tp.page_count:
            self.send_error(404)
            return

        tq = tq.order_by('-id')[tp.start:tp.end]
        tp.datalist = get_full_topics(tq)
        #: }}}

        #: user's faved topics pagination {{{
        #: TODO cache
        votes = Vote.query.filter_by(user_id=user.id, type='up')\
                .values('topic_id')
        topic_ids = (v[0] for v in votes)
        fq = Topic.query.filter_by(id__in=topic_ids)
        total = fq.count()
        fp = Pagination(fav_page, perpage, total)
        if fp.page > fp.page_count:
            self.send_error(404)
            return

        fq = fq.order_by('-id')[fp.start:fp.end]
        fp.datalist = get_full_topics(fq)
        #: }}}

        replies = Reply.query.filter_by(user_id=user.id).order_by('-id')[:20]

        self.render('member.html', topic_pagination=tp, fav_pagination=fp,
                    user=user, replies=replies)


class RedirectMemberHandler(JulyHandler):
    def get(self, username):
        self.redirect('/~%s' % username)


class SiteFeedHandler(JulyHandler):
    def get_template_path(self):
        return os.path.join(os.path.dirname(__file__), '_templates')

    def get(self):
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        html = cache.get('sitefeed')
        if html is not None:
            self.write(html)
            return
        topics = get_full_topics(Topic.query.order_by('-id')[:20])
        html = self.render_string('feed.xml', topics=topics)
        cache.set('sitefeed', html, 1800)
        self.write(html)


class NodeFeedHandler(JulyHandler):
    def get_template_path(self):
        return os.path.join(os.path.dirname(__file__), '_templates')

    def get(self, slug):
        node = Node.query.get_first(slug=slug)
        if not node:
            self.send_error(404)
            return

        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        key = 'nodefeed:%s' % str(slug)
        html = cache.get(key)
        if html is not None:
            self.write(html)
            return

        topics = Topic.query.filter_by(node_id=node.id)[:20]
        topics = get_full_topics(topics)
        html = self.render_string('node_feed.xml', topics=topics, node=node)
        cache.set(key, html, 1800)
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
    ('/node/(\w+)/feed', NodeFeedHandler),
    ('/~(\w+)', MemberHandler),
    ('/member/(\w+)', RedirectMemberHandler),
]
