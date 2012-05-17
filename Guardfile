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

    uglifyjs('http://code.jquery.com/jquery.js', output)()

    github = 'https://raw.github.com'
    urls = [
        'assets/js/jquery.extends.js',
        '%s/jaz303/tipsy/master/src/javascripts/jquery.tipsy.js' % github,
        '%s/ichord/At.js/master/js/jquery.caret.js' % github,
        '%s/ichord/At.js/master/js/jquery.atwho.js' % github,
        '%s/chjj/marked/master/lib/marked.js' % github,
    ]
    for path in urls:
        uglifyjs(path, output, 'a')()


def site_js():
    from livereload.compiler import uglifyjs
    output = 'june/_static/js/site.js'
    uglifyjs('assets/js/editor.js', output)()

    urls = [
        'assets/js/site.js',
    ]
    for path in urls:
        uglifyjs(path, output, 'a')()


def site_css():
    from livereload.compiler import lessc, slimmer
    output = 'june/_static/css/site.css'
    lessc('assets/less/site.less', output)()
    pygments = 'http://flask.pocoo.org/docs/_static/pygments.css'

    github = 'https://raw.github.com'
    tipsy = '%s/jaz303/tipsy/master/src/stylesheets/tipsy.css' % github
    slimmer(pygments, output, 'a')()
    slimmer(tipsy, output, 'a')()


#: less tasks
Task.add('assets/less', site_css)


#: javascript tasks
Task.add('assets/js/', site_js)


#: html tasks
Task.add('june/_templates/*.html')
Task.add('june/_templates/snippet/*.html')
Task.add('june/_templates/module/*.html')
