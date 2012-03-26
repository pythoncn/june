import os.path
from tornado.options import options
from june.backend import Backend


class LocalBackend(Backend):
    def save(self, body, filename, callback=None):
        path = os.path.join(options.local_backend_path, filename)
        f = open(path, 'w')
        f.write(body)
        f.close()
        if not callback:
            return
        callback(os.path.join(options.local_backend_url, filename))
        return
