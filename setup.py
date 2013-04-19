
import june
from email.utils import parseaddr
from setuptools import setup

author, author_email = parseaddr(june.__author__)


setup(
    name='june',
    version=june.__version__,
    author=author,
    author_email=author_email,
    url='https://github.com/pythoncn/june',
    packages=['june'],
    license=open('License').read()
)
