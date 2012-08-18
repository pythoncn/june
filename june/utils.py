import re

def import_object(name, arg=None):
    if '.' not in name:
        return __import__(name)
    parts = name.split('.')
    obj = __import__('.'.join(parts[:-1]), None, None, [parts[-1]], 0)
    return getattr(obj, parts[-1], arg)

def find_mention(text):
    regex = r'@(\w+)\s'
    return re.findall(regex, text)
