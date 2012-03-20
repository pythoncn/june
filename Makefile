# Makefile for June Project
#
# Project Owner: lepture
#

CONFIG = tmp.config
PROJSERVER = linode.lepture.com:/home/lepture/project/june

server:
	june/app.py --config=$(CONFIG)

static: less js image

less: siteless mobileless dashboardless googleless

siteless:
	if [ ! -d june/static/css ]; then mkdir -p june/static/css; fi
	lessc --compress assets/less/site.less > june/static/css/site.css

mobileless:
	lessc --compress assets/less/mobile.less > june/static/css/mobile.css

dashboardless:
	lessc --compress assets/less/dashboard.less > june/static/css/dashboard.css

googleless:
	lessc --compress assets/less/google.less > june/static/css/google.css

js: libjs atjs editorjs copyjs

libjs:
	if [ ! -d june/static/js ]; then mkdir -p june/static/js; fi
	uglifyjs -nc assets/js/lib/jquery.js > june/static/js/lib.js
	uglifyjs -nc assets/js/lib/jquery.timeago.js >> june/static/js/lib.js
	uglifyjs -nc assets/js/lib/jquery.tipsy.js >> june/static/js/lib.js

atjs:
	uglifyjs -nc assets/js/lib/jquery.caret.js > june/static/js/at.js
	uglifyjs -nc assets/js/lib/jquery.atwho.js >> june/static/js/at.js
	uglifyjs -nc assets/js/at.js >> june/static/js/at.js

editorjs:
	uglifyjs -nc assets/js/lib/showdown.js > june/static/js/editor.js
	uglifyjs -nc assets/js/editor.js >> june/static/js/editor.js

image:
	if [ ! -d june/static/img ]; then mkdir june/static/img; fi
	cp -r assets/img/* june/static/img/

copyjs:
	if [ ! -d june/static/js ]; then mkdir -p june/static/js; fi
	cp assets/js/pears.js june/static/js/

upload:
	rsync -av --del --exclude=*.pyc june/* $(PROJSERVER)

clean:
	rm -fr build
	rm -fr dist
	rm -fr *.egg-info
