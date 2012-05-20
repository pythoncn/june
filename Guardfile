#!/usr/bin/env python

#: Guardfile for livereload
#: http://lepture.com/project/livereload/

#: TODO
# https://github.com/ichord/At.js/raw/master/css/jquery.atwho.css

from livereload.task import Task


def lib_js():
    from livereload.compiler import uglifyjs
    output = 'june/_static/js/lib.js'

    uglifyjs('http://code.jquery.com/jquery.js', output)()

    github = 'https://raw.github.com'
    urls = [
        'assets/js/jquery.extends.js',
        '%s/jaz303/tipsy/master/src/javascripts/jquery.tipsy.js' % github,
    ]
    for path in urls:
        uglifyjs(path, output, 'a')()


def editor_js():
    from livereload.compiler import uglifyjs
    output = 'june/_static/js/editor.js'
    marked = 'https://raw.github.com/chjj/marked/master/lib/marked.js'
    uglifyjs(marked, output)()
    uglifyjs('assets/js/editor.js', output, 'a')()


def topic_js():
    from livereload.compiler import uglifyjs
    output = 'june/_static/js/topic.js'
    github = 'https://raw.github.com/ichord/At.js/master/js'
    uglifyjs('%s/jquery.caret.js' % github, output)()
    uglifyjs('%s/jquery.atwho.js' % github, output, 'a')()
    uglifyjs('assets/js/topic.js', output, 'a')()


def site_js():
    from livereload.compiler import uglifyjs
    output = 'june/_static/js/site.js'
    uglifyjs('assets/js/site.js', output)()


def site_css():
    from livereload.compiler import lessc, slimmer
    output = 'june/_static/css/site.css'
    lessc('assets/less/site.less', output)()
    pygments = 'http://flask.pocoo.org/docs/_static/pygments.css'

    github = 'https://raw.github.com'
    tipsy = '%s/jaz303/tipsy/master/src/stylesheets/tipsy.css' % github
    atwho = '%s/ichord/At.js/master/css/jquery.atwho.css' % github
    slimmer(pygments, output, 'a')()
    slimmer(tipsy, output, 'a')()
    slimmer(atwho, output, 'a')()


#: less tasks
Task.add('assets/less', site_css)


#: javascript tasks
Task.add('assets/js/site.js', site_js)
Task.add('assets/js/editor.js', editor_js)
Task.add('assets/js/topic.js', topic_js)


#: html tasks
Task.add('june/_templates/*.html')
Task.add('june/_templates/snippet/*.html')
Task.add('june/_templates/module/*.html')
