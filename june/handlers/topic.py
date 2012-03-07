import hashlib
import math
from datetime import datetime
from tornado.escape import utf8
from tornado.options import options
from june.lib.handler import BaseHandler
from june.lib.decorators import require_user
from june.lib.util import ObjectDict, PageMixin
from june.filters import find_mention
from june.models import Node, Topic, Reply, Member
from june.models import NodeMixin, TopicMixin


class NewTopicHandler(BaseHandler, NodeMixin):
    @require_user
    def get(self):
        nodes = self.cache.get('allnodes')
        if nodes is None:
            nodes = Node.query.all()
            nodes = sorted(nodes, key=lambda o: o.updated, reverse=True)
            self.cache.set('allnodes', nodes, 600)
        self.render("new_topic.html", nodes=nodes)


class CreateTopicHandler(BaseHandler, NodeMixin):
    @require_user
    def get(self, slug):
        node = self.get_node_by_slug(slug)
        if not node:
            self.send_error(404)
            return
        if not self._check_permission(node):
            msg = ObjectDict(
                header='Warning',
                body="You have no permission to create a topic in this node")
            self._context.message.append(msg)
            self.render('topic_form.html', topic=None, node=node)
            return
        self.render('topic_form.html', topic=None, node=node)

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
            self.render('topic_form.html', topic=None, node=node)
            return
        if not self._check_permission(node):
            msg = ObjectDict(
                header='Warning',
                body="You have no permission to create a topic in this node")
            self._context.message.append(msg)
            self.render('topic_form.html', topic=None, node=node)
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
        self.cache.delete_multi(['status', 'homepage:-impact:1'])
        self.redirect(url)

    def _check_permission(self, node):
        user = self.current_user
        if user.role > 9:
            return True
        if user.reputation < node.limit_reputation:
            return False
        return user.role >= node.limit_role


class EditTopicHandler(BaseHandler, TopicMixin, NodeMixin):
    @require_user
    def get(self, id):
        topic = self.get_topic_by_id(id)
        if not topic:
            self.send_error(404)
            return
        if not self._check_permission(topic):
            self.send_error(403)
            return
        node = self.get_node_by_id(topic.node_id)
        self.render('topic_form.html', topic=topic, node=node)

    @require_user
    def post(self, id):
        topic = self.db.query(Topic).filter_by(id=id).first()
        if not topic:
            self.send_error(404)
            return
        if self._check_permission(topic) != 1:
            self.redirect('/topic/%s' % id)
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
        self.cache.delete('topic:%s' % topic.id)
        self.redirect('/topic/%s' % topic.id)

    def _check_permission(self, topic):
        if self.current_user.role > 9:
            return 1
        if not self.is_owner_of(topic):
            self.send_error(403)
            return 0
        timedel = datetime.utcnow() - topic.created
        if timedel.days:
            # user can only edit a topic in 10 minutes
            msg = ObjectDict(header='Warning',
                             body="You can't edit this topic now")
            self._context.message.append(msg)
            return 2
        return 1


