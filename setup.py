
import june
from email.utils import parseaddr
from setuptools import setup, find_packages

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
        'Flask'
        'Flask-SQLAlchemy',
        'Flask-Cache',
        'Flask-Babel',
        'Flask-WTF',
        'Flask-Mail',
        'Flask-Script==0.5',

        'misaka',
        'pygments',
        'houdini.py',
        'gevent',
        'gunicorn',
    ]
)
