#!/usr/bin/python
# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='bgpranking',
    version='0.1',
    description='API to access the Redis database of a BGP Ranking instance.',
    url='https://github.com/CIRCL/bgpranking-py.git',
    author='Raphaël Vinot',
    author_email='raphael.vinot@circl.lu',
    maintainer='Raphaël Vinot',
    maintainer_email='raphael.vinot@circl.lu',
    packages=['bgpranking'],
    license='GNU GPLv3',
    long_description=open('README.md').read(),
    )
