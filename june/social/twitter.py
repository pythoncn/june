from tornado import escape
from tornado.web import asynchronous
from tornado.options import options
from tornado.auth import TwitterMixin
from june.lib.decorators import require_user, require_system
from june.lib.handler import BaseHandler
from june.models import Social


class TwitterHandler(BaseHandler, TwitterMixin):
    def check_xsrf_cookie(self):
        # disable xsrf check
        return

    def _oauth_consumer_token(self):
        # reset method to get consumer token
        return {'key': options.twitter_key, 'secret': options.twitter_secret}

    @require_user
    @asynchronous
    def get(self):
        if 'twitter' in self.get_user_social(self.current_user.id):
            enabled = self.get_argument('enabled', 'a')
            if enabled not in ('y', 'n'):
                self.redirect('/account/setting')
                return
            q = self.db.query(Social).filter_by(service='twitter')
            t = q.filter_by(user_id=self.current_user.id).first()
            t.enabled = enabled
            self.db.add(t)
            self.db.commit()
            self.cache.delete('social:%s' % self.current_user.id)
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
        self.cache.delete('social:%s' % self.current_user.id)
        self.redirect('/account/setting')

    @require_system
    @asynchronous
    def post(self):
        content = self.get_argument('content', None)
        token = self.get_argument('token', None)
        if not (content and token):
            self.finish('deny')
            return
        token = escape.json_decode(token)
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
    ('/social/twitter', TwitterHandler),
]