class TopicHandler(BaseHandler, TopicMixin, NodeMixin, PageMixin):
    def head(self, id):
        pass

    def get(self, id):
        topic = self.get_topic_by_id(id)
        if not topic:
            self.send_error(404)
            return
        node = self.get_node_by_id(topic.node_id)
        if self._get_page() == 1:
            page = self.cache.get('reply-of-topic:%s' % str(id))
            if page is None:
                page = self._get_pagination(
                    Reply.query.filter_by(topic_id=id),
                    perpage=30)
                self.cache.set('reply-of-topic:%s' % str(id), page, 600)
        else:
            page = self._get_pagination(
                Reply.query.filter_by(topic_id=id),
                perpage=30)
        page = ObjectDict(page)
        user_ids = [o.user_id for o in page.datalist]
        user_ids.append(topic.user_id)
        user_ids.extend(topic.up_users)
        user_ids.extend(topic.down_users)
        users = self.get_users(user_ids)
        if self.is_ajax():
            self.render('snippet/topic.html', topic=topic, node=node,
                        page=page, users=users)
            return
        self.render('topic.html', topic=topic, node=node, page=page,
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

        # impact on topic
        topic.reply_count += 1
        topic.impact += self._calc_impact(topic)

        #TODO impact on creator

        self.db.add(reply)
        self.db.add(topic)

        # notifications
        self.create_notify(topic.user_id, topic, content)
        for username in set(find_mention(content)):
            self.create_mention(username, topic, content)

        self.db.commit()
        url = '/topic/%s' % str(id)
        self.cache.set(key, url, 100)
        self.cache.delete('reply-of-topic:%s' % str(id))
        self.redirect(url)

    def _calc_impact(self, topic):
        if self.current_user.reputation < 2:
            return 0
        if hasattr(options, 'reply_factor_for_topic'):
            factor = int(options.reply_factor_for_topic)
        else:
            factor = 300
        if hasattr(options, 'reply_time_factor'):
            time_factor = int(options.reply_time_factor)
        else:
            time_factor = 200
        time = datetime.utcnow() - topic.created
        factor += time.days * time_factor
        return factor * int(math.log(self.current_user.reputation))


class UpTopicHandler(BaseHandler):
    """Up a topic will increase impact of the topic,
    and increase reputation of the creator
    """

    @require_user
    def post(self, id):
        topic = self.db.query(Topic).filter_by(id=id).first()
        if not topic:
            self.send_error(404)
            return
        user_id = self.current_user.id
        if topic.user_id == user_id:
            # you can't vote your own topic
            dct = {'status': 'fail', 'msg': 'cannot up vote your own topic'}
            self.write(dct)
            return
        if user_id in topic.down_users:
            # you can't up and down vote at the same time
            dct = {'status': 'fail', 'msg': 'cannot up vote your down topic'}
            self.write(dct)
            return
        creator = self.db.query(Member).filter_by(id=topic.user_id).first()
        up_users = list(topic.up_users)
        if user_id in up_users:
            up_users.remove(user_id)
            topic.ups = ','.join(str(i) for i in up_users)
            topic.impact -= self._calc_topic_impact()
            creator.reputation -= self._calc_user_impact()
            self.db.add(creator)
            self.db.add(topic)
            self.db.commit()
            dct = {'status': 'ok', 'msg': 'cancel'}
            self.write(dct)
            return
        up_users.append(user_id)
        topic.ups = ','.join(str(i) for i in up_users)
        topic.impact += self._calc_topic_impact()
        creator.reputation += self._calc_user_impact()
        self.db.add(topic)
        self.db.commit()
        dct = {'status': 'ok', 'msg': 'active'}
        self.write(dct)
        return

    def _calc_topic_impact(self):
        if self.current_user.reputation < 2:
            return 0
        if hasattr(options, 'up_factor_for_topic'):
            factor = int(options.up_factor_for_topic)
        else:
            factor = 1000
        return factor * int(math.log(self.current_user.reputation))

    def _calc_user_impact(self):
        if self.current_user.reputation < 2:
            return 0
        if hasattr(options, 'up_factor_for_user'):
            factor = int(options.up_factor_for_user)
        else:
            factor = 6
        return factor * int(math.log(self.current_user.reputation))


class DownTopicHandler(BaseHandler):
    """Down a topic will reduce impact of the topic,
    and decrease reputation of the creator
    """

    @require_user
    def post(self, id):
        topic = self.db.query(Topic).filter_by(id=id).first()
        if not topic:
            self.send_error(404)
            return
        user_id = self.current_user.id
        if topic.user_id == user_id:
            # you can't vote your own topic
            dct = {'status': 'fail', 'msg': "cannot down vote your own topic"}
            self.write(dct)
            return
        if user_id in topic.up_users:
            # you can't down and up vote at the same time
            dct = {'status': 'fail', 'msg': "cannot down vote your up topic"}
            self.write(dct)
            return
        creator = self.db.query(Member).filter_by(id=topic.user_id).first()
        down_users = list(topic.down_users)
        if user_id in down_users:
            #TODO: can you cancel a down vote ?
            down_users.remove(user_id)
            topic.downs = ','.join(str(i) for i in down_users)
            topic.impact += self._calc_topic_impact()
            creator.reputation += self._calc_user_impact()
            self.db.add(creator)
            self.db.add(topic)
            self.db.commit()
            dct = {'status': 'ok', 'msg': 'cancel'}
            self.write(dct)
            return
        down_users.append(user_id)
        topic.downs = ','.join(str(i) for i in down_users)
        topic.impact -= self._calc_topic_impact()
        creator.reputation -= self._calc_user_impact()
        self.db.add(creator)
        self.db.add(topic)
        self.db.commit()
        dct = {'status': 'ok', 'msg': 'active'}
        self.write(dct)
        return

    def _calc_topic_impact(self):
        if self.current_user.reputation < 2:
            return 0
        if hasattr(options, 'down_factor_for_topic'):
            factor = int(options.down_factor_for_topic)
        else:
            factor = 800
        return factor * int(math.log(self.current_user.reputation))

    def _calc_user_impact(self):
        if self.current_user.reputation < 2:
            return 0
        if hasattr(options, 'down_factor_for_user'):
            factor = int(options.down_factor_for_user)
        else:
            factor = 1
        return factor * int(math.log(self.current_user.reputation))


handlers = [
    ('/node/(\w+)/topic', CreateTopicHandler),
    ('/topic', NewTopicHandler),
    ('/topic/(\d+)', TopicHandler),
    ('/topic/(\d+)/up', UpTopicHandler),
    ('/topic/(\d+)/down', DownTopicHandler),
    ('/topic/(\d+)/edit', EditTopicHandler),
]
