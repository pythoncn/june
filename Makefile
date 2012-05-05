# Makefile for June Project
#
# Project Owner: lepture
#

CONFIG = tmp.config
PROJSERVER = linode.lepture.com:/home/lepture/project/june
STATIC = june/_static

server:
	june/app.py --settings=$(CONFIG)

image:
	if [ ! -d $(STATIC)/img ]; then mkdir $(STATIC)/img; fi
	cp -r assets/img/* $(STATIC)/img/

upload:
	rsync -av --del --exclude=*.pyc june/* $(PROJSERVER)

clean:
	rm -fr build
	rm -fr dist
	rm -fr *.egg-info
