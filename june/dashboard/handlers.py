from tornado.web import URLSpec as url
from july.app import JulyApp
from july.util import ObjectDict
from july.database import db
from july.cache import cache

from june.account.decorators import require_admin
from june.account.models import Member
from june.account.lib import UserHandler
from june.node.models import Node
from june.topic.models import Topic, Reply


class DashMixin(object):
    def update_model(self, model, attr, required=False):
        value = self.get_argument(attr, '')
        if required and value:
            setattr(model, attr, value)
        elif not required:
            setattr(model, attr, value)


class EditStorage(UserHandler):
    @require_admin
    def post(self):
        self.set_storage('header', self.get_argument('header', ''))
        self.set_storage('sidebar', self.get_argument('sidebar', ''))
        self.set_storage('footer', self.get_argument('footer', ''))
        db.commit()
        self.reverse_redirect('dashboard')


class CreateNode(UserHandler):
    @require_admin
    def get(self):
        node = ObjectDict()
        self.render('admin/node.html', node=node)

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
            self.render('node.html', node=o)
            return

        node = Node(**o)

        db.session.add(node)
        db.session.commit()

        self.reverse_redirect('dashboard')


class EditNode(UserHandler, DashMixin):
    @require_admin
    def get(self, slug):
        node = Node.query.filter_by(slug=slug).first()
        if not node:
            self.send_error(404)
            return
        self.render('admin/node.html', node=node)

    @require_admin
    def post(self, slug):
        node = Node.query.filter_by(slug=slug).first()
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

        db.session.add(node)
        db.session.commit()

        self.redirect('/node/%s' % node.slug)


class FlushCache(UserHandler):
    @require_admin
    def get(self):
        cache.flush_all()
        self.write('done')


class EditMember(UserHandler, DashMixin):
    @require_admin
    def get(self, name):
        user = Member.query.filter_by(username=name).first_or_404()
        self.render('admin/member.html', user=user)

    @require_admin
    def post(self, name):
        user = Member.query.filter_by(username=name).first_or_404()
        self.update_model(user, 'username', True)
        self.update_model(user, 'email', True)
        self.update_model(user, 'role', True)
        self.update_model(user, 'reputation', True)
        db.session.add(user)
        db.session.commit()
        self.reverse_redirect('dashboard')


class EditTopic(UserHandler):
    @require_admin
    def get(self, id):
        topic = Topic.query.get_or_404(id)
        self.render('admin/topic.html', topic=topic)

    @require_admin
    def post(self, id):
        topic = Topic.query.get_or_404(id)
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
        db.session.add(topic)
        db.session.commit()
        self.redirect('/topic/%d' % topic.id)


class EditReply(UserHandler):
    @require_admin
    def get(self, id):
        reply = Reply.query.get_or_404(id)
        if self.get_argument('delete', 'false') == 'true':
            topic = Topic.query.filter_by(id=reply.topic_id).first()
            topic.reply_count -= 1
            db.session.add(topic)
            db.session.delete(reply)
            db.session.commit()
            self.reverse_redirect('dashboard')
            return
        self.render('admin/reply.html', reply=reply)

    @require_admin
    def post(self, id):
        reply = Reply.query.get_or_404(id)
        if not reply:
            self.send_error(404)
            return
        content = self.get_argument('content', '')
        reply.content = content
        db.session.add(reply)
        db.session.commit()
        self.reverse_redirect('dashboard')


class Dashboard(UserHandler):
    @require_admin
    def get(self):
        user = self.get_argument('user', None)
        if user:
            self.reverse_redirect('dashboard-member', user)
            return
        _cache_key = self.get_argument('cache', None)
        if _cache_key:
            cache.delete(str(_cache_key))
            self.reverse_redirect('dashboard')
            return
        nodes = Node.query.all()
        self.render('admin/index.html', nodes=nodes)


handlers = [
    url('/', Dashboard, name='dashboard'),
    ('/storage', EditStorage),
    ('/node', CreateNode),
    ('/node/(\w+)', EditNode),
    url('/member/(.*)', EditMember, name='dashboard-member'),
    ('/topic/(\d+)', EditTopic),
    ('/reply/(\d+)', EditReply),
    ('/flushcache', FlushCache),
]

app = JulyApp('dashboard', __name__, handlers=handlers,
              template_folder='templates')
