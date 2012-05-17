.. _installation:

Installation
=============

June is still under heavy development.


virtualenv
----------

Virtualenv is probably what you want to use during development,
and if you have shell access to your production machines,
you’ll probably want to use it there, too.

It is strongly suggested that you develop on virtualenv.

If you are on Linux or Mac OS X, you can install it with::

    $ sudo pip install virtualenv

if you have no pip::

    $ sudo easy_install virtualenv

And you should use **pip** instead of easy_install, install pip with::

    $ sudo easy_install pip

If you are on Windows, you should try **MinGW** or **Cygwin** .

Read document of virtualenv for a better life. But you can start now with::

    $ mkdir ~/env
    $ virtualenv ~/env/june

When the installation is finished, active this virtual environment::

    $ source ~/env/june/bin/active

Now, you are on a virtual environment called june. Any python package will be installed
on this june environment now::

    $ python setup.py install



Distribute & Pip
-----------------

June is under development.


System-Wide Installation
-------------------------

June is under development, you should use virtualenv instead.


Github Source
--------------

If you have git installed, get source code from github::

    $ git clone http://github.com/lepture/june.git
    $ cd june


Get required libraries for june::

    $ pip install -r requirements.txt

Get required libraries for your database, ``sqlite3``, ``MySQL``,  ``PostgreSQL``.

Get static development tools::

    $ pip install livereload


Explain on libraries:

1. July_ makes tornado easy to use.
2. misaka_ is a better solution for markdown
3. pygments_ highlights the code
4. sqlalchemy_ is the ORM engine
5. livereload_ is an awesome tool for web development.

.. _July: http://july.readthedocs.org
.. _misaka: http://misaka.61924.nl
.. _pygments: http://pygments.org
.. _sqlalchemy: http://sqlalchmey.org
.. _livereload: http://lepture.com/project/livereload/
