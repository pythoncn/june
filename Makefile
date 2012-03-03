server:
	june/app.py --config=tmp.config

less:
	if [ ! -d static/css ]; then mkdir -p static/css; fi
	lessc --compress assets/less/site.less > static/css/site.css

compilejs:
	if [ ! -d static/js ]; then mkdir static/js; fi
	uglifyjs -nc assets/js/lib/jquery.js > static/js/lib.js
	uglifyjs -nc assets/js/lib/jquery.timeago.js >> static/js/lib.js

copyimg:
	if [ ! -d static/img ]; then mkdir static/img; fi
	cp -r assets/img/* static/img/

copyjs:
	if [ ! -d static/js ]; then mkdir static/js; fi
	cp -r assets/js/* static/js/

upload:
	rsync -av --del static/* linode.lepture.com:/home/lepture/project/assets.lepture.com/june
	rsync -av --del --exclude=*.pyc june/* linode.lepture.com:/home/lepture/project/june

clean:
	rm -fr build
	rm -fr dist
	rm -fr *.egg-info
