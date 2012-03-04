import re
import markdown
from tornado import escape
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer


def safe_markdown(text):
    text = escape.xhtml_escape(text)

    # get link back
    text = re.sub(r'&lt;(http.*?)&gt;', r'<\1>', text)

    pattern = re.compile(r'```(\w+)(.+?)```', re.S)
    formatter = HtmlFormatter(noclasses=False)

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
    return markdown.markdown(text)
