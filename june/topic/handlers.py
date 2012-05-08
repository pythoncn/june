from july import JulyApp
from june.account.lib import UserHandler
from june.account.decorators import require_user
from june.node.models import Node
from models import Topic


class TopicHandler(UserHandler):
    def get(self, id):
        topic = Topic.query.get_first(id=id)
        node = Node.query.get_first(id=topic.node_id)
        self.render('topic.html', topic=topic, node=node)


class CreateTopicHandler(UserHandler):
    def get(self):
        nodes = Node.query.all()
        self.render("create_topic.html", nodes=nodes)


class CreateNodeTopicHandler(UserHandler):
    @require_user
    def get(self, slug):
        node = Node.query.get_first(slug=slug)
        self.render('topic_form.html', node=node)


app_handlers = [
    ('/create', CreateTopicHandler),
    ('/(\d+)', TopicHandler),
]
topic_app = JulyApp('topic', __name__, handlers=app_handlers)
