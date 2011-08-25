#!/usr/bin/env python

########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################


import unittest
import smear
import toolbox
import extrap_linear
import os


datafile = os.path.join('..', '..', 'data', 'test1.dsm')


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

    def test_Ic(self):
        q, C, dC = toolbox.GetDat(datafile)
        start = toolbox.find_first_index(q, 0.08)
        extrap = extrap_linear.Linear()
        extrap.fit(q[start:-1], C[start:-1], dC[start:-1])
        dataset = {}
        dataset[ 0.0283713 ] = 94.583700
        dataset[ 0.0291575 ] = 87.97486733043597
        dataset[ 0.0299437 ] = 65.745746276917316
        dataset[ 0.0307299 ] = 71.932648088208083
        dataset[ 0.0315161 ] = 81.720936087794271
        dataset[ 0.0323023 ] = 59.724180246127695
        dataset[ 0.0330649 ] = 34.700520014318151
        dataset[ 0.08 ] = 38.461301529649695
        dataset[ 0.09 ] = 32.131663454229546
        for qNow, expected in dataset.items():
            self.assertAlmostEquals( smear.FindIc(0, qNow, q, C, extrap), expected)

    def test_trapezoid_integration(self):
        dataset = []
        dataset.append( ((1,2,3), (0., 1., 0.), 1.0) )
        dataset.append( ((1,2,3,4), (0., 1., 1., 0.), 2.0) )
        for test_set in dataset:
            x, y, area = test_set
            self.assertAlmostEquals( smear.trapezoid_integration(x, y), area)

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
