#!/usr/bin/env python

'''
Iterative desmearing technique of Lake to small-angle scattering data
'''


import argparse
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join('..')))


def desmear_cli():
    '''command-line user interface'''
    import jldesmear.jl_api.traditional
    jldesmear.jl_api.traditional.command_line_interface()


def desmear_gui():
    '''graphical user interface'''
    import jldesmear.jl_api.gui
    jldesmear.jl_api.gui.main()


def decide_ui():
    '''get arguments passed on command line, if any'''
    doc = '''
Iterative desmearing of SAS data
using the technique of JA Lake 
as implemented by PR Jemian'''
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument('-g', '--gui', action='store_true', default=False,
                        dest='interface',
                        help='Use the graphical rather than command-line interface')
    results = parser.parse_args()
    # select the interface
    ui = {False: desmear_cli, True: desmear_gui}[results.interface]
    return ui


def main():
    # check if GUI was selected by command-line argument: -g or --gui
    ui = decide_ui()
    # call the user interface
    ui()


if __name__ == '__main__':
    main()
