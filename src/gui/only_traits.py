#!/usr/bin/env python

'''
Simple management of user input for lake desmearing.
Uses Enthought's Traits package.
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

import lake.toolbox
import lake.desmear
import lake.lake

from enthought.traits.api import HasTraits, Float, File, Int, Enum
from enthought.traits.ui.api import Item, View


class Parameters(HasTraits):
    '''
    Parameters used for lake desmearing SAS data,
    declared using Enthought's Traits module
    '''
    name = os.path.basename(__file__)
    infile = File(
                 desc="the name of the input smeared SAS data file",
                 label="smeared data",
                 exists=True,)
    outfile = File(
                 desc="the name of the output desmeared SAS data file",
                 label="desmeared result file",)
    slitlength = Float(
                 desc="s: slit length, as defined by Lake",
                 label="slit length",)
    sFinal = Float(
                 desc="fit extrapolation constants for q>=sFinal",
                 label="sFinal",)
    NumItr = Int(
                 desc="number of desmearing iterations",
                 label="# iterations",)
    extrapname = Enum( 
                 'constant',  'linear', 'powerlaw', 'Porod',
                 desc="form of extrapolation",
                 label="Extrapolation",)
    LakeWeighting = Enum( 
                 'constant', 'fast',  'ChiSqr',
                 desc="weighting method for iterative refinement",
                 label="weighting",)
    
    view = View('infile', 
                'outfile', 
                'slitlength', 
                'extrapname', 
                'sFinal', 
                'LakeWeighting',
                'NumItr', 
                 title="Desmearing parameters",
                 buttons = ['OK', 'Cancel'],
                 resizable=True)
    
    def __str__(self):
        rpt = ["%s desmearing parameters:" % self.name,]
        rpt.append( "infile: %s" % self.infile )
        rpt.append( "outfile: %s" % self.outfile )
        rpt.append( "slitlength: %g" % self.slitlength )
        rpt.append( "sFinal: %g" % self.sFinal )
        rpt.append( "NumItr: %d" % self.NumItr )
        rpt.append( "extrapname: %s" % self.extrapname )
        rpt.append( "LakeWeighting: %s" % self.LakeWeighting )
        return "\n".join( rpt )


def core_desmearing_algorithm(params):
    ''' the core part of the algorithm '''
    print str(params)
    params_dict =  {
            "infile": params.infile, 
            "outfile": params.outfile,
            "slitlength": params.slitlength,
            "sFinal": params.sFinal,
            "NumItr": params.NumItr,
            "extrapname": params.extrapname,
            "LakeWeighting": params.LakeWeighting,
        }
    
    q, E, dE = lake.toolbox.GetDat(params.infile)
    if (len(q) == 0):
        raise Exception, "no data points!"
    if (params.sFinal > q[-1]):
        raise Exception, "Fit range out of data range"
    C, dC = lake.desmear.Desmear(q, E, dE, params_dict, lake.lake.no_plotting_callback, True)
    lake.toolbox.SavDat(params.outfile, q, C, dC)
    lake.lake.plot_results(q, E, C)
    return q, E, dE, C, dC


def main():
    ''' '''
    # locate the parameters file in the same directory as this file
    path = os.path.abspath( os.path.dirname(__file__) )
    name = os.path.basename( os.path.splitext(__file__)[0] )
    paramfile = os.path.join(path, name + '.pkl')
    
    params = Parameters(
        infile = "../lake/data/test1.smr", 
        outfile = "test1.dsm",
        slitlength = 0.08,
        sFinal = 0.08,
        NumItr = 10,
        extrapname = 'linear',
        LakeWeighting = 'fast',
    )

    if not params.configure_traits(filename=paramfile):
        # Cancel button was pressed
        return

    core_desmearing_algorithm(params)


if __name__ == '__main__':
    sys.exit( main() )
