#!/usr/bin/env python


import unittest
import toolbox
import os           #@UnusedImport


missing_datafile = toolbox.GetTest1DataFilename('.txt')
expected_datafile = toolbox.GetTest1DataFilename('.smr')


class Test(unittest.TestCase):

    def test_linear_interpolation(self):
        eps = 1.0e-7
        x1, y1 = (0.1, 1000)
        x2, y2 = (1, 1)
        dataset = {0.1: 1000, 
               0.5: 556,
               1.0: 1,
               1.5: -554}
        for x, y in dataset.items():
            self.assertTrue( abs(1 - toolbox.linear_interpolation(x, x1,y1, x2,y2) / y) < eps)

    def test_log_interpolation(self):
        eps = 1.0e-7
        x1, y1 = (0.1, 1000)
        x2, y2 = (1, 1)
        dataset = {0.1: 1000, 
               0.5: 46.41588833,
               1.0: 1,
               1.5: 0.0215443469}
        for x, y in dataset.items():
            self.assertTrue( abs(1 - toolbox.log_interpolation(x, x1,y1, x2,y2) / y) < eps)

    def test_isDataLine(self):
        self.assertEquals(toolbox.isDataLine("1 2 3"), True)
        self.assertEquals(toolbox.isDataLine("#1 2 3"), False)

    def test_Iswap(self):
        self.assertEquals(toolbox.Iswap("a", "b"), ("b", "a"))
        self.assertNotEquals(toolbox.Iswap("a", "b"), ("a", "b"))

    def test_BSearch(self):
        x = toolbox.GetDat(expected_datafile)[0]
        dataset = {-1e100: (False, -1), 1e+100: (False, 250)}
        for v in (2, 11, 12, 13):
            dataset[ x[v] ] = (True, v)
        dataset[ (x[0]+x[-1])/2 ] = (True, 219)
        for z, v in dataset.items():
            self.assertTrue(toolbox.BSearch(z, x) == v)

    def test_GetDat(self):
        x_y_dy = toolbox.GetDat(expected_datafile)
        self.assertEquals(len(x_y_dy), 3)
        # test some more stuff here ...
        self.assertRaises(Exception, toolbox.GetDat, missing_datafile)

    def test_find_first_index(self):
        x = toolbox.GetDat(expected_datafile)[0]
        self.assertEquals( toolbox.find_first_index(x, 0.08), 211 )
        self.assertEquals( toolbox.find_first_index(x, 0), 0 )
        self.assertEquals( toolbox.find_first_index(x, 200), None )


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
