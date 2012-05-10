from tornado.web import UIModule
from july import JulyApp
from june.account.lib import UserHandler
from june.account.decorators import require_user
from june.account.models import Member
from june.node.models import Node
from models import Topic, Reply


class TopicHandler(UserHandler):
    def get(self, id):
        topic = Topic.query.get_first(id=id)
        node = Node.query.get_first(id=topic.node_id)
        user = Member.query.get_first(id=topic.user_id)
        self.render('topic.html', topic=topic, node=node, user=user)


class CreateTopicHandler(UserHandler):
    def get(self):
        nodes = Node.query.all()
        self.render("create_topic.html", nodes=nodes)


class CreateNodeTopicHandler(UserHandler):
    @require_user
    def get(self, slug):
        node = Node.query.get_first(slug=slug)
        self.render('topic_form.html', node=node)


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


app_handlers = [
    ('/create', CreateTopicHandler),
    ('/(\d+)', TopicHandler),
]

ui_modules = {
    'User': UserModule,
}
topic_app = JulyApp(
    'topic', __name__, handlers=app_handlers,
    ui_modules=ui_modules
)
