#!/usr/bin/env python


import unittest
import toolbox
import os           #@UnusedImport


missing_datafile = toolbox.GetTest1DataFilename('.txt')
expected_datafile = toolbox.GetTest1DataFilename('.smr')


class Test(unittest.TestCase):

    def test_isDataLine(self):
        self.assertEquals(toolbox.isDataLine("1 2 3"), True)
        self.assertEquals(toolbox.isDataLine("#1 2 3"), False)

    def test_Iswap(self):
        self.assertEquals(toolbox.Iswap("a", "b"), ("b", "a"))
        self.assertNotEquals(toolbox.Iswap("a", "b"), ("a", "b"))

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
