# coding: utf-8

import os
from fabric.api import env, local, cd, run, sudo
from fabric.operations import put

env.user = 'www'
# env.password
# env.hosts


def virtualenv():
    """Setup virtualenv for june."""
    run('mkdir -p ~/venv')
    run('virtualenv ~/venv/june')


def tarball():
    """Create tarball for june."""
    local('python setup.py sdist --formats=gztar', capture=False)


def upload():
    """Upload tarball to the server."""
    dist = local('python setup.py --fullname', capture=True).strip()
    put('dist/%s.tar.gz' % dist, '~/tmp/june.tar.gz')

    run('mkdir -p ~/tmp/june')
    with cd('~/tmp/june'):
        run('tar xzf ~/tmp/june.tar.gz')


def install():
    """Install june package."""
    dist = local('python setup.py --fullname', capture=True).strip()
    with cd('~/tmp/june/%s' % dist):
        run('~/venv/june/bin/python setup.py install')


def clean():
    """Clean packages on server."""
    run('rm -fr ~/tmp/june')
    run('rm -f ~/tmp/june.tar.gz')


def mkdirs():
    """Prepare directories."""
    # for june site
    run('mkdir -p ~/apps/june/public/static')
    run('mkdir -p ~/apps/june/public/data')


def configure():
    """Prepare configuration files."""
    dist = local('python setup.py --fullname', capture=True).strip()
    tmpdir = '~/tmp/june/%s' % dist
    run('cp %s/wsgi.py ~/apps/june/' % tmpdir)
    run('cp %s/manager.py ~/apps/june/' % tmpdir)

    run('cp %s/alembic.ini ~/apps/june/' % tmpdir)
    run('cp -r %s/migration ~/apps/june/' % tmpdir)

    run('cp %s/etc/supervisord.conf ~/etc/supervisord/june.conf' % tmpdir)
    run('cp %s/etc/nginx.conf ~/etc/nginx/june.conf' % tmpdir)

    run('cp -r %s/etc ~/apps/june/' % tmpdir)
    with cd('~/apps/june/etc'):
        run('mv online_config.py settings.py')


def upgrade_database():
    with cd('~/apps/june'):
        run('~/venv/june/bin/python manager.py migrate upgrade head')
