import math
from tornado.options import options
from june.lib.handler import BaseHandler
from june.lib.decorators import require_user
from june.models import Topic, Member, Reply
from june.models.mixin import NotifyMixin


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
            dct = {'status': 'ok'}
            dct['data'] = {'action': 'cancel', 'count': len(up_users)}
            self.write(dct)
            return
        up_users.append(user_id)
        topic.ups = ','.join(str(i) for i in up_users)
        topic.impact += self._calc_topic_impact()
        creator.reputation += self._calc_user_impact()
        self.db.add(topic)
        self.db.add(creator)
        self.db.commit()
        dct = {'status': 'ok'}
        dct['data'] = {'action': 'active', 'count': len(up_users)}
        self.write(dct)
        return

    def _calc_topic_impact(self):
        if self.current_user.reputation < 2:
            return 0
        factor = int(options.up_factor_for_topic)
        return factor * int(math.log(self.current_user.reputation))

    def _calc_user_impact(self):
        if self.current_user.reputation < 2:
            return 0
        factor = int(options.up_factor_for_user)
        impact = factor * int(math.log(self.current_user.reputation))
        return min(impact, options.up_max_for_user)


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
            dct = {'status': 'ok'}
            dct['data'] = {'action': 'cancel', 'count': len(down_users)}
            self.write(dct)
            return
        down_users.append(user_id)
        topic.downs = ','.join(str(i) for i in down_users)
        topic.impact -= self._calc_topic_impact()
        creator.reputation -= self._calc_user_impact()
        self.db.add(creator)
        self.db.add(topic)
        self.db.commit()
        dct = {'status': 'ok'}
        dct['data'] = {'action': 'active', 'count': len(down_users)}
        self.write(dct)
        return

    def _calc_topic_impact(self):
        if self.current_user.reputation < 2:
            return 0
        factor = int(options.down_factor_for_topic)
        return factor * int(math.log(self.current_user.reputation))

    def _calc_user_impact(self):
        if self.current_user.reputation < 2:
            return 0
        factor = int(options.down_factor_for_user)
        impact = factor * int(math.log(self.current_user.reputation))
        return min(impact, options.down_max_for_user)


class AcceptReplyHandler(BaseHandler, NotifyMixin):
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

    def _calc_user_impact(self):
        if self.current_user.reputation < 2:
            return 0
        factor = int(options.accept_reply_factor_for_user)
        impact = factor * int(math.log(self.current_user.reputation))
        return min(impact, options.vote_max_for_user)

    def post(self, topic_id, reply_id):
        reply_topic = self._is_exist(topic_id, reply_id)
        if not reply_topic:
            self.send_error(404)
            return

        reply, topic = reply_topic
        user_id = self.current_user.id
        if user_id != topic.user_id:
            dct = {'status': 'fail', 'msg': 'you are not topic owner'}
            self.write(dct)
            return
        if user_id == reply.user_id:
            dct = {'status': 'fail', 'msg': 'cannot accept your own reply'}
            self.write(dct)
            return

        creator = self.db.query(Member).filter_by(id=reply.user_id).first()
        if reply.accepted == 'y':
            creator.reputation -= self._calc_user_impact()
            reply.accepted = 'n'
            self.db.add(creator)
            self.db.add(reply)
            self.db.commit()
            dct = {'status': 'ok', 'data': 'cancel'}
            self.write(dct)
            return

        creator.reputation += self._calc_user_impact()
        reply.accepted = 'y'
        self.db.add(reply)
        self.db.add(creator)
        link = '/topic/%s' % topic.id
        self.create_notify(reply.user_id, topic.title, reply.content,
                           link, 'accept')
        self.db.commit()
        dct = {'status': 'ok', 'data': 'active'}
        self.write(dct)
        return


handlers = [
    ('/api/topic/(\d+)/up', UpTopicHandler),
    ('/api/topic/(\d+)/down', DownTopicHandler),
    ('/api/topic/(\d+)/(\d+)/accept', AcceptReplyHandler),
]
