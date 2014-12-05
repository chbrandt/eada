#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import imp
try:
    # This incantation forces distribute to be used (over setuptools) if it is
    # available on the path; otherwise distribute will be downloaded.
    import pkg_resources
    distribute = pkg_resources.get_distribution('distribute')
    if pkg_resources.get_distribution('setuptools') != distribute:
        sys.path.insert(1, distribute.location)
        distribute.activate()
        imp.reload(pkg_resources)
except:  # There are several types of exceptions that can occur here
    from distribute_setup import use_setuptools
    use_setuptools()

import glob
import os
from setuptools import setup, find_packages

#A dirty hack to get around some early import/configurations ambiguities
if sys.version_info[0] >= 3:
    import builtins
else:
    import __builtin__ as builtins
builtins._ASTROPY_SETUP_ = True

# Set affiliated package-specific settings
PACKAGENAME = 'zyxw'
DESCRIPTION = 'Package for dealing with astronomical data processing'
LONG_DESCRIPTION = """
Zyxw is strongly dependent on astropy and related packages. Codes here are
higher level interfaces -- you can call it workflows -- for other libraries
(e.g, Astropy) to further handle and process data.
"""

AUTHOR = 'Carlos H. Brandt'
AUTHOR_EMAIL = 'carlos.brandt@asdc.asi.it'
LICENSE = 'GPL'
URL = ''

# VERSION should be PEP386 compatible (http://www.python.org/dev/peps/pep-0386)
VERSION = '0.0.1.dev'

# Indicates if this version is a release version
RELEASE = 'dev' not in VERSION

# Treat everything in scripts except README.rst as a script to be installed
scripts = [fname for fname in glob.glob(os.path.join('scripts', '*'))]

# Additional C extensions that are not Cython-based should be added here.
extensions = []

# A dictionary to keep track of all package data to install
package_data = {PACKAGENAME: [os.path.join('data','*')]}

# A dictionary to keep track of extra packagedir mappings
package_dirs = {}

packages = find_packages()

setup(name=PACKAGENAME,
      version=VERSION,
      description=DESCRIPTION,
      packages=packages,
      package_data=package_data,
      package_dir=package_dirs,
      ext_modules=extensions,
      scripts=scripts,
      requires=['astropy','pyvo'],
      install_requires=['astropy'],
      provides=[PACKAGENAME],
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      license=LICENSE,
      url=URL,
      long_description=LONG_DESCRIPTION,
      zip_safe=False,
      use_2to3=True
      )
