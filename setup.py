#!/usr/bin/env python
#-*- coding:utf-8 -*-

##########

#from setuptools import setup
#
#setup(
#    entry_points = {
#        'console_scripts': ['npt=npt.cli:main'],
#    }
#)

##########

import sys
from setuptools import setup, find_packages


PACKAGE = 'eada'

URL = f"https://github.com/chbrandt/{PACKAGE}"

AUTHOR = "Carlos H. Brandt"

DESCRIPTION = "Look into astronomical objects in VO resources (scs/spectra)"

LONG_DESCRIPTION = """
    Eada (External Archive Data Access) queries VO services for data based
    on (RA,Dec) position and a radius around it.
    The package uses PyVO and Astropy.
"""

LICENSE = 'GPL'


from version import VERSION

## Treat everything in scripts except README.rst as a script to be installed
#import glob
#scripts = [fname for fname in glob.glob(os.path.join('scripts', '*'))]

## A dictionary to keep track of all package data to install
#import os
#package_data = {PACKAGENAME: [os.path.join('data','*')]}


setup(name=PACKAGE,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    url=URL,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <3.8',
    install_requires=[
        'astropy<4',
        'pyvo==0.6.1',
        'timeout_decorator',
        'pyyaml'
    ],
    packages=find_packages(),
    zip_safe=False,
    use_2to3=True,
    license=LICENSE
)
