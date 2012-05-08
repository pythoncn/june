import re
from july.cache import cache


def get_cache_list(model, id_list, key_prefix, time=600):
    if not id_list:
        return {}
    id_list = set(id_list)
    data = cache.get_multi(id_list, key_prefix=key_prefix)
    missing = id_list - set(data)
    if missing:
        dct = {}
        for item in model.query.filter_by(id__in=missing).all():
            dct[item.id] = item

        cache.set_multi(dct, time=time, key_prefix=key_prefix)
        data.update(dct)

    return data


def find_mention(text):
    regex = r'@(\w+)\s'
    return re.findall(regex, text)


def topiclink(topic, perpage=30):
    url = '/topic/%s' % topic.id
    num = (topic.reply_count - 1) / perpage + 1
    if not topic.reply_count:
        return url
    if num > 1:
        url += '?p=%s' % num

    url += '#reply%s' % topic.reply_count
    return url
