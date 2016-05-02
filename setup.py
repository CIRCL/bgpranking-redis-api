#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='bgpranking-redis',
    version='2.0',
    author='Raphaël Vinot',
    author_email='raphael.vinot@circl.lu',
    maintainer='Raphaël Vinot',
    url='https://github.com/CIRCL/bgpranking-redis-api',
    description='API to access the Redis database of a BGP Ranking instance.',
    long_description=open('README.md').read(),
    packages=['bgpranking_redis'],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Telecommunications Industry',
        'Programming Language :: Python',
        'Topic :: Security',
        'Topic :: Internet',
        'Topic :: System :: Networking',
    ],
    install_requires=['IPy', 'pubsublogger', 'redis', 'python-dateutil', 'asnhistory', 'ipasn-redis'],
)
