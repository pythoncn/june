import datetime
from tornado.web import authenticated, asynchronous
from tornado.auth import GoogleMixin
from july.app import JulyApp
from july.database import db
from july.auth.recaptcha import RecaptchaMixin
from .lib import UserHandler
from .models import Member, Profile, Notification
from . import validators


class SigninHandler(UserHandler):
    def head(self):
        pass

    def get(self):
        if self.current_user:
            self.redirect(self.next_url)
            return
        self.render('signin.html')

    def post(self):
        account = self.get_argument('account', None)
        password = self.get_argument('password', None)
        if not (account and password):
            self.flash_message('Please fill the required fields', 'error')
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
        self.flash_message('Invalid account or password', 'error')
        self.render('signin.html')


class GoogleSigninHandler(UserHandler, GoogleMixin):
    @asynchronous
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
            self.send_error(500)
            return
        email = user["email"].lower()
        user = Member.query.filter_by(email=email).first()
        if not user:
            user = Member(email)
            user.password = '!'
            db.master.add(user)
            db.master.commit()
            self.set_secure_cookie('user', '%s/%s' % (user.id, user.token))
            self.redirect('/account/setting')
            return

        self.set_secure_cookie('user', '%s/%s' % (user.id, user.token))
        self.redirect(self.next_url)
        return


class SignoutHandler(UserHandler):
    def get(self):
        self.clear_cookie('user')
        self.redirect(self.next_url)


class SignoutEverywhereHandler(UserHandler):
    @authenticated
    def get(self):
        user = db.master.query(Member).get(self.current_user.id)
        user.token = user.create_token(16)
        db.master.add(user)
        db.master.commit()
        self.redirect(self.next_url)


class SignupHandler(UserHandler, RecaptchaMixin):
    def head(self):
        pass

    def get(self):
        if self.current_user:
            return self.redirect(self.next_url)
        recaptcha = self.recaptcha_render()
        self.render('signup.html', username='', email='', recaptcha=recaptcha)

    @asynchronous
    def post(self):
        email = self.get_argument('email', '')
        password1 = self.get_argument('password1', None)
        password2 = self.get_argument('password2', None)
        if not (email and password1 and password2):
            self.flash_message('Please fill the required fields', 'error')
            recaptcha = self.recaptcha_render()
            self.render('signup.html', email=email, recaptcha=recaptcha)
            return

        if password1 != password2:
            self.flash_message("Password doesn't match", 'error')
            recaptcha = self.recaptcha_render()
            self.render('signup.html', email=email, recaptcha=recaptcha)
            return

        if not validators.email(email):
            self.flash_message('Not a valid email address', 'error')
            recaptcha = self.recaptcha_render()
            self.render('signup.html', email=email, recaptcha=recaptcha)
            return

        member = Member.query.filter_by(email=email).first()
        if member:
            self.flash_message("This email is already registered", 'warn')
            recaptcha = self.recaptcha_render()
            self.render('signup.html', email=email, recaptcha=recaptcha)
            return

        self.recaptcha_validate(self._on_validate)

    def _on_validate(self, response):
        email = self.get_argument('email', '')
        password = self.get_argument('password1', None)
        if not response:
            self.flash_message('Captcha not valid', 'error')
            recaptcha = self.recaptcha_render()
            self.render('signup.html', email=email, recaptcha=recaptcha)
            return
        user = Member(email)
        user.password = user.create_password(password)
        db.master.add(user)
        db.master.commit()
        self.set_secure_cookie('user', '%s/%s' % (user.id, user.token))
        self.redirect('/account/setting')  # account information
        return


class DeleteAccountHandler(UserHandler):
    @authenticated
    def post(self):
        password = self.get_argument('password', None)
        if not password:
            self.flash_message('Please fill the required fields', 'warn')
            #: TODO
            return
        if not self.current_user.check_password(password):
            self.flash_message('Invalid password', 'error')
            #: TODO
            return


class SettingHandler(UserHandler):
    @authenticated
    def get(self):
        profile = Profile.query.get_first(user_id=self.current_user.id)
        self.render('setting.html', profile=profile)

    @authenticated
    def post(self):
        profile = Profile.query.get_first(user_id=self.current_user.id)
        username = self.get_argument('username', None)
        if not username:
            self.flash_message('Please fill the required fields', 'error')
            self.render('setting.html', profile=profile)
            return

        if not validators.username(username):
            self.flash_message('Username is invalid', 'error')
            self.render('setting.html', profile=profile)
            return

        website = self.get_argument('website', '')
        if website and not validators.url(website):
            self.flash_message('Website is invalid', 'error')
            self.render('setting.html', profile=profile)
            return

        #: edit profile
        if not profile:
            profile = Profile(user_id=self.current_user.id,
                              edit_username_count=2)

        profile.city = self.get_argument('city', '')
        profile.description = self.get_argument('description', '')

        if self.current_user.username == username:
            user = Member.query.get(self.current_user.id)
            user.website = website
            db.master.add(user)
            db.master.add(profile)
            db.master.commit()
            self.redirect('/account/setting')
            return

        #: changed username
        if not profile.edit_username_count:
            self.flash_message("You can't edit username", 'warn')
            self.render('setting.html', profile=profile)
            return

        if Member.query.filter_by(username=username).count() > 0:
            self.flash_message('Username has been taken', 'error')
            self.render('setting.html', profile=profile)
            return

        profile.edit_username_count -= 1
        db.master.add(profile)

        user = Member.query.get(self.current_user.id)
        user.username = username
        user.website = website
        user.role = 2
        db.master.add(user)
        db.master.commit()
        self.redirect('/account/setting')


class NotificationHandler(UserHandler):
    @authenticated
    def get(self):
        user = Member.query.get(self.current_user.id)
        messages = Notification.query.filter_by(receiver=user.id)\
                .order_by('-id')[:20]
        self.render('notification.html', messages=messages)

        #: after render, modify user.last_notify
        user.last_notify = datetime.datetime.utcnow()
        db.master.add(user)
        db.master.commit()

    @authenticated
    def delete(self):
        pass

handlers = [
    ('/signup', SignupHandler),
    ('/signin', SigninHandler),
    ('/signin/google', GoogleSigninHandler),
    ('/signout', SignoutHandler),
    ('/setting', SettingHandler),
    ('/signout/everywhere', SignoutEverywhereHandler),
    ('/delete', DeleteAccountHandler),
    ('/notification', NotificationHandler),
]

app = JulyApp('account', __name__, handlers=handlers)
