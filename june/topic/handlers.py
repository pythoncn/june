# -*- coding: utf-8 -*-

import hashlib
from datetime import datetime

from tornado.web import UIModule, authenticated
from tornado.escape import utf8
from tornado.options import options

from july.app import JulyApp
from july.cache import cache
from july.database import db

from june.account.lib import UserHandler
from june.account.decorators import require_user
from june.account.models import Member
from june.node.models import Node
from june.util import find_mention

from .models import Topic, Reply, Vote, TopicLog
from .lib import get_full_replies
from .lib import reply_impact_for_topic, accept_reply_impact_for_user
from .lib import up_impact_for_topic, up_impact_for_user
from .lib import down_impact_for_topic, down_impact_for_user


class TopicHandler(UserHandler):
    def get(self, id):
        topic = Topic.query.get_or_404(id)
        node = Node.query.get_or_404(topic.node_id)
        p = self.get_argument('p', 1)
        pagination = Reply.query.filter_by(topic_id=topic.id).paginate(p, 50)
        pagination.items = get_full_replies(pagination.items)

        if self.current_user:
            vote = Vote.query.get_first(
                topic_id=topic.id, user_id=self.current_user.id)
        else:
            vote = None

        logs = TopicLog.query.filter_by(topic_id=topic.id)\
                .order_by('-id').all()
        self.render('topic.html', topic=topic, node=node,
                    pagination=pagination, vote=vote, logs=logs)

    def post(self, id):
        action = self.get_argument('action', 'hit')
        #: compatible for rest api
        if action == 'delete':
            self.delete(id)
            return
        if action == 'close':
            self.close_topic(id)
            return
        if action == 'promote':
            self.promote_topic(id)
            return
        #: hit count
        topic = Topic.query.get_first(id=id)
        if not topic:
            self.send_error(404)
            return
        topic.hits += 1
        db.session.add(topic)
        db.session.commit()
        self.write({'stat': 'ok'})

    @require_user
    def delete(self, id):
        topic = self._get_verified_topic(id)
        if not topic:
            return
        #: delete a topic
        db.session.delete(topic)

        #: decrease node.topic_count
        node = Node.query.get_first(id=topic.node_id)
        node.topic_count -= 1
        db.session.add(node)

        #: commit
        db.session.commit()

        self.flash_message('Topic is deleted', 'info')
        self.redirect('/')

    @require_user
    def close_topic(self, id):
        topic = self._get_verified_topic(id)
        if not topic:
            return
        topic.status = 'close'
        db.session.add(topic)
        db.session.commit()
        self.flash_message('Topic is closed', 'info')
        self.redirect('/topic/%s' % topic.id)

    @require_user
    def promote_topic(self, id):
        topic = self._get_verified_topic(id)
        if not topic:
            return
        #: promote topic cost reputation
        user = Member.query.get_first(id=topic.user_id)
        if not user:
            self.send_error(404)
            return
        if topic.status == 'promote':
            self.flash_message('Your topic is promoted', 'info')
            self.redirect('/topic/%s' % topic.id)
            return
        cost = int(options.promote_topic_cost)
        if user.reputation < cost + 20:
            self.flash_message('Your reputation is too low', 'warn')
            self.redirect('/topic/%s' % topic.id)
            return
        user.reputation -= cost
        db.session.add(user)

        topic.status = 'promote'
        topic.impact += 86400  # one day
        db.session.add(topic)
        db.session.commit()
        self.flash_message('Your topic is promoted', 'info')
        self.redirect('/topic/%s' % topic.id)

    @require_user
    def _get_verified_topic(self, id):
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
        return topic


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
        db.session.add(topic)
        db.session.add(node)
        db.session.commit()

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

        topic.title = title
        topic.content = content
        db.session.add(topic)

        log = TopicLog(topic_id=topic.id, user_id=self.current_user.id)
        db.session.add(log)

        db.session.commit()

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

        db.session.add(topic)
        db.session.add(node)
        db.session.add(old_node)

        #:TODO edit log

        db.session.commit()
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

        db.session.add(reply)
        db.session.add(topic)
        db.session.commit()

        num = (topic.reply_count - 1) / 30 + 1
        url = '/topic/%s' % str(id)
        if num > 1:
            url += '?p=%s' % num
        cache.set(key, url, 100)
        self.redirect("%s#reply%s" % (url, topic.reply_count))

        refer = '<a href="/topic/%s#reply-%s">%s</a>' % \
                (topic.id, topic.reply_count, topic.title)
        #: reply notification
        self.create_notification(topic.user_id, content, refer, type='reply')
        #: mention notification
        for username in set(find_mention(content)):
            self.create_notification(username, content, refer,
                                     exception=topic.user_id)

        db.session.commit()
        #TODO: social networks


