#!/usr/bin/env python

'''
traditional command-line interface: Iterative desmearing technique of Lake to small-angle scattering data
'''


import os, sys


def main():
    import api.traditional
    api.traditional.command_line_interface()


def lake_qt():
    sys.path.insert(0, os.path.abspath(os.path.join('..')))
    import gui.desmearinggui
    gui.desmearinggui.main()


if __name__ == '__main__':
    main()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
