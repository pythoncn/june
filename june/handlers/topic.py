import hashlib
import math
from datetime import datetime
from tornado.escape import utf8
from tornado.options import options
from june.lib.handler import BaseHandler
from june.lib.decorators import require_user
from june.lib.util import ObjectDict
from june.models import Node, Topic, Reply
from june.models import NodeMixin, TopicMixin


class CreateTopicHandler(BaseHandler):
    @require_user
    def get(self, slug):
        node = Node.query.filter_by(slug=slug).first()
        if not node:
            self.send_error(404)
            return
        self.render('topic_form.html', topic=None)

    @require_user
    def post(self, slug):
        node = self.db.query(Node).filter_by(slug=slug).first()
        if not node:
            self.send_error(404)
            return
        title = self.get_argument('title', None)
        content = self.get_argument('content', None)
        if not (title and content):
            msg = ObjectDict(header='Form Error',
                             body='Please fill the required field')
            self._context.message.append(msg)
            self.render('topic_form.html')
            return
        key = hashlib.md5(utf8(content)).hexdigest()
        url = self.cache.get(key)
        # avoid double submit
        if url:
            self.redirect(url)
            return
        topic = Topic(title=title, content=content)
        topic.node_id = node.id
        topic.user_id = self.current_user.id
        node.topic_count += 1
        self.db.add(topic)
        self.db.add(node)
        self.db.commit()
        url = '/topic/%d' % topic.id
        self.cache.set(key, url, 100)
        self.redirect(url)


class EditTopicHandler(BaseHandler, TopicMixin):
    @require_user
    def get(self, id):
        topic = self.get_topic_by_id(id)
        if not topic:
            self.send_error(404)
            return
        if not self._has_permission(topic):
            self.send_error(403)
            return
        self.render('topic_form.html', topic=topic)

    @require_user
    def post(self, id):
        topic = self.db.query(Topic).filter_by(id=id).first()
        if not topic:
            self.send_error(404)
            return
        if self._has_permission(topic) != 1:
            self.redirect('/topic/%d' % id)
            return

        title = self.get_argument('title', None)
        content = self.get_argument('content', None)
        if not (title and content):
            msg = ObjectDict(header='Form Error',
                             body='Please fill the required field')
            self._context.message.append(msg)
            self.render('topic_form.html')
            return
        topic.title = title
        topic.content = content
        self.db.add(topic)
        self.db.commit()
        self.redirect('/topic/%d' % topic.id)

    def _has_permission(self, topic):
        if self.current_user.role > 9:
            return 1
        if not self.is_owner_of(topic):
            self.send_error(403)
            return 0
        timedel = datetime.utcnow() - topic.created
        if timedel.seconds > 1200:
            # user can only edit a topic in 10 minutes
            msg = ObjectDict(header='Warning',
                             body="You can't edit this topic now")
            self._context.message.append(msg)
            return 2
        return 1


class TopicHandler(BaseHandler, TopicMixin, NodeMixin):
    def get(self, id):
        topic = self.get_topic_by_id(id)
        if not topic:
            self.send_error(404)
            return
        node = self.get_node_by_id(topic.node_id)
        replies = Reply.query.filter_by(topic_id=id).all()
        user_ids = [o.user_id for o in replies]
        user_ids.append(topic.user_id)
        users = self.get_users(user_ids)
        if self.is_ajax():
            self.render('snippet/topic.html', topic=topic, node=node,
                        replies=replies, users=users)
            return
        self.render('topic.html', topic=topic, node=node, replies=replies,
                    users=users)

    @require_user
    def post(self, id):
        # for topic reply
        content = self.get_argument('content', None)
        if not content:
            self.redirect('/topic/%s' % id)
            return

        topic = self.db.query(Topic).filter_by(id=id).first()
        if not topic:
            self.send_error(404)
            return

        key = hashlib.md5(utf8(content)).hexdigest()
        url = self.cache.get(key)
        # avoid double submit
        if url:
            self.redirect(url)
            return

        reply = Reply(content=content)
        reply.topic_id = id
        reply.user_id = self.current_user.id
        topic.reply_count += 1
        topic.impact += self._calc_impact(topic)
        self.db.add(reply)
        self.db.add(topic)
        self.create_notify(topic.user_id, topic, content)
        self.db.commit()
        url = '/topic/%s' % id
        self.cache.set(key, url, 100)
        self.redirect(url)

    def _calc_impact(self, topic):
        if hasattr(options, 'reply_factor_for_topic'):
            factor = int(options.reply_factor_for_topic)
        else:
            factor = 150
        if hasattr(options, 'reply_time_factor'):
            time_factor = int(options.reply_time_factor)
        else:
            time_factor = 100
        time = datetime.utcnow() - topic.created
        factor += time.days * time_factor
        return factor * int(math.log(self.current_user.reputation))


class UpTopicHandler(BaseHandler):
    @require_user
    def post(self, id):
        topic = self.db.query(Topic).filter_by(id=id).first()
        if not topic:
            self.send_error(404)
            return
        up_users = topic.up_users
        user_id = str(self.current_user.id)
        if user_id in up_users:
            up_users.remove(user_id)
            topic.ups = ','.join(up_users)
            topic.impact -= self._calc_impact()
            self.db.add(topic)
            self.db.commit()
            self.write('')
            return
        up_users.append(user_id)
        topic.ups = ','.join(up_users)
        topic.impact += self._calc_impact()
        self.db.add(topic)
        self.db.commit()
        self.write('')
        return

    def _calc_impact(self):
        if hasattr(options, 'up_factor_for_topic'):
            factor = int(options.up_factor_for_topic)
        else:
            factor = 600
        return factor * int(math.log(self.current_user.reputation))


class DownTopicHandler(BaseHandler):
    @require_user
    def post(self, id):
        topic = self.db.query(Topic).filter_by(id=id).first()
        if not topic:
            self.send_error(404)
            return
        down_users = topic.down_users
        user_id = str(self.current_user.id)
        if user_id in down_users:
            # you can't cancel a down vote
            self.write('')
            return
        down_users.append(user_id)
        topic.downs = ','.join(down_users)
        topic.impact -= self._calc_impact()
        self.db.add(topic)
        self.db.commit()
        self.write('')
        return

    def _calc_impact(self):
        if hasattr(options, 'down_factor_for_topic'):
            factor = int(options.down_factor_for_topic)
        else:
            factor = 600
        return factor * int(math.log(self.current_user.reputation))


handlers = [
    ('/node/(\w+)/topic', CreateTopicHandler),
    ('/topic/(\d+)', TopicHandler),
    ('/topic/(\d+)/up', UpTopicHandler),
    ('/topic/(\d+)/down', UpTopicHandler),
    ('/topic/(\d+)/edit', EditTopicHandler),
]
