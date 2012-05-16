#!/usr/bin/env python

#: Guardfile for livereload
#: http://lepture.com/project/livereload/

#: TODO
# https://raw.github.com/jaz303/tipsy/master/src/stylesheets/tipsy.css
# https://github.com/ichord/At.js/raw/master/css/jquery.atwho.css

from livereload.task import Task
from livereload.compiler import lessc, uglifyjs


def lib_js():
    from livereload.compiler import UglifyJSCompiler
    output = 'june/_static/js/lib.js'

    js = UglifyJSCompiler('http://code.jquery.com/jquery.js')
    js.write(output)

    github = 'https://raw.github.com'
    urls = [
        '%s/jaz303/tipsy/master/src/javascripts/jquery.tipsy.js' % github,
    ]
    for path in urls:
        js = UglifyJSCompiler(path)
        js.append(output)


def at_js():
    from livereload.compiler import UglifyJSCompiler
    github = 'https://raw.github.com/ichord/At.js/master/js'
    output = 'june/_static/js/at.js'
    js = UglifyJSCompiler('%s/jquery.caret.js' % github)
    js.write(output)
    js = UglifyJSCompiler('%s/jquery.atwho.js' % github)
    js.append(output)


def editor_js():
    from livereload.compiler import UglifyJSCompiler
    static = 'assets/js/editor'
    output = 'june/_static/js/editor.js'
    UglifyJSCompiler(
        'https://raw.github.com/chjj/marked/master/lib/marked.js'
    ).write(output)
    #UglifyJSCompiler('%s/upload.js' % static).append(output)
    UglifyJSCompiler('%s/editor.js' % static).append(output)


#: less tasks
Task.add(
    'assets/less',
    lessc('assets/less/site.less', 'june/_static/css/site.css')
)


#: javascript tasks
Task.add('assets/js/editor/', editor_js)
Task.add(
    'assets/js/site.js',
    uglifyjs('assets/js/site.js', 'june/_static/js/site.js')
)


#: html tasks
Task.add('june/_templates/*.html')
Task.add('june/_templates/snippet/*.html')
Task.add('june/_templates/module/*.html')
