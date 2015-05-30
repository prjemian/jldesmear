#!/usr/bin/env python


import unittest
import info
import desmear
import toolbox
import os       #@UnusedImport

arr_chiSqr = []


class Test(unittest.TestCase):
    ''' '''

    def test_(self):
        params = info.Info()
        if params == None:
            return          # no input file so quit the program

        # override default constants for code development
        params.infile = toolbox.GetTest1DataFilename('.smr')
        params.outfile = "test.dsm"
        params.slitlength = 0.08
        params.sFinal = 0.08
        params.NumItr = 9
        params.extrapname = "linear"
        params.callback = callback
        params.quiet = True
        
        q, E, dE = toolbox.GetDat(params.infile)
        dsm = desmear.Desmearing(q, E, dE, params)
        dsm.traditional()

        # This is the first 10 ChiSqr values
        dataset = {
            0: 12982255.997449555 ,
            1: 1368042.0757172147 ,
            2: 19048.7129764 ,
            3: 5992.12476839 ,
            4: 1476.83231416 ,
            5: 566.385118142 ,
            6: 293.855006653 ,
            7: 194.322940725 ,
            8: 158.47186882 ,
            9: 135.627852795 ,
        }
        for index, expected in dataset.items():
            self.assertAlmostEquals(dsm.ChiSqr[index], expected)


def callback (dsm):
    '''
    this function is called after every desmearing iteration
    
    :param obj dsm: Desmearing object
    :return: should desmearing stop?
    :rtype: bool
    '''
    return dsm.iteration_count >= dsm.params.NumItr

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_']
    unittest.main()
