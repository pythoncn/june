import re


def find_mention(text):
    regex = r'@(\w+)\s'
    return re.findall(regex, text)


def force_int(num, default=1):
    try:
        return int(num)
    except:
        return default


class Pagination(object):
    def __init__(self, page, perpage, total):
        self.page = page
        self.perpage = perpage
        self.total = total

        self.start = (page - 1) * perpage
        self.end = page * perpage

        self.page_count = (total - 1) / perpage + 1

    @property
    def page_range(self):
        page = self.page
        page_count = self.page_count

        if page < 5:
            return range(1, min(page_count, 9) + 1)
        if page + 4 > page_count:
            return range(max(page_count - 8, 1), page_count + 1)

        return range(page - 4, min(page_count, page + 4) + 1)
