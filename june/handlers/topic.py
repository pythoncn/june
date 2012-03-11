import hashlib
import math
from datetime import datetime
from tornado.escape import utf8
from tornado.options import options
from tornado.web import UIModule
from june.lib.handler import BaseHandler
from june.lib.decorators import require_user
from june.lib.util import ObjectDict, PageMixin
from june.filters import find_mention
from june.models import Node, Topic, Reply, Member
from june.models import NodeMixin, TopicMixin, MemberMixin, NotifyMixin


class TopicHandler(BaseHandler, TopicMixin, NodeMixin, PageMixin, NotifyMixin):
    def head(self, id):
        pass

    def get(self, id):
        topic = self._hit_topic(id)
        if not topic:
            self.send_error(404)
            return
        node = self.get_node_by_id(topic.node_id)
        user_ids = list(topic.up_users)
        user_ids.extend(topic.down_users)
        user_ids.append(topic.user_id)
        users = self.get_users(user_ids)
        self.render('topic.html', topic=topic, node=node, users=users)

    def _hit_topic(self, id):
        key = 'hit$topic:%s' % str(id)
        count = self.cache.get(key)
        if count is None:
            count = 1
            self.cache.set(key, 1)
        else:
            self.cache.incr(key)
        if count > 10:
            topic = self.db.query(Topic).filter_by(id=id).first()
            if not topic:
                return None
            self.cache.set(key, 1)
            topic.hits += 10
            topic.impact += 10
            self.db.add(topic)
            self.db.commit()
            self.cache.delete('topic:%s' % str(id))
        else:
            topic = self.get_topic_by_id(id)
            topic.hits = topic.hits + count
        return topic

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
        self.cache.delete('ui$reply:%s' % str(id))
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
            self.create_message(
                'Warning',
                "You have no permission to create a topic in this node")
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
            self.create_message('Form Error', 'Please fill the required field')
            self.render('topic_form.html', topic=None, node=node)
            return
        if not self._check_permission(node):
            self.create_message(
                'Warning',
                "You have no permission to create a topic in this node")
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
        key1 = 'ui$topiclist:0:1:-impact'
        key2 = 'ui$nodetopics:%s:1:-impact' % node.id
        self.cache.delete_multi(['status', key1, key2])
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
            self.create_message('Form Error', 'Please fill the required field')
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
            self.create_message('Warning', "You can't edit this topic now")
            return 2
        return 1


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
        self.db.add(creator)
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
            factor = 2
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


class VoteReplyHandler(BaseHandler):
    """Vote for a reply will affect the topic impact and reply user's
    reputation
    """

    def _is_exist(self, topic_id, reply_id):
        reply = self.db.query(Reply).filter_by(id=reply_id).first()
        if not reply or reply.topic_id != int(topic_id):
            return False
        topic = self.db.query(Topic).filter_by(id=topic_id).first()
        if not topic:
            return False
        return reply, topic

    def _calc_topic_impact(self):
        if self.current_user.reputation < 2:
            return 0
        if hasattr(options, 'vote_reply_factor_for_topic'):
            factor = int(options.vote_reply_factor_for_topic)
        else:
            factor = 500
        return factor * int(math.log(self.current_user.reputation))

    def _calc_user_impact(self):
        if self.current_user.reputation < 2:
            return 0
        if hasattr(options, 'vote_reply_factor_for_user'):
            factor = int(options.vote_reply_factor_for_user)
        else:
            factor = 2
        return factor * int(math.log(self.current_user.reputation))


class UpReplyHandler(VoteReplyHandler):
    @require_user
    def post(self, topic_id, reply_id):
        reply_topic = self._is_exist(topic_id, reply_id)
        if not reply_topic:
            self.send_error(404)
            return

        reply, topic = reply_topic
        user_id = self.current_user.id
        if user_id == reply.user_id:
            dct = {'status': 'fail', 'msg': 'cannot vote your own reply'}
            self.write(dct)
            return

        if user_id in reply.down_users:
            # you can't up and down vote at the same time
            dct = {'status': 'fail', 'msg': "cannot up vote your down reply"}
            self.write(dct)
            return

        creator = self.db.query(Member).filter_by(id=reply.user_id).first()
        up_users = list(reply.up_users)
        if user_id in up_users:
            up_users.remove(user_id)
            reply.ups = ','.join(str(i) for i in up_users)
            creator.reputation -= self._calc_user_impact()
            self.db.add(creator)
            self.db.add(reply)
            self.db.commit()
            dct = {'status': 'ok', 'msg': 'cancel'}
            self.write(dct)
            return

        if user_id != topic.user_id:
            # when topic creator vote a reply, topic impact will not change
            topic.impact += self._calc_topic_impact()
            self.db.add(topic)

        up_users.append(user_id)
        reply.ups = ','.join(str(i) for i in up_users)
        creator.reputation += self._calc_user_impact()
        self.db.add(reply)
        self.db.add(creator)
        self.db.commit()
        dct = {'status': 'ok', 'msg': 'active'}
        self.write(dct)
        return


