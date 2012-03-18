from tornado.auth import TwitterMixin
from tornado.options import options


class TweetMixin(TwitterMixin):
    def _oauth_consumer_token(self):
        return {'key': options.twitter_key, 'secret': options.twitter_secret}
