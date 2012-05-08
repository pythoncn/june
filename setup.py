#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='june',
    version='1.0',
    author='Hsiaoming Young',
    author_email='lepture@me.com',
    url='http://lepture.com/project/june',
    packages=find_packages(),
    description='June: a forum',
    install_requires=[
        'python-memcached',
        #'markdown2',
        'misaka',
        'pygments',
        'july',
    ],
    include_package_data=True,
    license='BSD License',
)
