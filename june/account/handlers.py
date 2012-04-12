import logging
import urllib
import tornado.web
from datetime import datetime
from tornado.auth import httpclient
from tornado.options import options
from tornado.auth import GoogleMixin

from june.account.lib import UserHandler
from june.lib import validators
from june.lib.util import ObjectDict, PageMixin
from june.account.models import Member, MemberLog, Notify
from june.account.models import MemberMixin, create_token
from june.social import services


class RecaptchaMixin(object):
    RECAPTCHA_VERIFY_URL = "http://www.google.com/recaptcha/api/verify"

    def recaptcha_render(self):
        token = self._recaptcha_token()
        html = ('<div id="recaptcha_div"></div><script type="text/javascript" '
                'src="http://www.google.com/recaptcha/api/js/recaptcha_ajax.js'
                '"></script><script type="text/javascript">Recaptcha.create'
                '("%(key)s", "recaptcha_div", {theme: "%(theme)s",callback:'
                'Recaptcha.focus_response_field});</script>')
        return html % token

    def recaptcha_validate(self, callback):
        token = self._recaptcha_token()
        challenge = self.get_argument('recaptcha_challenge_field', None)
        response = self.get_argument('recaptcha_response_field', None)
        callback = self.async_callback(self._on_recaptcha_request, callback)
        http = httpclient.AsyncHTTPClient()
        post_args = {
            'privatekey': token['secret'],
            'remoteip': self.request.remote_ip,
            'challenge': challenge,
            'response': response
        }
        http.fetch(self.RECAPTCHA_VERIFY_URL, method="POST",
                   body=urllib.urlencode(post_args), callback=callback)

    def _on_recaptcha_request(self, callback, response):
        if response.error:
            logging.warning("Error response %s fetching %s", response.error,
                    response.request.url)
            callback(None)
            return
        verify, message = response.body.split()
        if verify == 'true':
            callback(response.body)
        else:
            logging.warning("Recaptcha verify failed %s", message)
            callback(None)

    def _recaptcha_token(self):
        token = dict(
            key=options.recaptcha_key,
            secret=options.recaptcha_secret,
            theme=options.recaptcha_theme,
        )
        return token


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
            self.create_message('Form Error', 'Please fill the required field')
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
        self.create_message('Form Error', "Invalid account or password")
        self.render('signin.html')

    def create_log(self, user_id):
        ip = self.request.remote_ip
        log = MemberLog(user_id=user_id, ip=ip, message='Signin')
        self.db.add(log)
        self.db.commit()


class GoogleSigninHandler(UserHandler, GoogleMixin):
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
            user = self.create_user(email)
            user.password = '!'
            self.db.add(user)
            self.db.commit()
            self.cache.delete('status')

        self.set_secure_cookie('user', '%s/%s' % (user.id, user.token))
        self.create_log(user.id)
        self.redirect(self.next_url)

    def create_log(self, user_id):
        ip = self.request.remote_ip
        log = MemberLog(user_id=user_id, ip=ip, message='Google signin')
        self.db.add(log)
        self.db.commit()


class SignoutHandler(UserHandler):
    def get(self):
        self.clear_cookie('user')
        self.redirect(self.next_url)


