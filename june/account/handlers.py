import time
import datetime
import hashlib
import base64
from tornado.web import authenticated, asynchronous
from tornado.auth import GoogleMixin
from tornado.options import options
from july.app import JulyApp
from july.database import db
from july.auth.recaptcha import RecaptchaMixin
from .lib import UserHandler, get_full_notifications
from .models import Member, Notification
from .decorators import require_user
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
            db.session.add(user)
            db.session.commit()
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
        user = Member.query.get(self.current_user.id)
        user.token = user.create_token(16)
        db.session.add(user)
        db.session.commit()
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
        db.session.add(user)
        db.session.commit()
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
        self.render('setting.html')

    @authenticated
    def post(self):
        username = self.get_argument('username', None)
        if not username:
            self.flash_message('Please fill the required fields', 'error')
            self.render('setting.html')
            return

        if not validators.username(username):
            self.flash_message('Username is invalid', 'error')
            self.render('setting.html')
            return

        website = self.get_argument('website', '')
        if website and not validators.url(website):
            self.flash_message('Website is invalid', 'error')
            self.render('setting.html')
            return

        user = Member.query.get(self.current_user.id)

        user.city = self.get_argument('city', '')
        user.description = self.get_argument('description', '')
        user.website = website

        if user.username != username:
            if not user.edit_username_count:
                self.flash_message("You can't edit username", 'warn')
                self.redirect('/account/setting')
                return

            if Member.query.filter_by(username=username).count() > 0:
                self.flash_message('Username has been taken', 'error')
                self.render('setting.html')
                return

            user.username = username
            user.edit_username_count -= 1

        db.session.add(user)
        db.session.commit()
        self.redirect('/account/setting')


class NotificationHandler(UserHandler):
    @authenticated
    def get(self):
        user = Member.query.get(self.current_user.id)
        messages = Notification.query.filter_by(receiver=user.id)\
                .order_by('-id')[:20]
        messages = get_full_notifications(messages)
        self.render('notification.html', messages=messages)

        #: after render, modify user.last_notify
        user.last_notify = datetime.datetime.utcnow()
        db.session.add(user)
        db.session.commit()

    @authenticated
    def post(self):
        #: mark all as read
        messages = Notification.query.filter_by(readed='n')\
                .filter_by(receiver=self.current_user.id).all()
        for msg in messages:
            msg.readed = 'y'
            db.session.add(msg)

        db.session.commit()
        self.write({'stat': 'ok'})

    @authenticated
    def delete(self):
        #: delete all
        for msg in Notification.query.filter_by(receiver=self.current_user.id):
            db.session.delete(msg)

        db.session.commit()
        self.write({'stat': 'ok'})


class PasswordHandler(UserHandler):
    """Password

    - GET: 1. form view 2. verify link from email
    - POST: 1. send email to find password. 2. change password
    """
    def get(self):
        token = self.get_argument('verify', None)
        if token and self._verify_token(token):
            self.render('password.html', token=token)
            return

        if not self.current_user:
            self.redirect('/account/signin')
            return
        self.render('password.html', token=None)

    def post(self):
        action = self.get_argument('action', None)
        if action == 'email':
            self.send_password_email()
            return
        password = self.get_argument('password', None)
        if password:
            self.change_password()
            return
        self.find_password()

    def send_password_email(self):
        email = self.get_argument('email', None)
        if self.current_user:
            user = self.current_user
        elif not email:
            self.flash_message("Please fill the required fields", "error")
            self.redirect('/account/signin')
            return
        else:
            user = Member.query.get_first(email=email)
            if not user:
                self.flash_message("User does not exists", "error")
                self.redirect('/account/signin')
                return

        token = self._create_token(user)
        url = '%s/account/password?verify=%s' % \
                (options.siteurl, token)
        self.write(url)
        #TODO

    @authenticated
    def change_password(self):
        user = Member.query.get_or_404(self.current_user.id)
        password = self.get_argument('password', None)
        if not user.check_password(password):
            self.flash_message("Invalid password", "error")
            self.render('password.html', token=None)
            return
        password1 = self.get_argument('password1', None)
        password2 = self.get_argument('password2', None)
        self._change_password(user, password1, password2)

    def find_password(self):
        token = self.get_argument('token', None)
        if not token:
            self.redirect('/account/password')
            return
        user = self._verify_token(token)
        if not user:
            self.redirect('/account/password')
            return
        password1 = self.get_argument('password1', None)
        password2 = self.get_argument('password2', None)
        self._change_password(user, password1, password2)

    def _change_password(self, user, password1, password2):
        if password1 != password2:
            self.flash_message("Password doesn't match", 'error')
            self.render('password.html', token=None)
            return
        user.password = user.create_password(password1)
        user.token = user.create_token(16)
        db.session.add(user)
        db.session.commit()
        self.flash_message('Password changed', 'info')
        self.set_secure_cookie('user', '%s/%s' % (user.id, user.token))
        self.redirect('/account/password')

    def _create_token(self, user):
        salt = user.create_token(8)
        created = str(int(time.time()))
        hsh = hashlib.sha1(salt + created + user.token).hexdigest()
        token = "%s|%s|%s|%s" % (user.email, salt, created, hsh)
        return base64.b64encode(token)

    def _verify_token(self, token):
        try:
            token = base64.b64decode(token)
        except:
            self.flash_message("Don't be evil", 'error')
            return None
        splits = token.split('|')
        if len(splits) != 4:
            self.flash_message("Don't be evil", 'error')
            return None
        email, salt, created, hsh = splits
        delta = time.time() - int(created)
        if delta < 1:
            self.flash_message("Don't be evil", 'error')
            return None
        if delta > 600:
            self.flash_message('This link is expired, request again', 'warn')
            # 10 minutes
            return None
        user = Member.query.get_first(email=email)
        if not user:
            return None
        if hsh == hashlib.sha1(salt + created + user.token).hexdigest():
            return user
        self.flash_message("Don't be evil", 'error')
        return None


class MessageHandler(UserHandler):
    @require_user
    def post(self):
        receiver = self.get_argument('username', None)
        content = self.get_argument('content', None)
        if not (receiver and content):
            self.flash_message('Please fill the required fields', 'error')
        else:
            self.create_notification(receiver, content, '', type='message')
            db.session.commit()

        self.redirect(self.next_url)


handlers = [
    ('/signup', SignupHandler),
    ('/signin', SigninHandler),
    ('/signin/google', GoogleSigninHandler),
    ('/signout', SignoutHandler),
    ('/setting', SettingHandler),
    ('/signout/everywhere', SignoutEverywhereHandler),
    ('/delete', DeleteAccountHandler),
    ('/notification', NotificationHandler),
    ('/password', PasswordHandler),
    ('/message', MessageHandler),
]


app = JulyApp('account', __name__, handlers=handlers)
