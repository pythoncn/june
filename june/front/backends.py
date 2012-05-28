import os.path
import base64
import functools
from tornado.options import options
from tornado import httpclient


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


class Upyun(object):
    def __init__(self, bucket_with_dir, username, password, static_url=None):
        _ = bucket_with_dir.split('/')
        bucket = _[0]
        self.url = 'http://v0.api.upyun.com/' + bucket_with_dir + '/'
        self.username = username
        self.password = password
        self.static_url = 'http://%s.b0.upaiyun.com/%s/' \
                % (bucket, '/'.join(_[1:]))
        if static_url:
            self.static_url = self.static_url

    def basic_auth_header(self):
        auth = base64.b64encode('%s:%s' % (self.username, self.password))
        headers = {'Authorization': 'Basic %s' % auth}
        return headers

    def signature_auth_header(self):
        #TODO
        pass

    def get_usage(self, callback=None):
        url = self.url + '?usage'
        http = httpclient.AsyncHTTPClient()
        http.fetch(url, method='GET', headers=self.basic_auth_header(),
                   callback=callback)
        return

    def upload(self, body, filename, callback=None):
        url = self.url + filename
        http = httpclient.AsyncHTTPClient()
        http.fetch(
            url, method='PUT', headers=self.basic_auth_header(), body=body,
            callback=functools.partial(self._on_upload, callback, filename))
        return

    def _on_upload(self, callback, filename, response):
        if not callback:
            return
        if response.error:
            callback(None)
            return
        callback(self.static_url + filename)
        return


class UpyunBackend(object):
    @staticmethod
    def save(body, filename, callback):
        upyun = Upyun(options.upyun_bucket, options.upyun_username,
                      options.upyun_password)
        if hasattr(options, 'upyun_static_url'):
            upyun.static_url = options.upyun_static_url
        upyun.upload(body, filename, callback)
        return
