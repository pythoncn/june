# Makefile for June Project
#
# Project Owner: lepture
#

CONFIG = tmp.config
PROJSERVER = linode.lepture.com:/home/lepture/project/june
STATIC = june/_static

server:
	june/app.py --settings=$(CONFIG)

static: less js image

less: siteless mobileless dashboardless googleless

siteless:
	if [ ! -d $(STATIC)/css ]; then mkdir -p $(STATIC)/css; fi
	lessc --compress assets/less/site.less > $(STATIC)/css/site.css

mobileless:
	lessc --compress assets/less/mobile.less > $(STATIC)/css/mobile.css

dashboardless:
	lessc --compress assets/less/dashboard.less > $(STATIC)/css/dashboard.css

googleless:
	lessc --compress assets/less/google.less > $(STATIC)/css/google.css

js: libjs atjs editorjs copyjs

libjs:
	if [ ! -d $(STATIC)/js ]; then mkdir -p $(STATIC)/js; fi
	uglifyjs -nc assets/js/lib/jquery.js > $(STATIC)/js/lib.js
	uglifyjs -nc assets/js/lib/jquery.timeago.js >> $(STATIC)/js/lib.js
	uglifyjs -nc assets/js/lib/jquery.tipsy.js >> $(STATIC)/js/lib.js

atjs:
	uglifyjs -nc assets/js/lib/jquery.caret.js > $(STATIC)/js/at.js
	uglifyjs -nc assets/js/lib/jquery.atwho.js >> $(STATIC)/js/at.js
	uglifyjs -nc assets/js/lib/jquery.uploader.js >> $(STATIC)/js/at.js
	uglifyjs -nc assets/js/at.js >> $(STATIC)/js/at.js

editorjs:
	uglifyjs -nc assets/js/lib/showdown.js > $(STATIC)/js/editor.js
	uglifyjs -nc assets/js/lib/jquery.uploader.js >> $(STATIC)/js/editor.js
	uglifyjs -nc assets/js/editor.js >> $(STATIC)/js/editor.js

image:
	if [ ! -d $(STATIC)/img ]; then mkdir $(STATIC)/img; fi
	cp -r assets/img/* $(STATIC)/img/

copyjs:
	if [ ! -d $(STATIC)/js ]; then mkdir -p $(STATIC)/js; fi
	cp assets/js/pears.js $(STATIC)/js/

upload:
	rsync -av --del --exclude=*.pyc june/* $(PROJSERVER)

clean:
	rm -fr build
	rm -fr dist
	rm -fr *.egg-info
