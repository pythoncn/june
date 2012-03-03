import tornado.web
from tornado.auth import GoogleMixin
from june.lib.handler import BaseHandler
from june.lib import validators
from june.models import Member, MemberMixin


class SigninHandler(BaseHandler):
    def get(self):
        if self.current_user:
            self.redirect(self.next_url)
            return
        self.render('signin.html')

    def post(self):
        account = self.get_argument('account', None)
        password = self.get_argument('password', None)
        if not (account and password):
            self._context.message = 'Please fill the required field'
            self.render('signin.html')
            return
        if '@' in account:
            user = Member.query.filter_by(email=account).first()
        else:
            user = Member.query.filter_by(username=account).first()
        if user and user.check_password(password):
            self.set_secure_cookie('user', '%s/%s' % (user.id, user.token))
            self.redirect(self.next_url)
            return
        self._context.message = "Invalid account or password"
        self.render('signin.html')


class GoogleSigninHandler(BaseHandler, GoogleMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.current_user:
            self.redirect(self.next_url)
            return
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect(ax_attrs=["email"])

    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Google auth failed")
        email = user["email"].lower()
        user = Member.query.filter_by(email=email).first()
        if not user:
            user = Member(email)
            user.password = '!'
            self.db.add(user)
            self.db.commit()

        self.set_secure_cookie('user', '%s/%s' % (user.id, user.token))
        self.redirect(self.next_url)


class SignoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('user')
        self.redirect(self.next_url)


class SignupHandler(BaseHandler):
    def get(self):
        self.render('signup.html')


class SettingHandler(BaseHandler, MemberMixin):
    @tornado.web.authenticated
    def get(self):
        self.render('setting.html')

    @tornado.web.authenticated
    def post(self):
        username = self.get_argument('username', None)
        website = self.get_argument('website', None)
        if not username:
            self._context.message = 'Please fill the required field'
            self.render('setting.html')
            return

        if not validators.username(username):
            self._context.message = "Don't be evil"
            self.render('setting.html')
            return

        if website and not validators.url(website):
            self._context.message = "Don't be evil"
            self.render('setting.html')
            return

        user = self.db.query(Member).filter_by(id=self.current_user.id).first()
        user.username = username
        user.website = website
        self.db.add(user)
        self.db.commit()
        self.cache.delete_multi([user.id, user.username], key_prefix='member:')
        self.redirect('/account/setting')


class MemberHandler(BaseHandler, MemberMixin):
    def get(self, name):
        user = self.get_user_by_name(name)
        if not user:
            self.send_error(404)
            return
        self.render('member.html', user=user)


handlers = [
    ('/account/signin', SigninHandler),
    ('/account/signin/google', GoogleSigninHandler),
    ('/account/signout', SignoutHandler),
    ('/account/signup', SignupHandler),
    ('/account/setting', SettingHandler),
    ('/member/(\w+)', MemberHandler),
]