#: /reply/$id
class ReplyHandler(UserHandler):
    """ReplyHandler

    - POST: for topic owner to accept a reply.
    - DELETE: for reply owner to delete a reply.
    """

    @require_user
    def post(self, reply_id):
        #: toggle accept of a reply by topic owner
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
        #: delete a reply by reply owner
        reply = Reply.query.get_first(id=reply_id)
        if not reply:
            self.set_status(404)
            self.write({'stat': 'fail', 'msg': 'reply not found'})
            return
        if self.current_user.is_staff or self.current_user.id == reply.user_id:
            topic = Topic.query.get_first(id=reply.topic_id)
            if topic and topic.reply_count:
                topic.reply_count -= 1
            db.session.delete(reply)
            db.session.add(topic)
            db.session.commit()
            self.write({'stat': 'ok'})
            return
        self.set_status(403)
        self.write({'stat': 'fail', 'msg': 'permission denied'})

    def accept(self, reply):
        #: when accept an answer, topic owner pay 1 reputation
        user = Member.query.get_first(id=self.current_user.id)
        user.reputation -= 1
        db.session.add(user)

        reply.accepted = 'y'
        db.session.add(reply)

        #: replyer get reputation
        replyer = Member.query.get_first(id=reply.user_id)
        replyer.reputation += accept_reply_impact_for_user(user.reputation)
        db.session.add(replyer)
        self.write({'stat': 'ok', 'data': 'accept'})

        #: TODO notification

    def unaccept(self, reply):
        reply.accepted = 'n'
        db.session.add(reply)

        #: replyer loose reputation
        replyer = Member.query.get_first(id=reply.user_id)
        lose = accept_reply_impact_for_user(self.current_user.reputation)
        replyer.reputation -= lose
        db.session.add(replyer)
        self.write({'stat': 'ok', 'data': 'unaccept'})


class VoteTopicHandler(UserHandler):
    @require_user
    def post(self, id):
        _ = self.locale.translate
        topic = Topic.query.get_first(id=id)
        if not topic:
            self.send_error(404)
            return
        if topic.user_id == self.current_user.id:
            # you can't vote your own topic
            dct = {'stat': 'fail', 'msg': _("can't vote your own topic")}
            self.write(dct)
            return
        action = self.get_argument('action', None)
        if not action:
            self.send_error(403)
            return
        if action == 'up':
            self.up_topic(topic)
            return
        if action == 'down':
            self.down_topic(topic)
            return
        self.send_error('403')
        return

    def up_topic(self, topic):
        _ = self.locale.translate
        user = self.current_user
        vote = Vote.query.get_first(user_id=user.id, topic_id=topic.id)
        owner = Member.query.get_first(id=topic.user_id)
        if not vote:
            vote = Vote(user_id=user.id, topic_id=topic.id, type='up')
            db.session.add(vote)
            self._active_up(topic, owner, user.reputation)
            return
        #: cancel vote
        if vote.type == 'up':
            vote.type = 'none'
            db.session.add(vote)
            self._cancle_up(topic, owner, user.reputation)
            return
        #: change vote
        if vote.type == 'down':
            self.write({'stat': 'fail', 'msg': _("cancel your vote first")})
            return
        #: vote
        vote.type = 'up'
        db.session.add(vote)
        self._active_up(topic, owner, user.reputation)
        return

    def _active_up(self, topic, owner, reputation):
        #: increase topic's impact
        topic.impact += up_impact_for_topic(reputation)
        topic.up_count += 1
        db.session.add(topic)
        #: increase topic owner's reputation
        owner.reputation += up_impact_for_user(reputation)
        db.session.add(owner)
        db.session.commit()
        self.write({'stat': 'ok', 'data': topic.up_count})
        return

    def _cancle_up(self, topic, owner, reputation):
        topic.impact -= up_impact_for_topic(reputation)
        topic.up_count -= 1
        db.session.add(topic)
        owner.reputation -= up_impact_for_user(reputation)
        db.session.add(owner)
        db.session.commit()
        self.write({'stat': 'ok', 'data': topic.up_count})
        return

    def down_topic(self, topic):
        _ = self.locale.translate
        user = self.current_user
        vote = Vote.query.get_first(user_id=user.id, topic_id=topic.id)
        owner = Member.query.get_first(id=topic.user_id)
        if not vote:
            vote = Vote(user_id=user.id, topic_id=topic.id, type='down')
            db.session.add(vote)
            self._active_down(topic, owner, user.reputation)
            return
        #: cancel vote
        if vote.type == 'down':
            vote.type = 'none'
            db.session.add(vote)
            self._cancel_down(topic, owner, user.reputation)
            return

        #: change vote
        if vote.type == 'up':
            self.write({'stat': 'fail', 'msg': _("cancel your vote first")})
            return

        vote.type = 'down'
        db.session.add(vote)
        self._active_down(topic, owner, user.reputation)
        return

    def _active_down(self, topic, owner, reputation):
        #: increase topic's impact
        topic.impact -= down_impact_for_topic(reputation)
        topic.down_count += 1
        db.session.add(topic)
        #: increase topic owner's reputation
        owner.reputation -= down_impact_for_user(reputation)
        db.session.add(owner)
        db.session.commit()
        self.write({'stat': 'ok', 'data': topic.down_count})
        return

    def _cancel_down(self, topic, owner, reputation):
        topic.impact += down_impact_for_topic(reputation)
        topic.down_count -= 1
        db.session.add(topic)
        owner.reputation += down_impact_for_user(reputation)
        db.session.add(owner)
        db.session.commit()
        self.write({'stat': 'ok', 'data': topic.down_count})
        return


app_handlers = [
    ('/create', CreateTopicHandler),
    ('/(\d+)', TopicHandler),
    ('/(\d+)/edit', EditTopicHandler),
    ('/(\d+)/move', MoveTopicHandler),
    ('/(\d+)/reply', CreateReplyHandler),
    ('/(\d+)/vote', VoteTopicHandler),
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

app = JulyApp(
    'topic', __name__, handlers=app_handlers,
    ui_modules=app_modules
)
