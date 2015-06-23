#!/usr/bin/env python

'''
Python project installation setup for lake-python
'''


from setuptools import setup, find_packages
import os
import re

import os, sys

sys.path.insert(0, os.path.join('src', ))
import jldesmear

packages = {}
for pkg in ('jldesmear', 'jldesmear/jl_api',):
    packages[pkg]       = os.path.join('src', pkg)

setup(
        name             = jldesmear.__project__,
        version          = jldesmear.__version__,
        description      = jldesmear.__description__,
        long_description = jldesmear.__long_description__,
        keywords         = jldesmear.__keywords__,
        author           = jldesmear.__author__,
        author_email     = jldesmear.__email__,
        url              = jldesmear.__url__,
        license          = jldesmear.__license__,
        install_requires = jldesmear.__install_requires__,
        platforms        = 'any',
        zip_safe         = False,
        packages         = packages.keys(),
        package_dir      = packages,
        package_data     = {
            'jldesmear': ['data/*.*',]
        },
        entry_points     = {
          # create & install console_scripts in <python>/bin
          'console_scripts': jldesmear.__console_scripts__,
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
            'Topic :: Utilities'
        ],
     )
