#!/usr/bin/env python

import argparse
try:
    from june.app import parse_config_file
except ImportError:
    from app import parse_config_file


def create_db():
    from june.config import db
    import june.models
    db.create_db()
    return


def create_superuser():
    from june.config import db
    from june.models import Member
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


config = '''debug = True
version = 'dev 1.0.0'
num_processes = 1
master = "sqlite:////Users/lepture/workspace/tmp/june.sqlite"
slaves = ""
memcache = "127.0.0.1:11211"
xsrf_cookies = True
cookie_secret = "cookiesecret"
password_secret = "passwordsecret"
login_url = "/account/signin"
static_path = "/Users/lepture/workspace/june/static"
static_url_prefix = "/static/"

sitename = "June"
ga = ""
'''


def init_project():
    f = open('config.py', 'w')
    f.write(config)
    f.close()
    return


def main():
    parser = argparse.ArgumentParser(
        prog='june',
        description='June: a forum',
    )
    parser.add_argument('command', nargs="*")
    parser.add_argument('-f', '--config', dest='config')
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
