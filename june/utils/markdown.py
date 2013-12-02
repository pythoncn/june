# coding: utf-8
"""
    june.utils.markdown
    ~~~~~~~~~~~~~~~~~~~

    Markdown parser for June.

    :copyright: (c) 2013 by Hsiaoming Yang
"""

import re
import misaka as m
from markupsafe import escape
from jinja2 import Markup
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


class AutolinkRenderer(m.HtmlRenderer):
    def autolink(self, link, is_email):
        if is_email:
            return Markup(
                '<a href="mailto:%(link)s">%(link)s</a>' % {'link': link}
            )
        title = link.replace('http://', '').replace('https://', '')

        #: youtube.com
        pattern = r'http://www\.youtube\.com\/watch\?v=([a-zA-Z0-9\-\_]+)'
        match = re.match(pattern, link)
        if not match:
            pattern = r'http:\/\/youtu.be\/([a-zA-Z0-9\-\_]+)'
            match = re.match(pattern, link)
        if match:
            value = (
                '<iframe width="560" height="315" src='
                '"http://www.youtube.com/embed/%(id)s" '
                'frameborder="0" allowfullscreen></iframe>'
                '<div><a rel="nofollow" href="%(link)s">'
                '%(title)s</a></div>'
            ) % {'id': match.group(1), 'link': link, 'title': title}
            return Markup(value)

        #: gist support
        pattern = r'(https?:\/\/gist\.github\.com\/.+\d+)'
        match = re.match(pattern, link)
        if match:
            value = (
                '<script src="%(link)s.js"></script>'
                '<div><a rel="nofollow" href="%(link)s">'
                '%(title)s</a></div>'
            ) % {'link': match.group(1), 'title': title}
            return Markup(value)

        #: vimeo.com
        pattern = r'https?:\/\/vimeo\.com\/([\d]+)'
        match = re.match(pattern, link)
        if match:
            value = (
                '<iframe width="566" height="318" frameborder="0" '
                'src="https://player.vimeo.com/video/%(id)s" '
                'allowFullScreen></iframe>'
                '<div><a rel="nofollow" href="%(link)s">'
                '%(title)s</a></div>'
            ) % {'id': match.group(1), 'link': link, 'title': title}
            return Markup(value)

        #: ascii.io
        pattern = r'(http:\/\/ascii\.io\/a\/\d+)'
        match = re.match(pattern, link)
        if match:
            value = (
                '<iframe width="566" height="600" frameborder="0" '
                'src="%(url)s/raw" '
                'allowFullScreen></iframe>'
                '<div><a rel="nofollow" href="%(link)s">'
                '%(title)s</a></div>'
            ) % {'url': match.group(1), 'link': link, 'title': title}
            return Markup(value)

    def paragraph(self, text):
        pattern = re.compile(r'\s@(\w+)')
        text = pattern.sub(r' @<a href="/user/\1">\1</a>', text)
        pattern = re.compile(r'^@(\w+)')
        text = pattern.sub(r'@<a href="/user/\1">\1</a>', text)
        return Markup('<p>%s</p>' % text)


class HighlightRenderer(AutolinkRenderer):
    def block_code(self, text, lang):
        if not lang:
            return Markup('<pre><code>%s</code></pre>' % escape(text))

        inlinestyles = False
        linenos = False
        if hasattr(self, '_inlinestyles'):
            inlinestyles = self._inlinestyles
        if hasattr(self, '_linenos'):
            linenos = self._linenos

        try:
            lexer = get_lexer_by_name(lang, stripall=True)
            formatter = HtmlFormatter(
                noclasses=inlinestyles, linenos=linenos
            )
            return Markup(highlight(text, lexer, formatter))
        except:
            return Markup('<pre class="%s"><code>%s</code></pre>' % (
                lang, escape(text)
            ))


class PlainRenderer(AutolinkRenderer):
    def header(self, text, level):
        return Markup('<div class="md-h%d">%s</div>' % (level, text))


def markdown(text, renderer='highlight', inlinestyles=False, linenos=False):
    """Markdown filter for writeup.

    :param text: the content to be markdownify
    :param renderer: choose a renderer, default is HighlightRenderer
    :param inlinestyles: highlight the code with inline styles
    :param linenos: show linenos of the highlighted code
    """
    if not text:
        return u''
    if renderer == 'highlight':
        r = HighlightRenderer()
        r._inlinestyles = inlinestyles
        r._linenos = linenos
    elif renderer == 'plain':
        r = PlainRenderer()
    else:
        r = AutolinkRenderer()

    extensions = (
        m.EXT_NO_INTRA_EMPHASIS | m.EXT_FENCED_CODE | m.EXT_AUTOLINK |
        m.EXT_TABLES | m.EXT_STRIKETHROUGH | m.EXT_SUPERSCRIPT
    )
    md = m.Markdown(r, extensions=extensions)
    return md.render(text)