class DownReplyHandler(VoteReplyHandler):
    @require_user
    def post(self, topic_id, reply_id):
        reply_topic = self._is_exist(topic_id, reply_id)
        if not reply_topic:
            self.send_error(404)
            return

        reply, topic = reply_topic
        user_id = self.current_user.id
        if user_id == reply.user_id:
            dct = {'status': 'fail', 'msg': 'cannot vote your own reply'}
            self.write(dct)
            return

        if user_id in reply.up_users:
            # you can't down and up vote at the same time
            dct = {'status': 'fail', 'msg': "cannot down vote your up reply"}
            self.write(dct)
            return

        creator = self.db.query(Member).filter_by(id=reply.user_id).first()
        down_users = list(reply.down_users)
        if user_id in down_users:
            down_users.remove(user_id)
            reply.downs = ','.join(str(i) for i in down_users)
            creator.reputation += self._calc_user_impact()
            self.db.add(creator)
            self.db.add(reply)
            self.db.commit()
            dct = {'status': 'ok', 'msg': 'cancel'}
            self.write(dct)
            return

        if user_id != topic.user_id:
            # when topic creator vote a reply, topic impact will not change
            topic.impact += self._calc_topic_impact()
            self.db.add(topic)

        down_users.append(user_id)
        reply.downs = ','.join(str(i) for i in down_users)
        creator.reputation -= self._calc_user_impact()
        self.db.add(reply)
        self.db.add(creator)
        self.db.commit()
        dct = {'status': 'ok', 'msg': 'active'}
        self.write(dct)
        return


handlers = [
    ('/node/(\w+)/topic', CreateTopicHandler),
    ('/topic', NewTopicHandler),
    ('/topic/(\d+)', TopicHandler),
    ('/topic/(\d+)/up', UpTopicHandler),
    ('/topic/(\d+)/down', DownTopicHandler),
    ('/topic/(\d+)/(\d+)/up', UpReplyHandler),
    ('/topic/(\d+)/(\d+)/down', DownReplyHandler),
    ('/topic/(\d+)/edit', EditTopicHandler),
]


class ReplyModule(UIModule, PageMixin, MemberMixin):
    def render(self, topic):
        if self._get_page() == 1:
            key = 'ui$reply:%s' % topic.id
            html = self.handler.cache.get(key)
            if html is not None:
                return html
            html = self._render_html(topic.id)
            self.handler.cache.set(key, html, 600)
            return html
        return self._render_html(topic.id)

    def _render_html(self, topic_id):
        page = self._get_pagination(
            Reply.query.filter_by(topic_id=topic_id),
            perpage=30)
        page = ObjectDict(page)
        user_ids = [o.user_id for o in page.datalist]
        users = self.get_users(user_ids)
        return self.render_string('module/reply_list.html',
                                  page=page, users=users)


class TopicListModule(UIModule, MemberMixin, NodeMixin, PageMixin):
    def render(self, user_id=0):
        order = self._get_order()
        p = self._get_page()
        key = 'ui$topiclist:%s:%s:%s' % (user_id, p, order)
        html = self.handler.cache.get(key)
        if html is not None:
            return html

        if user_id:
            node_ids = self.get_user_follow_nodes(self.current_user.id)
            if not node_ids:
                msg = self.handler.locale.translate(
                    "You need follow some nodes")
                return '<div class="cell">%s</div>' % msg

            if len(node_ids) == 1:
                # for better performance
                q = Topic.query.filter_by(node_id=node_ids[0]).order_by(order)
            else:
                q = Topic.query.filter_by(node_id__in=set(node_ids))\
                        .order_by(order)
        else:
            q = Topic.query.order_by(self._get_order())

        page = ObjectDict(self._get_pagination(q))

        user_ids = []
        node_ids = []
        for topic in page.datalist:
            user_ids.append(topic.user_id)
            node_ids.append(topic.node_id)
        users = self.get_users(user_ids)
        nodes = self.get_nodes(node_ids)
        html = self.render_string('module/topic_list.html', page=page,
                                  users=users, nodes=nodes)
        self.handler.cache.set(key, html, 60)
        return html


class NodeTopicsModule(UIModule, MemberMixin, PageMixin):
    def render(self, node_id):
        order = self._get_order()
        p = self._get_page()
        key = 'ui$nodetopics:%s:%s:%s' % (node_id, p, order)
        html = self.handler.cache.get(key)
        if html is not None:
            return html

        q = Topic.query.filter_by(node_id=node_id).order_by(order)
        page = ObjectDict(self._get_pagination(q))

        user_ids = []
        for topic in page.datalist:
            user_ids.append(topic.user_id)
        users = self.get_users(user_ids)
        html = self.render_string('module/topic_list.html', page=page,
                                  users=users, nodes=None)
        self.handler.cache.set(key, html, 600)
        return html


ui_modules = {
    'ReplyModule': ReplyModule,
    'TopicListModule': TopicListModule,
    'NodeTopicsModule': NodeTopicsModule,
}
