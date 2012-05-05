#!/usr/bin/env python

#: Guardfile for livereload
#: http://lepture.com/project/livereload/

from livereload.task import Task
from livereload.compiler import lessc, uglifyjs


def less_all():
    from livereload.compiler import LessCompiler
    less = LessCompiler('assets/less/mobile.less')
    less.write('june/_static/css/mobile.css')


def js_lib():
    import glob
    from livereload.compiler import UglifyJSCompiler
    output = 'june/_static/js/lib.js'
    js = UglifyJSCompiler('assets/js/lib/jquery.js')
    js.write(output)
    files = glob.glob('assets/js/lib/*.js')
    files.remove('assets/js/lib/jquery.js')
    for path in files:
        js = UglifyJSCompiler(path)
        js.append(output)


def js_at():
    from livereload.compiler import UglifyJSCompiler
    static = 'assets/resources/At.js/js'
    output = 'june/_static/js/at.js'
    js = UglifyJSCompiler('%s/jquery.caret.js' % static)
    js.write(output)
    js = UglifyJSCompiler('%s/jquery.atwho.js' % static)
    js.append(output)


def js_editor():
    from livereload.compiler import UglifyJSCompiler
    static = 'assets/js/editor'
    output = 'june/_static/js/editor.js'
    js = UglifyJSCompiler('%s/upload.js' % static)
    js.write(output)


#: less tasks
Task.add(
    'assets/less/mobile.less',
    lessc('assets/less/mobile.less', 'june/_static/css/mobile.css')
)


#: javascript tasks
Task.add('assets/js/lib/', js_lib)
Task.add('assets/js/eidtor/', js_editor)
Task.add('assets/resources/At.js/js/', js_at)
Task.add(
    'assets/js/site.js',
    uglifyjs('assets/js/site.js', 'june/_static/js/site.js')
)


#: html tasks
Task.add('june/_templates/*.html')
Task.add('june/_templates/snippet/*.html')
Task.add('june/_templates/module/*.html')
