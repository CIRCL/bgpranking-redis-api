#!/usr/bin/python
# -*- coding: utf-8 -*-
from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

setup(
    name='bgpranking',
    version='1.0.3',
    author='Raphaël Vinot',
    author_email='raphael.vinot@circl.lu',
    maintainer='Raphaël Vinot',
    url='https://github.com/CIRCL/bgpranking-redis-api',
    description='API to access the Redis database of a BGP Ranking instance.',
    long_description=open('README.md').read(),
    packages=['bgpranking'],
    cmdclass = {'build_py': build_py},
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
    requires=['IPy', 'pubsublogger', 'redis', 'dateutil'],
    )
