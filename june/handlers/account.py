import tornado.web
from tornado.auth import GoogleMixin
from datetime import datetime
from june.lib.handler import BaseHandler
from june.lib import validators
from june.lib.util import ObjectDict
from june.auth.recaptcha import RecaptchaMixin
from june.models import Member, MemberLog, Topic, Notify


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
            msg = ObjectDict(header='Form Error',
                             body='Please fill the required field')
            self._context.message.append(msg)
            self.render('signin.html')
            return
        if '@' in account:
            user = Member.query.filter_by(email=account).first()
        else:
            user = Member.query.filter_by(username=account).first()
        if user and user.check_password(password):
            self.set_secure_cookie('user', '%s/%s' % (user.id, user.token))
            self.redirect(self.next_url)
            self.create_log(user.id)
            return
        msg = ObjectDict(header='Form Error',
                         body="Invalid account or password")
        self._context.message.append(msg)
        self.render('signin.html')

    def create_log(self, user_id):
        ip = self.request.remote_ip
        log = MemberLog(user_id=user_id, ip=ip, message='Signin')
        self.db.add(log)
        self.db.commit()


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
        self.create_log(user.id)
        self.redirect(self.next_url)

    def create_log(self, user_id):
        ip = self.request.remote_ip
        log = MemberLog(user_id=user_id, ip=ip, message='Google signin')
        self.db.add(log)
        self.db.commit()


class SignoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('user')
        self.redirect(self.next_url)


class SignupHandler(BaseHandler, RecaptchaMixin):
    def get(self):
        if self.current_user:
            return self.redirect(self.next_url)
        recaptcha = self.recaptcha_render()
        self.render('signup.html', email='', recaptcha=recaptcha)

    @tornado.web.asynchronous
    def post(self):
        email = self.get_argument('email', None)
        password1 = self.get_argument('password1', None)
        password2 = self.get_argument('password2', None)
        validate = True
        if not (email and password1 and password2):
            validate = False
            msg = ObjectDict(header='Form Error',
                             body='Please fill the required field')
            self._context.message.append(msg)

        if not validators.email(email):
            validate = False
            msg = ObjectDict(header='Email Error',
                             body='Not a valid email address')
            self._context.message.append(msg)

        if password1 != password2:
            validate = False
            msg = ObjectDict(header='Password Error',
                             body="Password doesn't match")
            self._context.message.append(msg)

        if not validate:
            recaptcha = self.recaptcha_render()
            self.render('signup.html', email=email, recaptcha=recaptcha)
            return

        member = Member.query.filter_by(email=email).first()
        if member:
            msg = ObjectDict(header='Form Error',
                             body="This email is already registered")
            self._context.message.append(msg)
            recaptcha = self.recaptcha_render()
            self.render('signup.html', email=email, recaptcha=recaptcha)
            return

        self.recaptcha_validate(self._on_validate)

    def _on_validate(self, response):
        email = self.get_argument('email', None)
        password = self.get_argument('password1', None)
        if not response:
            msg = ObjectDict(header='Captcha Error',
                             body='Captcha not valid')
            self._context.message.append(msg)
            recaptcha = self.recaptcha_render()
            self.render('signup.html', email=email, recaptcha=recaptcha)
            return
        user = self.create_user(email)
        user.password = user.create_password(password)
        self.db.add(user)
        self.db.commit()
        return self.redirect('/account/signin')


class SettingHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('setting.html')

    @tornado.web.authenticated
    def post(self):
        username = self.get_argument('username', None)
        website = self.get_argument('website', None)
        validate = True
        if not username:
            validate = False
            msg = ObjectDict(header='Form Error',
                             body='Please fill the required field')
            self._context.message.append(msg)

        if not validators.username(username):
            validate = False
            msg = ObjectDict(header='Username Error',
                             body="Username not valid, don't be evil")
            self._context.message.append(msg)

        if website and not validators.url(website):
            validate = False
            msg = ObjectDict(header='Website Error',
                             body="Website not valid, don't be evil")
            self._context.message.append(msg)

        if not validate:
            self.render('setting.html')
            return

        user = self.db.query(Member).filter_by(id=self.current_user.id).first()
        user.username = username
        user.website = website
        self.db.add(user)
        self.create_log(user.id)
        self.db.commit()
        self.cache.delete_multi([user.id, user.username], key_prefix='member:')
        self.redirect('/account/setting')

    def create_log(self, user_id):
        ip = self.request.remote_ip
        log = MemberLog(user_id=user_id, ip=ip, message='Edit account')
        self.db.add(log)


class NotifyHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.db.query(Member).filter_by(id=self.current_user.id).first()
        notify = Notify.query.filter_by(receiver=user.id).order_by('-id')[:20]
        user.last_notify = datetime.utcnow()
        self.db.add(user)
        self.db.commit()
        self.cache.set('member:%s' % user.id, user, 600)
        self.cache.delete('notify:%s' % user.id)
        self.render('notify.html', notify=notify)


class MemberHandler(BaseHandler):
    def get(self, name):
        user = self.get_user_by_name(name)
        if not user:
            self.send_error(404)
            return
        topics = Topic.query.filter_by(user_id=user.id).order_by('-id')[:20]
        self.render('member.html', user=user, topics=topics)


handlers = [
    ('/account/signin', SigninHandler),
    ('/account/signin/google', GoogleSigninHandler),
    ('/account/signout', SignoutHandler),
    ('/account/signup', SignupHandler),
    ('/account/setting', SettingHandler),
    ('/account/notify', NotifyHandler),
    ('/member/(\w+)', MemberHandler),
]
