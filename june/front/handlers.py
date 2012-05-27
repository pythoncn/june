import os.path
import hashlib
import tornado.web
from tornado.options import options
from july.web import JulyHandler
from july.util import import_object
from july.cache import cache
from june.account.models import Member, Profile
from june.account.lib import UserHandler
from june.account.decorators import require_user
from june.node.models import FollowNode, Node
from june.topic.models import Topic, Reply, Vote
from june.topic.lib import get_full_topics
from june.filters import markdown


class LatestHandler(UserHandler):
    def head(self):
        pass

    def get(self):
        title = 'Latest'

        p = self.get_argument('p', 1)
        pagination = Topic.query.order_by('-last_reply_time').paginate(p, 30)

        pagination.items = get_full_topics(pagination.items)
        self.render('topic_list.html', title=title, pagination=pagination)


class PopularHandler(UserHandler):
    def head(self):
        pass

    def get(self):
        title = 'Popular'

        p = self.get_argument('p', 1)
        pagination = Topic.query.order_by('-impact').paginate(p, 30)

        pagination.items = get_full_topics(pagination.items)
        self.render('topic_list.html', title=title, pagination=pagination)


class FollowingHandler(UserHandler):
    @tornado.web.authenticated
    def get(self):
        title = 'Popular'

        user_id = self.current_user.id
        fs = FollowNode.query.filter_by(user_id=user_id).values('node_id')
        node_ids = (f[0] for f in fs)

        p = self.get_argument('p', 1)
        pagination = Topic.query.filter_by(node_id__in=node_ids)\
                .order_by('-last_reply_time').paginate(p, 30)

        pagination.items = get_full_topics(pagination.items)
        self.render('topic_list.html', title=title, pagination=pagination)


class NodeHandler(UserHandler):
    def head(self, slug):
        pass

    def get(self, slug):
        node = Node.query.filter_by(slug=slug).first_or_404()
        title = node.title

        p = self.get_argument('p', 1)
        pagination = Topic.query.filter_by(node_id=node.id)\
                .order_by('-impact').paginate(p, 30)

        pagination.items = get_full_topics(pagination.items)
        self.render('topic_list.html', node=node,
                    pagination=pagination, title=title)


class MemberHandler(UserHandler):
    def get(self, username):
        user = Member.query.filter_by(username=username).first_or_404()

        q = Topic.query.filter_by(user_id=user.id)
        topics = get_full_topics(q.order_by('-id')[:10])

        #: user's faved topics {{{
        #: TODO cache
        votes = Vote.query.filter_by(user_id=user.id, type='up')\
                .values('topic_id')
        topic_ids = (v[0] for v in votes)
        q = Topic.query.filter_by(id__in=topic_ids)
        likes = get_full_topics(q.order_by('-id')[:10])
        #: }}}

        replies = Reply.query.filter_by(user_id=user.id).order_by('-id')[:20]
        profile = Profile.query.get_first(user_id=user.id)
        self.render('member.html', topics=topics, likes=likes, user=user,
                    replies=replies, profile=profile)


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
