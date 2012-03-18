import logging
import functools
import urlparse


class require_role(object):
    def __init__(self, role):
        self.role = role

    def __call__(self, method):
        @functools.wraps(method)
        def wrapper(handler, *args, **kwargs):
            if not handler.current_user:
                url = handler.get_login_url()
                if '?' not in url:
                    if urlparse.urlsplit(url).scheme:
                        next_url = handler.request.full_url()
                    else:
                        next_url = handler.request.uri
                    url += '?next=' + next_url
                return handler.redirect(url)
            user = handler.current_user
            if user.role == 1:
                return handler.redirect('/account/verify')
            if user.role == 0:
                return handler.redirect('/doc/guideline')
            if user.role < self.role:
                return handler.send_error(403)
            return method(handler, *args, **kwargs)
        return wrapper

require_user = require_role(2)
require_staff = require_role(6)
require_admin = require_role(9)


class cache(object):
    """Cache decorator, an easy way to manage cache.
    The result key will be like: prefix:arg1-arg2k1#v1k2#v2
    """
    def __init__(self, prefix, time=0):
        self.prefix = prefix
        self.time = time

    def __call__(self, method):
        @functools.wraps(method)
        def wrapper(handler, *args, **kwargs):
            if not hasattr(handler, 'cache'):
                # fix for UIModule
                handler.cache = handler.handler.cache
            if not handler.cache:
                return method(handler, *args, **kwargs)

            if args:
                key = self.prefix + ':' + '-'.join(str(a) for a in args)
            else:
                key = self.prefix
            if kwargs:
                for k, v in kwargs.iteritems():
                    key += '%s#%s' % (k, v)

            value = handler.cache.get(key)
            if value is None:
                value = method(handler, *args, **kwargs)
                try:
                    handler.cache.set(key, value, self.time)
                except:
                    logging.warn('cache error: %s' % key)
                    pass
            return value
        return wrapper


def require_system(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.request.remote_ip != '127.0.0.1':
            self.send_error(403)
            return
        return method(self, *args, **kwargs)
    return wrapper
