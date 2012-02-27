import re
import datetime
import logging
from tornado.web import RequestHandler
from tornado.options import options
from tornado.util import ObjectDict
from tornado import escape

from june.models import Member


class BaseHandler(RequestHandler):
    _first_run = True

    def initialize(self):
        if BaseHandler._first_run:
            logging.info('First Run')
            BaseHandler._first_run = False

    def finish(self, chunk=None):
        super(BaseHandler, self).finish(chunk)
        if self.get_status() == 500:
            try:
                self.db.commit()
            except:
                self.db.rollback()
            finally:
                self.db.commit()

    @property
    def db(self):
        return self.application.db

    @property
    def cache(self):
        return self.application.cache

    def prepare(self):
        self._prepare_context()
        self._prepare_filters()
        options.tforms_locale = self.locale

    def render_string(self, template_name, **kwargs):
        kwargs.update(self._filters)
        assert "context" not in kwargs, "context is a reserved keyword."
        kwargs["context"] = self._context
        return super(BaseHandler, self).render_string(template_name, **kwargs)

    def write(self, chunk):
        if isinstance(chunk, dict):
            chunk = escape.json_encode(chunk)
            callback = self.get_argument('callback', None)
            if callback:
                chunk = "%s(%s)" % (callback, escape.to_unicode(chunk))
                self.set_header("Content-Type",
                                "application/javascript; charset=UTF-8")
            else:
                self.set_header("Content-Type",
                                "application/json; charset=UTF-8")
        super(BaseHandler, self).write(chunk)

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
        user = Member.query.filter_by(id=id).first()
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
        self._context.sitename = options.sitename
        self._context.version = options.version
        self._context.debug = options.debug
        self._context.ga = options.ga

        self._context.get_msg = self.get_msg

    def _prepare_filters(self):
        self._filters = ObjectDict()

    def set_msg(self, msg):
        expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
        self.set_cookie('msg', msg, expires=expires)
        return msg

    def get_msg(self):
        msg = self.get_cookie('msg', None)
        if msg:
            self.clear_cookie('msg')
        return msg

    def is_system(self):
        return self.request.remote_ip == '127.0.0.1'

    def is_mobile(self):
        _mobile = ('ipod|iphone|android|blackberry|palm|nokia|symbian|',
                   'samsung|psp|kindle|phone|mobile|ucweb|opera mini|fennec')
        return True if re.search(_mobile, self.user_agent.lower()) else False

    def is_spider(self):
        _spider = 'bot|crawl|spider|slurp|search|lycos|robozilla|fetcher'
        return True if re.search(_spider, self.user_agent.lower()) else False

    def is_ajax(self):
        return "XMLHttpRequest" == self.request.headers.get("X-Requested-With")

    @property
    def user_agent(self):
        return self.request.headers.get("User-Agent", "bot")
