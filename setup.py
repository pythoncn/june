#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='june',
    version='0.9.0',
    author='Hsiaoming Yang',
    author_email='lepture@me.com',
    url='http://project.lepture.com/june',
    packages=find_packages(),
    description='June: a forum',
    install_requires=[
        'july',
        'misaka',
        'pygments',
        'sqlalchemy',
        'MySQL-python',
        'python-memcached',
    ],
    include_package_data=True,
    license='BSD License',
)
