# coding: utf-8

from fabric.api import env, local, cd, run, sudo
from fabric.operations import put

env.use_ssh_config = True
env.keepalive = 60


def tarball():
    """Create tarball for june."""
    local('make static')
    local('python setup.py sdist --formats=gztar', capture=False)


def upload():
    """Upload tarball to the server."""
    dist = local('python setup.py --fullname', capture=True).strip()
    run('rm -f ~/tmp/june.tar.gz')
    sudo('rm -fr ~/tmp/june')
    run('mkdir -p ~/tmp/june')

    put('dist/%s.tar.gz' % dist, '~/tmp/june.tar.gz')
    with cd('~/tmp/june'):
        run('tar xzf ~/tmp/june.tar.gz')


def install():
    """Install june package."""
    dist = local('python setup.py --fullname', capture=True).strip()
    with cd('~/tmp/june/%s' % dist):
        sudo('/srv/venv/june/bin/pip install .')


def restart():
    """Restart remote server"""
    run('supervisorctl pid june | xargs kill -HUP')


def bootstrap():
    dist = local('python setup.py --fullname', capture=True).strip()
    tarball()
    upload()

    # prepare
    sudo('mkdir -p /var/log/june')
    sudo('mkdir -p /srv/venv')
    sudo('virtualenv /srv/venv/june')
    sudo('mkdir -p /www/june/public/static')

    install()
    # install patch
    sudo('/srv/venv/june/bin/pip install MySQL-python redis')

    with cd('~/tmp/june/%s' % dist):
        sudo('mv etc/nginx.conf /etc/nginx/conf.d/june.conf')
        sudo('mv etc/supervisord.conf /etc/supervisor/conf.d/june.conf')

        sudo('rm -fr /www/june/etc')
        sudo('mv etc /www/june/')
        sudo('rm -fr /www/june/public')
        sudo('mv june/public /www/june/')
        sudo('mv wsgi.py /www/june/')
