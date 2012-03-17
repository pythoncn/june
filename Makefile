# Makefile for June Project
#
# Project Owner: lepture
#

CONFIG = tmp.config
STATICSERVER = linode.lepture.com:/home/lepture/project/assets.lepture.com/pears
PROJSERVER = linode.lepture.com:/home/lepture/project/pears

server:
	june/app.py --config=$(CONFIG)

less:
	if [ ! -d june/static/css ]; then mkdir -p june/static/css; fi
	lessc --compress assets/less/site.less > june/static/css/site.css
	lessc --compress assets/less/mobile.less > june/static/css/mobile.css
	lessc --compress assets/less/dashboard.less > june/static/css/dashboard.css

libjs:
	if [ ! -d june/static/js ]; then mkdir -p june/static/js; fi
	uglifyjs -nc assets/js/lib/jquery.js > june/static/js/lib.js
	uglifyjs -nc assets/js/lib/jquery.caret.js >> june/static/js/lib.js
	uglifyjs -nc assets/js/lib/jquery.atwho.js >> june/static/js/lib.js
	uglifyjs -nc assets/js/lib/jquery.timeago.js >> june/static/js/lib.js
	uglifyjs -nc assets/js/lib/jquery.tipsy.js >> june/static/js/lib.js

editorjs:
	uglifyjs -nc assets/js/lib/showdown.js > june/static/js/editor.js
	uglifyjs -nc assets/js/editor.js >> june/static/js/editor.js

image:
	if [ ! -d june/static/img ]; then mkdir june/static/img; fi
	cp -r assets/img/* june/static/img/

js:
	if [ ! -d june/static/js ]; then mkdir -p june/static/js; fi
	cp assets/js/pears.js june/static/js/

upload_static:
	rsync -av --del june/static/* $(STATICSERVER)

upload_py:
	rsync -av --del --exclude=*.pyc june/* $(PROJSERVER)

upload: upload_static upload_py

clean:
	rm -fr build
	rm -fr dist
	rm -fr *.egg-info
