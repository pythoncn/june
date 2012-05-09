from july.cache import get_cache_list
from june.account.models import Member
from june.node.models import Node


def get_full_topics(topics):
    users = get_cache_list(Member, (t.user_id for t in topics), 'member:')
    nodes = get_cache_list(Node, (t.node_id for t in topics), 'node:')
    print users
    for topic in topics:
        if topic.user_id in users and topic.node_id in nodes:
            topic.user = users[topic.user_id]
            topic.node = nodes[topic.node_id]
            yield topic
