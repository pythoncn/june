import os.path
from tornado.options import options
from july.auth.upyun import BaseUpyun


class LocalBackend(object):
    @staticmethod
    def save(body, filename, callback=None):
        path = os.path.join(options.local_static_path, filename)
        f = open(path, 'w')
        f.write(body)
        f.close()
        if not callback:
            return
        callback(os.path.join(options.local_static_url, filename))
        return


class UpyunBackend(object):
    @staticmethod
    def save(body, filename, callback):
        upyun = BaseUpyun(
            options.upyun_bucket, options.upyun_username,
            options.upyun_password
        )
        if 'upyun_static_url' in options:
            upyun.static_url = options.upyun_static_url
        upyun.upload(body, filename, callback)
        return
