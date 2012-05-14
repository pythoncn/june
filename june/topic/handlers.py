import hashlib
from tornado.web import UIModule
from tornado.escape import utf8
from july import JulyApp
from july.cache import cache
from july.database import db
from june.account.lib import UserHandler
from june.account.decorators import require_user
from june.account.models import Member
from june.node.models import Node
from june.util import Pagination
from models import Topic, Reply, Vote
from lib import get_full_replies


class TopicHandler(UserHandler):
    def get(self, id):
        page = self.get_argument('p', 1)
        try:
            page = int(page)
        except:
            self.send_error(404)
            return
        if page < 0:
            self.send_error(404)
            return

        topic = Topic.query.get_first(id=id)
        if not topic:
            self.send_error(404)
            return

        p = Pagination(page, 50, topic.reply_count)
        if topic.reply_count and p.page > p.page_count:
            self.send_error(404)
            return

        node = Node.query.get_first(id=topic.node_id)
        q = Reply.query.filter_by(topic_id=topic.id)[p.start:p.end]
        p.datalist = get_full_replies(q)

        if self.current_user:
            vote = Vote.query.get_first(
                topic_id=topic.id, user_id=self.current_user.id)
        else:
            vote = None
        self.render('topic.html', topic=topic, node=node, pagination=p,
                    vote=vote)


class CreateTopicHandler(UserHandler):
    def get(self):
        nodes = Node.query.all()
        self.render("create_topic.html", nodes=nodes)


class CreateNodeTopicHandler(UserHandler):
    @require_user
    def get(self, slug):
        node = Node.query.get_first(slug=slug)
        if not node:
            self.send_error(404)
            return
        self._check_permission(node)
        self.render('create_topic_form.html', node=node)

    @require_user
    def post(self, slug):
        node = Node.query.get_first(slug=slug)
        if not node:
            self.send_error(404)
            return
        title = self.get_argument('title', None)
        content = self.get_argument('content', None)
        if not (title and content):
            self.flash_message('Please fill the required fields', 'error')
            self.render('create_topic_form.html', node=node)
            return
        if not self._check_permission(node):
            self.render('create_topic_form.html', node=node)
            return
        #: avoid double submit
        key = hashlib.md5(utf8(content)).hexdigest()
        url = cache.get(key)
        if url:
            self.redirect(url)
            return

        topic = Topic(title=title, content=content)
        topic.node_id = node.id
        topic.user_id = self.current_user.id
        node.topic_count += 1
        db.master.add(topic)
        db.master.add(node)
        db.master.commit()

        url = '/topic/%d' % topic.id
        cache.set(key, url, 100)
        self.redirect(url)

        #TODO social networks

    def _check_permission(self, node):
        user = self.current_user
        if user.role > 9:
            return True
        if user.reputation < node.limit_reputation or \
           user.role < node.limit_role:
            self.flash_message(
                "You have no permission to create a topic in this node",
                "warn"
            )
            return False
        return True


class EditTopicHandler(UserHandler):
    @require_user
    def get(self, id):
        topic = Topic.query.get_first(id=id)
        if not topic:
            self.send_error(404)
            return
        self._check_permission(topic)
        self.render('edit_topic_form.html', topic=topic)

    @require_user
    def post(self, id):
        topic = Topic.query.get_first(id=id)
        if not topic:
            self.send_error(404)
            return
        title = self.get_argument('title', None)
        content = self.get_argument('content', None)
        if not (title and content):
            self.flash_message('Please fill the required fields', 'error')
            self.render('edit_topic_form.html', topic=topic)
            return
        if not self._check_permission(topic):
            self.render('edit_topic_form.html', topic=topic)
            return

        #TODO topic log

        topic.title = title
        topic.content = content
        db.master.add(topic)
        db.master.commit()

        url = '/topic/%s' % topic.id
        self.redirect(url)

    def _check_permission(self, topic):
        user = self.current_user
        if user.role > 9 or topic.user_id == user.id:
            return True
        self.flash_message(
            "You have no permission to edit this topic",
            "warn"
        )
        return False


app_handlers = [
    ('/create', CreateTopicHandler),
    ('/(\d+)', TopicHandler),
    ('/(\d+)/edit', EditTopicHandler),
]


class UserModule(UIModule):
    """UserModule

    This module contains topic and reply count,
    in this case, it is located in topic app
    """
    def render(self, user_id):
        user = Member.query.get_first(id=user_id)
        if not user:
            return ''
        topic_count = Topic.query.filter_by(user_id=user_id).count()
        reply_count = Reply.query.filter_by(user_id=user_id).count()
        user.topic_count = topic_count
        user.reply_count = reply_count
        return self.render_string('module/user.html', user=user)


app_modules = {
    'User': UserModule,
}

topic_app = JulyApp(
    'topic', __name__, handlers=app_handlers,
    ui_modules=app_modules
)
