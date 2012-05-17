#!/usr/bin/env python

#: Guardfile for livereload
#: http://lepture.com/project/livereload/

#: TODO
# https://raw.github.com/jaz303/tipsy/master/src/stylesheets/tipsy.css
# https://github.com/ichord/At.js/raw/master/css/jquery.atwho.css

from livereload.task import Task


def lib_js():
    from livereload.compiler import uglifyjs
    output = 'june/_static/js/lib.js'

    uglifyjs('http://code.jquery.com/jquery.js', output)

    github = 'https://raw.github.com'
    urls = [
        '%s/jaz303/tipsy/master/src/javascripts/jquery.tipsy.js' % github,
    ]
    for path in urls:
        uglifyjs(path, output, 'a')


def at_js():
    from livereload.compiler import uglifyjs
    github = 'https://raw.github.com/ichord/At.js/master/js'
    output = 'june/_static/js/at.js'

    uglifyjs('%s/jquery.caret.js' % github, output)
    uglifyjs('%s/jquery.atwho.js' % github, output, 'a')


def editor_js():
    from livereload.compiler import uglifyjs
    static = 'assets/js/editor'
    output = 'june/_static/js/editor.js'
    marked = 'https://raw.github.com/chjj/marked/master/lib/marked.js'
    uglifyjs(marked, output)
    uglifyjs('%s/editor.js' % static, output, 'a')


def site_css():
    from livereload.compiler import lessc, slimmer
    output = 'june/_static/css/site.css'
    lessc('assets/less/site.less', output)
    pygments = 'http://flask.pocoo.org/docs/_static/pygments.css'
    slimmer(pygments, output, 'a')


#: less tasks
Task.add('assets/less', site_css)


#: javascript tasks
Task.add('assets/js/editor/', editor_js)


#: html tasks
Task.add('june/_templates/*.html')
Task.add('june/_templates/snippet/*.html')
Task.add('june/_templates/module/*.html')
