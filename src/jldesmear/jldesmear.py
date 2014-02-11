#!/usr/bin/env python

'''
traditional command-line interface: Iterative desmearing technique of Lake to small-angle scattering data
'''


import os, sys
sys.path.insert(0, os.path.abspath(os.path.join('..')))


def desmear_cli():
    import jldesmear.api.traditional
    jldesmear.api.traditional.command_line_interface()


def desmear_qt():
    import jldesmear.gui.desmearinggui
    jldesmear.gui.desmearinggui.main()


if __name__ == '__main__':
    desmear_cli()
