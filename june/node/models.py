from datetime import datetime
from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime
from june.config import db


class Node(db.Model):
    title = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False, index=True)
    avatar = Column(String(400))
    description = Column(String(1000))
    fgcolor = Column(String(40))
    bgcolor = Column(String(40))
    header = Column(String(2000))
    sidebar = Column(String(2000))
    footer = Column(String(2000))
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow,
                     onupdate=datetime.utcnow)
    limit_reputation = Column(Integer, default=0)
    limit_role = Column(Integer, default=2)
    topic_count = Column(Integer, default=0)


class FollowNode(db.Model):
    user_id = Column(Integer, nullable=False, index=True)
    node_id = Column(Integer, nullable=False, index=True)
    created = Column(DateTime, default=datetime.utcnow)


class NodeMixin(object):
    def get_node_by_id(self, id):
        return Node.query.filter_by(id=id).first()

    def get_node_by_slug(self, slug):
        return Node.query.filter_by(slug=slug).first()

    def get_all_nodes(self):
        nodes = Node.query.all()
        nodes = sorted(nodes, key=lambda o: o.updated, reverse=True)
        return nodes

    def get_nodes(self, id_list):
        return None
        #return get_cache_list(self, Node, id_list, 'node:')

    def follow_node(self, node_id):
        if not self.current_user:
            return 0
        nodes = self.get_user_follow_nodes(self.current_user.id)
        if node_id in nodes:
            return node_id
        nodes.append(node_id)
        user = self.current_user
        self.cache.set('follownode:%s' % user.id, nodes, 6000)
        f = FollowNode(user_id=user.id, node_id=node_id)
        self.db.add(f)
        return node_id

    def get_user_follow_nodes(self, user_id):
        q = FollowNode.query.filter_by(user_id=user_id).values('node_id')
        nodes = []
        for values in q:
            nodes.append(values[0])
        return nodes

    def is_user_follow_node(self, user_id, node_id):
        # should query again ?
        return node_id in self.get_user_follow_nodes(user_id)
