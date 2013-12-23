#!/usr/bin/env python

'''
Python project installation setup for lake-python
'''


#from distutils.core import setup
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

import os, sys

sys.path.insert(0, os.path.join('src', ))
import api

requires = ['Sphinx>=0.6']

packages = {}
for pkg in ('api', 'gui'):
    packages[pkg]       = os.path.join('src', pkg)

console_scripts = []
for launcher, method_path in {
    'lake_python': 'api.traditional:command_line_interface',
    'lake_python_qt': 'gui.desmearinggui:main',
    'lake_python_traits': 'gui.traitsgui:main',
                 }.items():
    console_scripts.append(launcher + ' = ' + method_path)

setup(
        name=api.__project__,
        version=api.__version__,
        description=api.__description__,
        long_description = api.__long_description__,
        author=api.__author__,
        author_email=api.__email__,
        url=api.__url__,
        packages=packages.keys(),
        license = api.__license__,
        package_dir=packages,
        platforms='any',
        zip_safe=False,
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Environment :: Web Environment',
            'Intended Audience :: Science/Research',
            'License :: Free To Use But Restricted',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Utilities',
        ],
      entry_points={
          # create & install console_scripts in <python>/bin
          'console_scripts': console_scripts,
      },
     )

########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
