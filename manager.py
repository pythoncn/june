#!/usr/bin/env python
# coding: utf-8

import os
from flask_script import Manager, Server
from june.app import create_app


settings = os.path.abspath('./etc/settings.py')
if not os.path.exists(settings):
    settings = os.path.abspath('./etc/dev_config.py')

if 'JUNE_SETTINGS' not in os.environ and os.path.exists(settings):
    os.environ['JUNE_SETTINGS'] = settings

manager = Manager(create_app)
manager.add_option('-c', '--config', dest='config', required=False)
manager.add_command('runserver', Server())


@manager.command
def createdb():
    """Create database for june."""
    from june.models import db
    db.create_all()


if __name__ == '__main__':
    manager.run()
