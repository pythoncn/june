June
=====

This is a forum project.

Before start:
-------------

Make sure you have python2.7, pip and virtualenv installed.

Development
-----------

To start development server:

    $ git checkout https://github.com/ekzhu/june.git
    $ cd june
    $ virtualenv --distribute venv
    $ source venv/bin/activate
    (venv)$ pip install -r conf/reqs-dev.txt
    (venv)$ python manager.py creatdb
    (venv)$ python manager.py runserver

It should be running at localhost:5000.

Trouble shooting
----------------

If you encounter build failure when trying to install gevent and get error saying "event.h" not found. You need to install libevent before installing gevent again. 

On Mac OS X with homebrew, you can simply do:

    brew install libevent