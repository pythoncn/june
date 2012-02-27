server:
	june/app.py --config=tmp.config

less:
	if [ ! -d static/css ]; then mkdir static/css; fi
	lessc --compress assets/less/site.less > static/css/site.css

compilejs:
	if [ ! -d static/js ]; then mkdir static/js; fi
	uglifyjs -nc assets/js/lib/jquery.js > static/js/lib.js
	uglifyjs -nc assets/js/app.js >> static/js/lib.js

copystatic:
	if [ ! -d static/js ]; then mkdir static/js; fi
	if [ ! -d static/img ]; then mkdir static/img; fi
	cp -r assets/js/* static/js/
	cp -r assets/img/* static/img/

clean:
	rm -fr build
	rm -fr dist
	rm -fr *.egg-info
