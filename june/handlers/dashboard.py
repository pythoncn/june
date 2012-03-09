from june.lib.util import ObjectDict
from june.lib.handler import BaseHandler
from june.lib.decorators import require_admin
from june.models import Topic, Member, Node, NodeMixin, TopicMixin


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
        self.render('dashboard/node.html', node=node)

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
        try:
            o.limit_reputation = int(self.get_argument('reputation', 0))
        except:
            o.limit_reputation = 0

        try:
            o.limit_role = int(self.get_argument('role', 0))
        except:
            o.limit_role = 0

        if not (o.slug and o.title and o.description):
            self.create_message('Form Error', 'Please fill the required field')
            self.render('dashboard/node.html', node=o)
            return
        node = Node(**o)
        self.db.add(node)
        self.db.commit()
        self.cache.delete('allnodes')
        self.redirect('/dashboard')


class EditNode(BaseHandler, DashMixin):
    @require_admin
    def get(self, slug):
        node = Node.query.filter_by(slug=slug).first()
        if not node:
            self.send_error(404)
            return
        self.render('dashboard/node.html', node=node)

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

        try:
            node.limit_reputation = int(self.get_argument('reputation', 0))
        except:
            node.limit_reputation = 0

        try:
            node.limit_role = int(self.get_argument('role', 0))
        except:
            node.limit_role = 0

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
        self.render('dashboard/member.html', user=user)

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


class EditTopic(BaseHandler, TopicMixin):
    @require_admin
    def get(self, id):
        topic = self.get_topic_by_id(id)
        if not topic:
            self.send_error(404)
            return
        self.render('dashboard/topic.html', topic=topic)

    @require_admin
    def post(self, id):
        topic = self.db.query(Topic).filter_by(id=id).first()
        if not topic:
            self.send_error(404)
            return
        impact = self.get_argument('impact', None)
        node = self.get_argument('node', None)
        try:
            topic.impact = int(impact)
        except:
            pass
        try:
            topic.node_id = int(node)
        except:
            pass
        self.db.add(topic)
        self.db.commit()
        self.cache.delete('topic:%s' % topic.id)
        self.redirect('/topic/%d' % topic.id)


class Dashboard(BaseHandler, NodeMixin):
    @require_admin
    def get(self):
        user = self.get_argument('user', None)
        if user:
            self.redirect('/dashboard/member/%s' % user)
            return
        nodes = Node.query.all()
        self.render('dashboard/index.html', nodes=nodes)


handlers = [
    ('/dashboard', Dashboard),
    ('/dashboard/node', CreateNode),
    ('/dashboard/node/(\w+)', EditNode),
    ('/dashboard/member/(.*)', EditMember),
    ('/dashboard/topic/(\d+)', EditTopic),
    ('/dashboard/flushcache', FlushCache),
]
