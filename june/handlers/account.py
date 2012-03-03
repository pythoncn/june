import tornado.web
from tornado.auth import GoogleMixin
from june.lib.handler import BaseHandler
from june.models import Member


class SigninHandler(BaseHandler):
    def get(self):
        if self.current_user:
            self.redirect(self.next_url)
            return
        self.render('signin.html', message=None)

    def post(self):
        account = self.get_argument('account', None)
        password = self.get_argument('password', None)
        if not (account and password):
            message = "Please fill the form"
            self.render('signin.html', message=message)
            return
        if '@' in account:
            user = Member.query.filter_by(email=account).first()
        else:
            user = Member.query.filter_by(username=account).first()
        if user and user.check_password(password):
            self.set_secure_cookie('user', '%s/%s' % (user.id, user.token))
            self.redirect(self.next_url)
            return
        message = "Invalid Account or Password"
        self.render('signin.html', message=message)


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
            user = Member(email.split('@')[0], email)
            user.password = 'google'
            self.db.add(user)
            self.db.commit()

        self.set_secure_cookie('user', '%s/%s' % (user.id, user.token))
        self.redirect(self.next_url)


class SignoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('user')
        self.redirect(self.next_url)


class SettingHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('setting.html')

    @tornado.web.authenticated
    def post(self):
        username = self.get_argument('username', None)
        website = self.get_argument('website', None)
        if not username:
            self.render('setting.html')
            return
        user = self.db.query(Member).filter_by(id=self.current_user.id).first()
        user.username = username
        user.website = website
        self.db.add(user)
        self.db.commit()
        self.redirect('/account/setting')


class MemberHandler(BaseHandler):
    def get(self, name):
        user = Member.query.filter_by(username=name).first()
        if not user:
            self.send_error(404)
            return
        self.render('member.html', user=user)


handlers = [
    ('/account/signin', SigninHandler),
    ('/account/signin/google', GoogleSigninHandler),
    ('/account/signout', SignoutHandler),
    ('/account/setting', SettingHandler),
    ('/member/(\w+)', MemberHandler),
]
