from june.lib.util import ObjectDict
from june.lib.handler import BaseHandler
from june.lib.decorators import require_admin
from june.models import Member, Node, NodeMixin


class DashMixin(object):
    def update_model(self, model, attr, required=False):
        value = self.get_argument(attr, '')
        if required and value:
            setattr(model, attr, value)
        elif not required:
            setattr(model, attr, value)


class CreateNode(BaseHandler):
    @require_admin
    def get(self):
        node = ObjectDict()
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
        o.footer = self.get_argument('limit_reputation', 0)
        o.footer = self.get_argument('limit_role', 0)
        try:
            o.limit_reputation = int(self.get_argument('reputation', 0))
        except:
            o.limit_reputation = 0

        try:
            o.limit_role = int(self.get_argument('role', 0))
        except:
            o.limit_role = 0

        if not (o.slug and o.title and o.description):
            self._context.message = 'Please fill the required field'
            self.render('dashboard_node.html', node=o)
            return
        node = Node(**o)
        self.db.add(node)
        self.db.commit()
        self.redirect('/dashboard')


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
        self.update_model(node, 'title', True)
        self.update_model(node, 'slug', True)
        self.update_model(node, 'avatar')
        self.update_model(node, 'description', True)
        self.update_model(node, 'fgcolor')
        self.update_model(node, 'bgcolor')
        self.update_model(node, 'header')
        self.update_model(node, 'sidebar')
        self.update_model(node, 'footer')
        self.update_model(node, 'limit_reputation')
        self.update_model(node, 'limit_role')
        self.db.add(node)
        self.db.commit()

        self.cache.delete('node:%s' % str(slug))
        self.redirect('/node/%s' % node.slug)


class FlushCache(BaseHandler):
    @require_admin
    def get(self):
        self.cache.flush_all()
        self.write('done')


class EditMember(BaseHandler, DashMixin):
    @require_admin
    def get(self, name):
        user = Member.query.filter_by(username=name).first()
        if not user:
            self.send_error(404)
            return
        self.render('dashboard_member.html', user=user)

    @require_admin
    def post(self, name):
        user = self.db.query(Member).filter_by(username=name).first()
        if not user:
            self.send_error(404)
            return
        self.update_model(user, 'username', True)
        self.update_model(user, 'email', True)
        self.update_model(user, 'role', True)
        self.update_model(user, 'reputation', True)
        self.db.add(user)
        self.db.commit()
        self.cache.delete('user:%s' % str(user.id))
        self.redirect('/dashboard')


class Dashboard(BaseHandler, NodeMixin):
    @require_admin
    def get(self):
        user = self.get_argument('user', None)
        if user:
            self.redirect('/dashboard/member/%s' % user)
            return
        nodes = Node.query.all()
        self.render('dashboard.html', nodes=nodes)


handlers = [
    ('/dashboard', Dashboard),
    ('/dashboard/node', CreateNode),
    ('/dashboard/node/(\w+)', EditNode),
    ('/dashboard/member/(\w+)', EditMember),
    ('/dashboard/flushcache', FlushCache),
]
