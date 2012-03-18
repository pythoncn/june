import urllib
from tornado import escape
from tornado.web import asynchronous
from tornado.options import options
from tornado.auth import httpclient
from june.lib.decorators import require_user, require_system
from june.auth.twitter import TweetMixin
from june.lib.handler import BaseHandler
from june.models import Social

active_services = []
if hasattr(options, 'twitter_key') and hasattr(options, 'twitter_secret'):
    active_services.append('twitter')


def register_service(name, user_id, content):
    if name not in active_services:
        return
    http = httpclient.AsyncHTTPClient()
    url = 'http://127.0.0.1:%s/social/%s' % (options.port, name)
    post_args = {'user': user_id, 'content': escape.utf8(content)}
    http.fetch(url, method="POST", body=urllib.urlencode(post_args),
               callback=None)


class TwitterHandler(BaseHandler, TweetMixin):
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

    def check_xsrf_cookie(self):
        # disable xsrf check
        return

    @require_system
    @asynchronous
    def post(self):
        content = self.get_argument('content', None)
        user_id = self.get_argument('user', None)
        if not (content and user_id):
            self.finish('deny')
            return
        networks = self.get_user_social(user_id)
        if 'twitter' not in networks:
            self.finish('deny')
            return
        twitter = networks['twitter']
        if twitter['enabled'] != 'y':
            self.finish('deny')
            return
        token = escape.json_decode(twitter['token'])
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
twitter_service = ('/social/twitter', TwitterHandler)


handlers = []
if 'twitter' in active_services:
    handlers.append(twitter_service)
