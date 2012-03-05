import functools
from tornado import ioloop, stack_context
from tornado.options import define, options


def parse_config_file(path):
    config = {}
    exec(compile(open(path).read(), path, 'exec'), config, config)
    for name in config:
        if name in options:
            options[name].set(config[name])
        else:
            define(name, config[name])


class ObjectDict(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        return None

    def __setattr__(self, key, value):
        self[key] = value


def delay_call(func, *arg, **kwargs):
    with stack_context.NullContext():
        io = ioloop.IOLoop.instance()
        io.add_callback(functools.partial(func, *arg, **kwargs))


class PageMixin(object):
    def _get_order(self):
        order = self.get_argument('o', '0')
        if order == '1':
            return '-id'
        return '-impact'

    def _get_page(self):
        page = self.get_argument('p', '1')
        try:
            return int(page)
        except:
            return 1

    def _get_pagination(self, q, count=None):
        if hasattr(options, 'perpage'):
            perpage = int(options.perpage)
        else:
            perpage = 20

        page = self._get_page()
        start = (page - 1) * perpage
        end = page * perpage
        if not count:
            count = q.count()

        dct = {}
        page_number = (count - 1) / perpage + 1  # this algorithm is fabulous
        dct['page_number'] = page_number
        dct['datalist'] = q[start:end]
        dct['pagelist'] = range(1, page_number + 1)
        dct['current_page'] = page
        dct['item_number'] = count
        return dct
