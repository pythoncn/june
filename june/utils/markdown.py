# coding: utf-8
"""
    june.markdown
    ~~~~~~~~~~~~~

    Markdown parser for June.

    :copyright: (c) 2013 by Hsiaoming Yang
"""

import re
import misaka as m
from markupsafe import escape
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


class AutolinkRenderer(m.HtmlRenderer):
    def autolink(self, link, is_email):
        if is_email:
            return '<a href="mailto:%(link)s">%(link)s</a>' % {'link': link}
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
            return value

        #: gist support
        pattern = r'(https?:\/\/gist\.github\.com\/.+\d+)'
        match = re.match(pattern, link)
        if match:
            value = (
                '<script src="%(link)s.js"></script>'
                '<div><a rel="nofollow" href="%(link)s">'
                '%(title)s</a></div>'
            ) % {'link': match.group(1), 'title': title}
            return value

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
            return value

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
            return value


class HighlightRenderer(AutolinkRenderer):
    def block_code(self, text, lang):
        if not lang:
            return u'<pre><code>%s</code></pre>' % escape(text)

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
            return highlight(text, lexer, formatter)
        except:
            return '<pre class="%s"><code>%s</code></pre>' % (
                lang, escape(text)
            )


def markdown(text, highlight=True, inlinestyles=False, linenos=False):
    """Markdown filter for writeup.

    :param text: the content to be markdownify
    :param highlight: highlight the code block or not
    :param inlinestyles: highlight the code with inline styles
    :param linenos: show linenos of the highlighted code
    """
    if not text:
        return u''
    if highlight:
        renderer = HighlightRenderer()
        renderer._inlinestyles = inlinestyles
        renderer._linenos = linenos
    else:
        renderer = AutolinkRenderer()

    extensions = (
        m.EXT_NO_INTRA_EMPHASIS | m.EXT_FENCED_CODE | m.EXT_AUTOLINK |
        m.EXT_TABLES | m.EXT_STRIKETHROUGH | m.EXT_SUPERSCRIPT
    )
    md = m.Markdown(renderer, extensions=extensions)
    return md.render(text)
