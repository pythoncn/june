from tornado.util import ObjectDict
from june.lib.handler import BaseHandler
from june.lib.decorators import require_admin
from june.models import Node


class DashMixin(object):
    def update_model(self, model, attr):
        value = self.get_argument(attr, None)
        if value:
            setattr(model, attr, value)


class _Object(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        return None


class CreateNode(BaseHandler):
    @require_admin
    def get(self):
        node = _Object()
        self.render('dashboard_node.html', node=node)

    @require_admin
    def post(self):
        o = ObjectDict()
        o.title = self.get_argument('title', None)
        o.slug = self.get_argument('slug', None)
        o.avatar = self.get_argument('avatar', None)
        o.description = self.get_argument('description', None)
        o.fgcolor = self.get_argument('fgcolor', None)
        o.bgcolor = self.get_argument('bgcolor', None)
        o.header = self.get_argument('header', None)
        o.sidebar = self.get_argument('sidebar', None)
        o.footer = self.get_argument('footer', None)
        if not (o.slug and o.title and o.description):
            self.render('dashboard_node.html', node=o)
            return
        node = Node(**o)
        self.db.add(node)
        self.db.commit()
        self.redirect('/node/%s' % o.slug)


class EditNode(BaseHandler, DashMixin):
    @require_admin
    def get(self, slug):
        node = Node.query.filter_by(slug=slug).first()
        if not node:
            self.send_error(404)
            return
        self.render('dashboard_node.html', node=node)

    @require_admin
    def post(self, slug):
        node = self.db.query(Node).filter_by(slug=slug).first()
        if not node:
            self.send_error(404)
            return
        self.update_model(node, 'title')
        self.update_model(node, 'slug')
        self.update_model(node, 'avatar')
        self.update_model(node, 'description')
        self.update_model(node, 'fgcolor')
        self.update_model(node, 'bgcolor')
        self.update_model(node, 'header')
        self.update_model(node, 'sidebar')
        self.update_model(node, 'footer')
        self.db.add(node)
        self.db.commit()
        self.redirect('/node/%s' % node.slug)


handlers = [
    ('/dashboard/node', CreateNode),
    ('/dashboard/node/(\w+)', EditNode),
]
