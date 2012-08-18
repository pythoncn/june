import math
from datetime import datetime
from june.account.models import Member
from june.node.models import Node
from june.cache import get_cache_list


def get_user_id_list(topics):
    for t in topics:
        yield t.user_id
        if t.last_reply_by:
            yield t.last_reply_by


def get_full_topics(topics):
    users = get_cache_list(Member, get_user_id_list(topics), 'member:')
    nodes = get_cache_list(Node, (t.node_id for t in topics), 'node:')
    for topic in topics:
        if topic.user_id in users and topic.node_id in nodes:
            topic.user = users[topic.user_id]
            if topic.last_reply_by:
                topic.replyer = users[topic.last_reply_by]
            else:
                topic.replyer = None
            topic.node = nodes[topic.node_id]
            yield topic


def get_full_replies(replies):
    users = get_cache_list(Member, (r.user_id for r in replies), 'member:')
    for reply in replies:
        if reply.user_id in users:
            reply.user = users[reply.user_id]
            yield reply


def reply_impact_for_topic(topic, reputation):
    if reputation < 2:
        return 0
    factor = int(options.reply_factor_for_topic)
    time_factor = int(options.reply_time_factor)
    time = datetime.utcnow() - topic.created
    factor += time.days * time_factor
    return factor * int(math.log(reputation))


def up_impact_for_topic(reputation):
    if reputation < 2:
        return 0
    factor = int(options.up_factor_for_topic)
    return factor * int(math.log(reputation))


def down_impact_for_topic(reputation):
    if reputation < 2:
        return 0
    factor = int(options.down_factor_for_topic)
    return factor * int(math.log(reputation))


def up_impact_for_user(reputation):
    if reputation < 2:
        return 0
    factor = int(options.up_factor_for_user)
    impact = factor * int(math.log(reputation))
    return min(impact, int(options.up_max_for_user))


def down_impact_for_user(reputation):
    if reputation < 2:
        return 0
    factor = int(options.down_factor_for_user)
    impact = factor * int(math.log(reputation))
    return min(impact, int(options.down_max_for_user))


def accept_reply_impact_for_user(reputation):
    if reputation < 2:
        return 0
    factor = int(options.accept_reply_factor_for_user)
    impact = factor * int(math.log(reputation))
    return min(impact, int(options.vote_max_for_user))
