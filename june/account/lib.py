import datetime
from tornado.options import options
from junetornado import JuneHandler
from junetornado.util import ObjectDict
from june.account.models import MemberMixin


class UserHandler(JuneHandler, MemberMixin):
    def finish(self, chunk=None):
        super(UserHandler, self).finish(chunk)
        if self.get_status() == 500:
            try:
                self.db.commit()
            except:
                self.db.rollback()
            finally:
                self.db.commit()

    def prepare(self):
        self._prepare_context()
        self._prepare_filters()

    def render_string(self, template_name, **kwargs):
        kwargs.update(self._filters)
        assert "context" not in kwargs, "context is a reserved keyword."
        kwargs["context"] = self._context
        return super(UserHandler, self).render_string(template_name, **kwargs)

    def get_current_user(self):
        cookie = self.get_secure_cookie("user")
        if not cookie:
            return None
        try:
            id, token = cookie.split('/')
            id = int(id)
        except:
            self.clear_cookie("user")
            return None
        user = self.get_user_by_id(id)
        if not user:
            return None
        if token == user.token:
            return user
        self.clear_cookie("user")
        return None

    def is_owner_of(self, model):
        if not hasattr(model, 'user_id'):
            return False
        if not self.current_user:
            return False
        return model.user_id == self.current_user.id

    @property
    def next_url(self):
        next_url = self.get_argument("next", None)
        return next_url or '/'

    def _prepare_context(self):
        self._context = ObjectDict()
        self._context.now = datetime.datetime.utcnow()
        #self._context.version = june.__version__
        self._context.version = ''
        self._context.sitename = options.sitename
        self._context.siteurl = options.siteurl
        self._context.sitefeed = options.sitefeed
        self._context.sidebar = ''
        self._context.footer = ''
        self._context.header = ''
        self._context.ga = options.ga
        self._context.gcse = options.gcse
        self._context.debug = options.debug
        self._context.message = []

    def _prepare_filters(self):
        self._filters = ObjectDict()
        #self._filters.xmldatetime = xmldatetime
        #self._filters.topiclink = topiclink
        self._filters.get_user = self.get_user_by_id
        self._filters.is_mobile = lambda f=None: False

    def create_message(self, header, body):
        msg = ObjectDict(header=header, body=body)
        self._context.message.append(msg)
