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
            if not user.username:
                handler.flash_message('Please setup a username', 'warn')
                return handler.redirect('/account/setting')
            if user.role == 1:
                handler.flash_message('Please verify your email', 'warn')
                return handler.redirect('/account/setting')
            if user.role < 1:
                return handler.redirect('/doc/guideline')
            if user.role < self.role:
                return handler.send_error(403)
            return method(handler, *args, **kwargs)
        return wrapper

require_user = require_role(2)
require_staff = require_role(6)
require_admin = require_role(9)


def require_system(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.request.remote_ip != '127.0.0.1':
            self.send_error(403)
            return
        return method(self, *args, **kwargs)
    return wrapper
