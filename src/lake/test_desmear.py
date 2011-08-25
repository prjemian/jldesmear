#!/usr/bin/env python

########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################


import unittest
import desmear
import toolbox
import os

arr_chiSqr = []


class Test(unittest.TestCase):


    def test_(self):
        info = {                # set the defaults
            "infile": os.path.join('..', '..', 'data', 'test1.smr'), 
            "outfile": "test.dsm",
            "slitlength": 0.08,              # s: slit length, as defined by Lake
            "sFinal": 0.08,                  # fit extrapolation constants for q>=sFinal
            "NumItr": 10,                # number of desmearing iterations
            "extrapname": "constant",       # model final data as a constant
            "LakeWeighting": "fast",        # shows the fastest convergence most times
        }
        q, E, dE = toolbox.GetDat(info["infile"])
        C, dC = desmear.Desmear(q, E, dE, info, callback, quiet = True)
        # This is the first 10 ChiSqr values
        dataset = {0: 12982255.937849568, 
                   1: 1368042.0652772535, 
                   2: 19048.702152480953, 
                   3: 5992.1067392198993, 
                   4: 1476.8092179696571, 
                   5: 566.3589299728435, 
                   6: 293.82635615061247, 
                   7: 194.29171584652019, 
                   8: 158.43812910492957, 
                   9: 135.59214114346224
                   }
        for index, expected in dataset.items():
            self.assertAlmostEquals(arr_chiSqr[index], expected)


def callback (q, I, dI, C, S, iteration, ChiSqr, info=None, extrap=None):
    '''
    this function is called after every desmearing iteration
    
    :param q: array (list)
    :param I: array (list) of SAS data I(q) +/- dI(q)
    :param dI: array (list)
    :param S: array (list) of smeared intensity
    :param C: array (list) of corrected intensity
    :param iteration: iteration number
    :param ChiSqr: Chi-Squared value
    :param info: dictionary of input parameters
    :param extrap: extrapolation function structure
    :return: should desmearing stop?
    '''
    arr_chiSqr.append(ChiSqr)
    return iteration >= info['NumItr']

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_']
    unittest.main()