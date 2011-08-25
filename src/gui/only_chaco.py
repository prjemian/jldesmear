#!/usr/bin/env python

'''
Simple plotting of results from lake desmearing.
Uses Enthought's Chaco package.
'''


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################


import os
import sys

from enthought.chaco.shell import loglog, hold, show
import only_traits


class OnlyChacoParameters(only_traits.Parameters):
    '''
    Use the same structure
    '''
    name = os.path.basename(__file__)


def main():
    ''' '''
    # locate the parameters file in the same directory as this file
    path = os.path.abspath( os.path.dirname(__file__) )
    name = os.path.basename( os.path.splitext(__file__)[0] )
    paramfile = os.path.join(path, name + '.pkl')
    
    params = OnlyChacoParameters(
        infile = "../lake/data/test1.smr", 
        outfile = "test1.dsm",
        slitlength = 0.08,
        sFinal = 0.08,
        NumItr = 10,
        extrapname = 'linear',
        LakeWeighting = 'fast',
    )

    params.configure_traits(filename=paramfile, edit=False)
    
    q, E, dE, C, dC = only_traits.core_desmearing_algorithm(params)

    loglog(q, E, "b-", name="smeared data", bgcolor="white")
    hold(True)
    loglog(q, C, "r-", name="desmeared result")
    show()


if __name__ == '__main__':
    sys.exit( main() )
