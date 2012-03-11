# Makefile for June Project
#
# Project Owner: lepture
#

CONFIG = tmp.config
ProjectServer = linode.lepture.com:/home/lepture/project/assets.lepture.com/june
StaticServer = linode.lepture.com:/home/lepture/project/june

server:
	june/app.py --config=$(CONFIG)

less:
	if [ ! -d static/css ]; then mkdir -p static/css; fi
	lessc --compress assets/less/site.less > static/css/site.css
	lessc --compress assets/less/mobile.less > static/css/mobile.css

compilejs:
	if [ ! -d static/js ]; then mkdir static/js; fi
	uglifyjs -nc assets/js/lib/jquery.js > static/js/lib.js
	uglifyjs -nc assets/js/lib/jquery.caret.js >> static/js/lib.js
	uglifyjs -nc assets/js/lib/jquery.atwho.js >> static/js/lib.js
	uglifyjs -nc assets/js/lib/jquery.timeago.js >> static/js/lib.js

compileshowdown:
	uglifyjs -nc assets/js/lib/showdown.js > static/js/lib/showdown.js

copyimg:
	if [ ! -d static/img ]; then mkdir static/img; fi
	cp -r assets/img/* static/img/

copyjs:
	if [ ! -d static/js ]; then mkdir static/js; fi
	cp -r assets/js/*.js static/js/

upload_static:
	rsync -av --del static/* $(ProjectServer)

upload_py:
	rsync -av --del --exclude=*.pyc june/* $(StaticServer)

upload: upload_static upload_py

clean:
	rm -fr build
	rm -fr dist
	rm -fr *.egg-info
