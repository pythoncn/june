# coding: utf-8

import june
from email.utils import parseaddr
from setuptools import setup, find_packages

kwargs = {}
try:
    from babel.messages import frontend as babel
    kwargs['cmdclass'] = {
        'extract_messages': babel.extract_messages,
        'update_catalog': babel.update_catalog,
        'compile_catalog': babel.compile_catalog,
        'init_catalog': babel.init_catalog,
    }
    kwargs['message_extractors'] = {
        'june': [
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
except ImportError:
    pass


flask_requires = [
    'Flask',
    'Flask-SQLAlchemy',
    'Flask-Cache',
    'Flask-Babel',
    'Flask-WTF',
    'Flask-Mail',
    'Flask-Script',
]
install_requires = [
    'Alembic',
    'misaka',
    'pygments',
    'gevent',
    'gunicorn',
]
install_requires.extend(flask_requires)
author, author_email = parseaddr(june.__author__)

setup(
    name='june',
    version=june.__version__,
    author=author,
    author_email=author_email,
    url='http://python-china.org/',
    packages=find_packages(exclude=['tests', 'tests.*']),
    license='BSD',
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
    **kwargs
)
