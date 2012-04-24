from july import JulyApp
from june.account.lib import UserHandler


class TopicHandler(UserHandler):
    def get(self, id):
        pass


class NewTopicHandler(UserHandler):
    def get(self):
        nodes = self.get_all_nodes()
        self.render("new_topic.html", nodes=nodes)


topic_app = JulyApp('topic', __name__)
