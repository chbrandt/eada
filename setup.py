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

import os
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

LICENSE = 'GPL2'


from version import VERSION

## Treat everything in scripts except README.rst as a script to be installed
import glob
scripts = [fname for fname in glob.glob(os.path.join('scripts', '*'))]

## A dictionary to keep track of all package data to install
#import os
#package_data = {PACKAGENAME: [os.path.join('data','*')]}


setup(name=PACKAGE,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <4',
    version=VERSION,
    description=DESCRIPTION,
    packages=find_packages(),
    scripts=scripts,
    install_requires=[
        'astropy==4.1', #required by new pyvo
        'pyvo==1.5', #for new catalogs
        'ipython==7.32.0', #'IPython.utils.io' has no attribute 'IOStream'
        'timeout_decorator',
        'pyyaml'
    ],
    zip_safe=False,
    url=URL,
    author=AUTHOR,
    long_description=LONG_DESCRIPTION,
    license=LICENSE
)
