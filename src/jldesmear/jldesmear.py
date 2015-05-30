#!/usr/bin/env python

'''
traditional command-line interface: Iterative desmearing technique of Lake to small-angle scattering data
'''


import os, sys
sys.path.insert(0, os.path.abspath(os.path.join('..')))


def desmear_cli():
    import jldesmear.jl_api.traditional
    jldesmear.jl_api.traditional.command_line_interface()


def desmear_qt():
    import jldesmear.jl_gui
    jldesmear.jl_gui.main()


if __name__ == '__main__':
    desmear_cli()
