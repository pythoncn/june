Development
===========

This section assumes that you have everything installed. If you haven't, head over to :ref:`installation`.

But development environment requires more, you should install some compilers, such as less
and uglifyJS.

If you have npm installed, that should be easy::

    $ npm install less -g
    $ npm install uglify-js -g


If not, try install node and npm for yourself.

Install one more python library::

    $ pip install slimmer


Git Pro
--------

You should first fork June, and clone it from your own repo.

When you cloned June, you are on the master branch. But actually, we are developing on the
develop branch. Switch your branch::

    $ git checkout origin/develop
    $ git branch develop
    $ git checkout develop


Now push to your own repo with::

    $ git push origin develop


And switch your branch to ``develop`` on GitHub before sending your pull request.


It Works
----------

Make an alias::

    $ ln -s settings.py tmp.config


Create database::

    $ make database
    $ make admin


Create static files::

    $ make install_static


Start Server::

    $ make server


Join Trello Board: https://trello.com/board/june/4f51c57ed8fc74c84450311e
