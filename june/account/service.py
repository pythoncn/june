from tornado import escape
from tornado.web import asynchronous
from tornado.options import options
from tornado.auth import TwitterMixin
from july.database import db
from july.app import JulyApp
from .decorators import require_user, require_system
from .lib import UserHandler, get_social_map
from .models import Social


class TwitterHandler(UserHandler, TwitterMixin):
    def check_xsrf_cookie(self):
        # disable xsrf check
        return

    def _oauth_consumer_token(self):
        # reset method to get consumer token
        return {'key': options.twitter_key, 'secret': options.twitter_secret}

    @require_user
    @asynchronous
    def get(self):
        user = self.current_user
        networks = get_social_map(user.id)
        if 'twitter' in networks:
            enabled = self.get_argument('enabled', 'a')
            if enabled not in ('y', 'n'):
                self.redirect('/account/setting')
                return
            twitter = networks['twitter']
            twitter.enabled = enabled
            db.master.add(twitter)
            db.master.commit()
            self.redirect('/account/setting')
            return
        if self.get_argument('oauth_token', None):
            self.get_authenticated_user(self._on_auth)
            return
        self.authorize_redirect()

    def _on_auth(self, user):
        if not user:
            self.write('Twitter auth failed')
            self.finish()
            return
        access_token = escape.json_encode(user['access_token'])
        network = Social(service='twitter', user_id=self.current_user.id,
                         token=access_token)
        self.db.add(network)
        self.db.commit()
        self.redirect('/account/setting')

    @require_system
    @asynchronous
    def post(self):
        content = self.get_argument('content', None)
        user_id = self.get_argument('user', None)
        if not (content and user_id):
            self.finish('deny')
            return
        network = Social.query.get_first(service='twitter', user_id=user_id)
        if not network:
            self.finish('deny')
            return
        token = escape.json_decode(network.token)
        status = escape.utf8(content)
        self.twitter_request(
            '/statuses/update',
            post_args={'status': status},
            access_token=token,
            callback=self._on_post)

    def _on_post(self, entry):
        if not entry:
            self.finish('fail')
            return
        self.finish('ok')


handlers = [
    ('/twitter', TwitterHandler),
]

app = JulyApp('social', __name__, handlers=handlers)
