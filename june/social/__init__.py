import urllib
from tornado import escape
from tornado import httpclient
from tornado.options import options

services = []
handlers = []
if hasattr(options, 'twitter_key') and hasattr(options, 'twitter_secret'):
    services.append('twitter')
    from june.social import twitter
    handlers.extend(twitter.handlers)


def register(networks, content):
    for name in networks:
        if name not in services:
            return
        service = networks[name]
        if service['enabled'] != 'y':
            return
        http = httpclient.AsyncHTTPClient()
        url = 'http://127.0.0.1:%s/social/%s' % (options.port, name)
        post_args = {'token': service['token'],
                     'content': escape.utf8(content)}
        http.fetch(url, method="POST", body=urllib.urlencode(post_args),
                   callback=None)
