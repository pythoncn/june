# coding: utf-8
import re
import markdown
from tornado import escape
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer


def safe_markdown(text, noclasses=False):
    text = escape.xhtml_escape(text)

    # get link back
    def make_link(m):
        link = m.group(1)
        title = link.replace('http://', '').replace('https://', '')
        if len(title) > 30:
            title = title[:20] + '...'
        if link.startswith('http://') or link.startswith('https://'):
            return '<a href="%s" rel="nofollow">%s</a>' % (link, title)
        return '<a href="http://%s" rel="nofollow">%s</a>' % (link, title)

    # http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    pattern = re.compile(
        r'(?m)^((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}'
        r'/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+'
        r'|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))')
    text = pattern.sub(make_link, text)

    pattern = re.compile(
        r'(?i)(?:&lt;)((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}'
        r'/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+'
        r'|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))(?:&gt;)')

    text = pattern.sub(make_link, text)

    pattern = re.compile(r'```(\w+)(.+?)```', re.S)
    formatter = HtmlFormatter(noclasses=noclasses)

    def repl(m):
        try:
            name = m.group(1)
            lexer = get_lexer_by_name(name)
        except ValueError:
            name = 'text'
            lexer = TextLexer()
        text = m.group(2).replace('&quot;', '"').replace('&amp;', '&')
        text = text.replace('&lt;', '<').replace('&gt;', '>')
        #text = m.group(2)
        code = highlight(text, lexer, formatter)
        code = code.replace('\n\n', '\n&nbsp;\n').replace('\n', '<br />')
        tpl = '\n\n<div class="code" data-syntax="%s">%s</div>\n\n'
        return tpl % (name, code)

    text = pattern.sub(repl, text)
    pattern = re.compile(r'@(\w+)')
    text = pattern.sub(r'<a href="/member/\1">@\1</a>', text)
    return markdown.markdown(text)


def find_mention(text):
    regex = r'@(\w+)'
    return re.findall(regex, text)


def xmldatetime(value):
    return value.strftime('%Y-%m-%dT%H:%M:%SZ')
