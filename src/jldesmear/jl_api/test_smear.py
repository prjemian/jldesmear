#!/usr/bin/env python


import unittest
import smear
import toolbox
import extrap_linear    #@UnusedImport
import os               #@UnusedImport


datafile = toolbox.GetTest1DataFilename('.dsm')


class Test(unittest.TestCase):

    def test_Smear(self):
        q, C, dC = toolbox.GetDat(datafile)
        dataset = {
                    0: 210191.57390922101,
                    25: 137101.45437268729,
                    50: 87438.6991492,
                    75: 57579.5878989,
                    100: 14761.8436667,
                    125: 803.794376001,
                    150: 193.052837038,
                    175: 43.3284721365,
                    200: 38.906636007,
                    225: 37.5749435326,
                    249: 38.589716377562361
                   }
        sFinal = 0.08
        slitlength = 0.08
        S, extrap = smear.Smear(q, C, dC, "constant", sFinal, slitlength, quiet = True)
        for index, expected in dataset.items():
            self.assertAlmostEquals( S[index], expected )
        coeff = extrap.GetCoefficients()
        self.assertTrue('B' in coeff)
        self.assertFalse('m' in coeff)
        self.assertAlmostEquals( coeff['B'], 38.589860526315789 )

    def test_Plengt(self):
        dataset = {}
        dataset[ (-0.1, .5) ] = 1.0
        dataset[ (0, .5) ] = 1.0
        dataset[ (1.1, .5) ] = 0
        dataset[ (0.1, 3) ] = 1./6
        dataset[ (-0.1, 3.) ] = 1./6
        for kk, v in dataset.items():
            l, slitlength = kk
            self.assertAlmostEquals( smear.Plengt(l, slitlength), v)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