class SignoutEverywhereHandler(UserHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.db.query(Member).get(self.current_user.id)
        user.token = create_token(16)
        self.db.add(user)
        self.db.commit()
        self.cache.delete('member:%s' % user.id)
        self.redirect(self.next_url)


class SignupHandler(UserHandler, RecaptchaMixin):
    def head(self):
        pass

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
        if not (email and password1 and password2):
            self.create_message('Form Error', 'Please fill the required field')
            recaptcha = self.recaptcha_render()
            self.render('signup.html', email=email, recaptcha=recaptcha)
            return

        validate = True
        if not validators.email(email):
            validate = False
            self.create_message('Form Error', 'Not a valid email address')

        if password1 != password2:
            validate = False
            self.create_message('Form Error', "Password doesn't match")

        if not validate:
            recaptcha = self.recaptcha_render()
            self.render('signup.html', email=email, recaptcha=recaptcha)
            return

        member = Member.query.filter_by(email=email).first()
        if member:
            self.create_message('Form Error',
                                "This email is already registered")
            recaptcha = self.recaptcha_render()
            self.render('signup.html', email=email, recaptcha=recaptcha)
            return

        self.recaptcha_validate(self._on_validate)

    def _on_validate(self, response):
        email = self.get_argument('email', None)
        password = self.get_argument('password1', None)
        if not response:
            self.create_message('Form Error', 'Captcha not valid')
            recaptcha = self.recaptcha_render()
            self.render('signup.html', email=email, recaptcha=recaptcha)
            return
        user = self.create_user(email)
        user.password = user.create_password(password)
        self.db.add(user)
        self.db.commit()
        self.cache.delete('status')
        self.set_secure_cookie('user', '%s/%s' % (user.id, user.token))
        return self.redirect(self.next_url)


class SettingHandler(UserHandler):
    @tornado.web.authenticated
    def get(self):
        self._setting_render()

    def _setting_render(self):
        q = MemberLog.query.filter_by(user_id=self.current_user.id)
        logs = q.order_by('-id').limit(5)
        networks = self.get_user_social(self.current_user.id)
        self.render('setting.html', logs=logs,
                    services=services, networks=networks)

    @tornado.web.authenticated
    def post(self):
        username = self.get_argument('username', None)
        website = self.get_argument('website', None)
        if not username:
            self.create_message('Form Error', 'Please fill the required field')
            self._setting_render()
            return

        if not validators.username(username):
            self.create_message('Form Error',
                                "Username not valid, don't be evil")
            self._setting_render()
            return

        if website and not validators.url(website):
            self.create_message('Form Error',
                                "Website not valid, don't be evil")
            self._setting_render()
            return

        user = self.get_user_by_name(username)
        if user and user.id != self.current_user.id:
            self.create_message('Form Error',
                                "Username is registered by other member")
            self._setting_render()
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


class NotifyHandler(UserHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.db.query(Member).get(self.current_user.id)
        notify = Notify.query.filter_by(receiver=user.id).order_by('-id')[:20]
        self.render('notify.html', notify=notify)

        key1 = 'notify:%s' % user.id
        key2 = 'member:%s' % user.id
        self.cache.delete_multi([key1, key2])
        user.last_notify = datetime.utcnow()
        self.db.add(user)
        self.db.commit()


class MemberHandler(UserHandler):
    def head(self, name):
        pass

    def get(self, name):
        user = self.get_user_by_name(name)
        if not user:
            self.send_error(404)
            return
        self.render('member.html', user=user)


class MemberListHandler(UserHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('member_list.html')


urls = [
    ('/signin', SigninHandler),
    ('/signin/google', GoogleSigninHandler),
    ('/signout', SignoutHandler),
    ('/signout/everywhere', SignoutEverywhereHandler),
    ('/signup', SignupHandler),
    ('/setting', SettingHandler),
    ('/notify', NotifyHandler),
]

handlers = [
    ('/member/(\w+)', MemberHandler),
    ('/members', MemberListHandler),
]


class MemberModule(tornado.web.UIModule, MemberMixin):
    def render(self, user, tpl='module/member.html'):
        key = 'notify:%s' % user.id
        notify = self.handler.cache.get(key)
        if notify is None:
            q = Notify.query.filter_by(receiver=user.id)
            notify = q.filter_by(created__gt=user.last_notify).count()
            self.handler.cache.set(key, notify, 600)
        html = self.render_string(tpl, user=user, notify=notify)
        return html


class MemberListModule(tornado.web.UIModule, PageMixin):
    def render(self, tpl='module/member_list.html'):
        p = self._get_page()
        key = 'MemberListModule:%s' % p
        html = self.handler.cache.get(key)
        if html is not None:
            return html

        page = self._get_pagination(
            Member.query.order_by('-reputation'),
            perpage=30)
        page = ObjectDict(page)
        html = self.render_string(tpl, page=page)
        self.handler.cache.set(key, html, 600)
        return html


ui_modules = {
    'MemberModule': MemberModule,
    'MemberListModule': MemberListModule,
}
