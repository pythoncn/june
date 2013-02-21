June
=====

This is a forum project.

Installation
-------------

Make sure you have python2.7, pip and virtualenv installed.

Development
-----------

You should read the Contribution Guide first.

To start development server::

    $ git checkout your_fork_of_june
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

On Mac OS X with homebrew, you can simply do::

    brew install libevent
