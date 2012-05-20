import hashlib
from datetime import datetime
from tornado.web import UIModule, authenticated
from tornado.escape import utf8
from july.app import JulyApp
from july.cache import cache
from july.database import db
from june.account.lib import UserHandler
from june.account.decorators import require_user
from june.account.models import Member
from june.node.models import Node
from june.util import Pagination
from .models import Topic, Reply, Vote
from .lib import get_full_replies, reply_impact_for_topic
from .lib import accept_reply_impact_for_user


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

    def post(self, id):
        action = self.get_argument('action', 'hit')
        #: compatible for rest api
        if action == 'delete':
            self.delete(id)
            return
        #: hit count
        topic = Topic.query.get_first(id=id)
        if not topic:
            self.send_error(404)
            return
        topic.hits += 1
        db.master.add(topic)
        db.master.commit()
        self.write({'stat': 'ok'})

    @require_user
    def delete(self, id):
        #: delete topic need a password
        password = self.get_argument('password', None)
        if not password:
            self.flash_message('Password is required', 'error')
            self.redirect('/topic/%s' % id)
            return
        if not self.current_user.check_password(password):
            self.flash_message('Invalid password', 'error')
            self.redirect('/topic/%s' % id)
            return
        topic = Topic.query.get_first(id=id)
        if not topic:
            self.send_error(404)
            return
        #: check permission
        if not self.check_permission_of(topic):
            return

        #: delete a topic
        db.master.delete(topic)

        #: decrease node.topic_count
        node = Node.query.get_first(id=topic.node_id)
        node.topic_count -= 1
        db.master.add(node)

        #: commit
        db.master.commit()

        self.flash_message('Topic is deleted', 'info')
        self.redirect('/')


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
        if user.is_admin:
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
        self.check_permission_of(topic)
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
        if not self.check_permission_of(topic):
            self.render('edit_topic_form.html', topic=topic)
            return

        #TODO topic log

        topic.title = title
        topic.content = content
        db.master.add(topic)
        db.master.commit()

        url = '/topic/%s' % topic.id
        self.redirect(url)


class MoveTopicHandler(UserHandler):
    @require_user
    def get(self, topic_id):
        topic = Topic.query.get_first(id=topic_id)
        if not topic:
            self.send_error(404)
            return
        self.check_permission_of(topic)
        nodes = Node.query.all()
        self.render('move_topic.html', topic=topic, nodes=nodes)

    @require_user
    def post(self, topic_id):
        slug = self.get_argument('slug', None)
        if not slug:
            self.send_error(404)
            return
        topic = Topic.query.get_first(id=topic_id)
        if not topic:
            self.send_error(404)
            return
        node = Node.query.get_first(slug=slug)
        if not node:
            self.send_error(404)
            return
        #: check permission
        if not self.check_permission_of(topic):
            return

        #: increase node.topic_count
        topic.node_id = node.id
        node.topic_count += 1

        #: decrease topic's original node.topic_count
        old_node = Node.query.get_first(id=topic.node_id)
        old_node.topic_count -= 1

        db.master.add(topic)
        db.master.add(node)
        db.master.add(old_node)

        db.master.commit()
        self.redirect('/topic/%s' % topic.id)


class CreateReplyHandler(UserHandler):
    @require_user
    def post(self, id):
        # for topic reply
        content = self.get_argument('content', None)
        if not content:
            self.flash_message('Please fill the required fields', 'error')
            self.redirect('/topic/%s' % id)
            return

        topic = Topic.query.get_first(id=id)
        if not topic:
            self.send_error(404)
            return
        if topic.status == 'delete':
            self.send_error(404)
            return
        if topic.status == 'close':
            self.send_error(403)
            return
        key = hashlib.md5(utf8(content)).hexdigest()
        url = cache.get(key)
        # avoid double submit
        if url:
            self.redirect(url)
            return

        user = self.current_user

        #: create reply
        reply = Reply(topic_id=id, user_id=user.id, content=content)

        #: impact on topic
        topic.reply_count += 1
        topic.impact += reply_impact_for_topic(topic, user.reputation)

        #: update topic's last replyer
        topic.last_reply_by = self.current_user.id
        topic.last_reply_time = datetime.utcnow()

        db.master.add(reply)
        db.master.add(topic)
        db.master.commit()

        num = (topic.reply_count - 1) / 30 + 1
        url = '/topic/%s' % str(id)
        if num > 1:
            url += '?p=%s' % num
        cache.set(key, url, 100)
        self.redirect("%s#reply%s" % (url, topic.reply_count))

        #TODO: notifications
        #TODO: social networks


#: /reply/$id
class ReplyHandler(UserHandler):
    """ReplyHandler

    - POST: for topic owner to accept a reply.
    - DELETE: for reply owner to delete a reply.
    """

    @require_user
    def post(self, reply_id):
        _ = self.locale.translate
        reply = Reply.query.get_first(id=reply_id)
        if not reply:
            self.set_status(404)
            self.write({'stat': 'fail', 'msg': _('reply not found')})
            return
        #: check permission,
        #: only topic owner can accept a reply
        topic = Topic.query.get_first(id=reply.topic_id)
        #: if this topic is deleted
        if not topic:
            self.set_status(404)
            self.write({'stat': 'fail', 'msg': _('topic not found')})
            return
        if self.current_user.id != topic.user_id:
            self.set_status(403)
            self.write({'stat': 'fail', 'msg': _('permission denied')})
            return

        #: toggle acception
        if reply.accepted == 'y':
            self.unaccept(reply)
            return
        self.accept(reply)

    @authenticated
    def delete(self, reply_id):
        reply = Reply.query.get_first(id=reply_id)
        if not reply:
            self.set_status(404)
            self.write({'stat': 'fail', 'msg': 'reply not found'})
            return
        if self.current_user.is_staff or self.current_user.id == reply.user_id:
            topic = Topic.query.get_first(id=reply.topic_id)
            if topic and topic.reply_count:
                topic.reply_count -= 1
            db.master.delete(reply)
            db.master.add(topic)
            db.master.commit()
            self.write({'stat': 'ok'})
            return
        self.set_status(403)
        self.write({'stat': 'fail', 'msg': 'permission denied'})

    def accept(self, reply):
        #: when accept an answer, topic owner pay 1 reputation
        user = Member.query.get_first(id=self.current_user.id)
        user.reputation -= 1
        db.master.add(user)

        reply.accepted = 'y'
        db.master.add(reply)

        #: replyer get reputation
        replyer = Member.query.get_first(id=reply.user_id)
        replyer.reputation += accept_reply_impact_for_user(user.reputation)
        db.master.add(replyer)
        self.write({'stat': 'ok', 'data': 'accept'})

    def unaccept(self, reply):
        reply.accepted = 'n'
        db.master.add(reply)

        #: replyer loose reputation
        replyer = Member.query.get_first(id=reply.user_id)
        loose = accept_reply_impact_for_user(self.current_user.reputation)
        replyer.reputation -= loose
        db.master.add(replyer)
        self.write({'stat': 'ok', 'data': 'unaccept'})


app_handlers = [
    ('/create', CreateTopicHandler),
    ('/(\d+)', TopicHandler),
    ('/(\d+)/edit', EditTopicHandler),
    ('/(\d+)/move', MoveTopicHandler),
    ('/(\d+)/reply', CreateReplyHandler),
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
