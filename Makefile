# Makefile for June Project
#
# Project Owner: lepture
#

CONFIG = tmp.config
PROJSERVER = linode.lepture.com:/home/lepture/project/june
JS = uglifyjs -nc assets/js
LESS = lessc --compress assets/less
STATIC = june/_static

server:
	june/app.py --settings=$(CONFIG)

static: js image

css: mobilecss

mobilecss:
	if [ ! -d $(STATIC)/css ]; then mkdir -p $(STATIC)/css; fi
	$(LESS)/mobile.less > $(STATIC)/css/mobile.css


js: libjs atjs editorjs copyjs

libjs:
	if [ ! -d $(STATIC)/js ]; then mkdir -p $(STATIC)/js; fi
	$(JS)/lib/jquery.js > $(STATIC)/js/lib.js
	$(JS)/lib/jquery.timeago.js >> $(STATIC)/js/lib.js
	$(JS)/lib/jquery.tipsy.js >> $(STATIC)/js/lib.js

atjs:
	$(JS)/lib/jquery.caret.js > $(STATIC)/js/at.js
	$(JS)/lib/jquery.atwho.js >> $(STATIC)/js/at.js
	$(JS)/lib/jquery.uploader.js >> $(STATIC)/js/at.js
	$(JS)/at.js >> $(STATIC)/js/at.js

editorjs:
	$(JS)/lib/showdown.js > $(STATIC)/js/editor.js
	$(JS)/lib/jquery.uploader.js >> $(STATIC)/js/editor.js
	$(JS)/editor.js >> $(STATIC)/js/editor.js

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
