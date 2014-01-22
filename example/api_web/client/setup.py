#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='bgpranking-web',
    version='1.0',
    description='Library to access the BGP Ranking REST API.',
    url='https://github.com/CIRCL/bgpranking-redis-api',
    author='Raphaël Vinot',
    author_email='raphael.vinot@circl.lu',
    maintainer='Raphaël Vinot',
    packages=['bgpranking_web'],
    long_description=open('README.md').read(),
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

    install_requires=['requests']
    )
