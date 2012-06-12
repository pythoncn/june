import tornado.web
from tornado.web import UIModule
from july.app import JulyApp
from july.database import db
from june.account.lib import UserHandler
from .models import FollowNode, Node


class FollowNodeHandler(UserHandler):
    """Toggle following"""

    @tornado.web.authenticated
    def post(self, slug):
        node = Node.query.filter_by(slug=slug).first_or_404()

        user = self.current_user
        follow = FollowNode.query.get_first(user_id=user.id, node_id=node.id)
        if follow:
            db.session.delete(follow)
            db.session.commit()
            self.write({'stat': 'ok', 'data': 'unfollow'})
            return
        follow = FollowNode(user_id=self.current_user.id, node_id=node.id)
        db.session.add(follow)
        db.session.commit()
        self.write({'stat': 'ok', 'data': 'follow'})


class NodeListHandler(UserHandler):
    def head(self):
        pass

    def get(self):
        nodes = Node.query.order_by('-updated').all()
        self.render('node_list.html', nodes=nodes)


app_handlers = [
    ('/(\w+)/follow', FollowNodeHandler),
]


class NodeModule(UIModule):
    def render(self, node):
        user = self.handler.current_user
        if not user:
            following = False
        elif FollowNode.query.get_first(user_id=user.id, node_id=node.id):
            following = True
        else:
            following = False

        return self.render_string('module/node.html', node=node,
                                  following=following)


class FollowingNodesModule(UIModule):
    def render(self, user_id):
        fs = FollowNode.query.filter_by(user_id=user_id).values('node_id')
        node_ids = (f[0] for f in fs)
        nodes = Node.query.filter_by(id__in=node_ids).all()
        return self.render_string('module/node_list.html', nodes=nodes)


class RecentAddNodesModule(UIModule):
    def render(self):
        nodes = Node.query.order_by('-id')[:20]
        return self.render_string('module/node_list.html', nodes=nodes)


app_modules = {
    'Node': NodeModule,
    'FollowingNodes': FollowingNodesModule,
    'RecentAddNodes': RecentAddNodesModule,
}

app = JulyApp('node', __name__, handlers=app_handlers, ui_modules=app_modules)
