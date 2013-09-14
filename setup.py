# coding: utf-8

import june
from email.utils import parseaddr
from setuptools import setup, find_packages

try:
    from babel.messages import frontend as babel
except:
    class Babel(object):
        def extract_messages(self):
            pass

        def update_catalog(self):
            pass

        def compile_catalog(self):
            pass

        def init_catalog(self):
            pass

    babel = Babel()


author, author_email = parseaddr(june.__author__)


setup(
    name='june',
    version=june.__version__,
    author=author,
    author_email=author_email,
    url='http://python-china.org',
    packages=find_packages(exclude=['tests', 'tests.*']),
    license='BSD',
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-Cache',
        'Flask-Babel',
        'Flask-WTF',
        'Flask-Mail',
        'Flask-Script',

        'Alembic',
        'misaka',
        'pygments',
        'houdini.py',
        'gevent',
        'gunicorn',
    ],
    cmdclass={
        'extract_messages': babel.extract_messages,
        'update_catalog': babel.update_catalog,
        'compile_catalog': babel.compile_catalog,
        'init_catalog': babel.init_catalog,
    },
    message_extractors={
        'yuehu': [
            ('**.py', 'python', None),
            ('**/templates/**.html', 'jinja2', {
                'extensions': (
                    'jinja2.ext.autoescape,'
                    'jinja2.ext.with_,'
                    'jinja2.ext.do,'
                )
            })
        ]
    }
)
