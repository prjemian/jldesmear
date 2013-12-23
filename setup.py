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
import jldesmear

requires = ['Sphinx>=0.6']

packages = {}
for pkg in ('jldesmear', 'jldesmear/api', 'jldesmear/gui'):
    packages[pkg]       = os.path.join('src', pkg)

console_scripts = []
for launcher, method_path in {
    'jldesmear': 'jldesmear.desmear:desmear_cli',
    'jldesmear_qt': 'jldesmear.desmear:desmear_qt',
    'jldesmear_traits': 'jldesmear.gui.traitsgui:main',
                 }.items():
    console_scripts.append(launcher + ' = ' + method_path)

setup(
        name             = jldesmear.__project__,
        version          = jldesmear.__version__,
        description      = jldesmear.__description__,
        long_description = jldesmear.__long_description__,
        author           = jldesmear.__author__,
        author_email     = jldesmear.__email__,
        url              = jldesmear.__url__,
        license          = jldesmear.__license__,
        platforms        = 'any',
        zip_safe         = False,
        packages         = packages.keys(),
        package_dir      = packages,
        package_data     = {
            'jldesmear': ['data/*.*',]
        },
        entry_points     = {
          # create & install console_scripts in <python>/bin
          'console_scripts': console_scripts,
        },
        classifiers      = [
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
     )

########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
