import re


def regex(pattern, data, flags=0):
    if isinstance(pattern, basestring):
        pattern = re.compile(pattern, flags)

    return pattern.match(data)


def email(data):
    pattern = r'^.+@[^.].*\.[a-z]{2,10}$'
    return regex(pattern, data, re.IGNORECASE)


def url(data):
    pattern = (r'^https?://([^/:]+\.[a-z]{2,10}|([0-9]{1,3}\.){3}'
               '[0-9]{1,3})(:[0-9]+)?(\/.*)?$')
    return regex(pattern, data, re.IGNORECASE)


def username(data):
    pattern = r'^[a-zA-Z0-9]+$'
    return regex(pattern, data)
