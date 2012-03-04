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
