# coding: utf-8

from fabric.api import env, local, cd, run
from fabric.operations import put

env.user = 'www'
env.hosts = ['python-china.org']
# env.password


def prepare():
    """Prepare server for installation."""
    run('mkdir -p ~/venv')
    run('virtualenv ~/venv/june')
    run('mkdir -p ~/apps/june/public/static')


def tarball():
    """Create tarball for june."""
    local('make static')
    local('python setup.py sdist --formats=gztar', capture=False)


def upload():
    """Upload tarball to the server."""
    dist = local('python setup.py --fullname', capture=True).strip()
    run('mkdir -p ~/tmp/june')

    put('dist/%s.tar.gz' % dist, '~/tmp/june.tar.gz')
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


def update():
    """Update assets"""
    dist = local('python setup.py --fullname', capture=True).strip()
    tmpdir = '~/tmp/june/%s' % dist
    run('cp -r %s/june/public ~/apps/june/' % tmpdir)


def upgrade():
    """Upgrade database"""
    dist = local('python setup.py --fullname', capture=True).strip()
    tmpdir = '~/tmp/june/%s' % dist
    run('cp %s/alembic.ini ~/apps/june/' % tmpdir)
    run('rm -fr ~/apps/june/alembic')
    run('cp -r %s/alembic ~/apps/june/' % tmpdir)
    with cd('~/apps/june'):
        run('~/venv/june/bin/alembic upgrade head')


def restart():
    """Restart remote server"""
    run('supervisorctl pid june | xargs kill -HUP')
