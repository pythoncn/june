#!/usr/bin/env python

import argparse
from july.util import parse_config_file


def create_db():
    from july.database import db
    import account.models
    import node.models
    import topic.models
    import dashboard.models
    import feedback.models
    db.Model.metadata.create_all(db.engine)
    return


def create_superuser():
    from july.database import db
    from account.models import Member
    cmd = raw_input('Create superuser?(Y/n): ')
    if cmd == 'n':
        import sys
        sys.exit(1)
    import getpass
    username = raw_input('username: ')
    email = raw_input('email: ')
    password = getpass.getpass('password: ')
    user = Member(email=email, username=username)
    user.password = Member.create_password(password)
    user.role = 10
    db.session.add(user)
    db.session.commit()
    return user


config = '''debug = False
master = "sqlite:////tmp/june.sqlite"
memcache = "127.0.0.1:11211"
cookie_secret = "cookiesecret"
password_secret = "passwordsecret"

sitename = "June"
siteurl = "http://python-china.org"

recaptcha_key = ''
recaptcha_secret = ''
'''


def init_project():
    f = open('settings.py', 'w')
    f.write(config)
    f.close()
    return


def main():
    parser = argparse.ArgumentParser(
        prog='june',
        description='June: a forum',
    )
    parser.add_argument('command', nargs="*")
    parser.add_argument('-f', '--settings', dest='config')
    args = parser.parse_args()

    if args.config:
        parse_config_file(args.config)  # config
    else:
        return init_project()

    def run_command(cmd):
        if cmd == 'createdb':
            return create_db()
        if cmd == 'createuser':
            return create_superuser()
        if cmd == 'init':
            return init_project()

    if isinstance(args.command, basestring):
        return run_command(args.command)
    if isinstance(args.command, (list, tuple)):
        for cmd in args.command:
            run_command(cmd)


if __name__ == "__main__":
    main()
