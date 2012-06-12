import re


def find_mention(text):
    regex = r'@(\w+)\s'
    return re.findall(regex, text)


def force_int(num, default=1):
    try:
        return int(num)
    except:
        return default
