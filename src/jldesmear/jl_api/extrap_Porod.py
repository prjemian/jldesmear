#!/usr/bin/env python

'''
Extrapolate as:  I(q) = B + Cp / q^4
'''


import extrapolation
import toolbox
import math
import pprint
import os       #@UnusedImport
import numpy    #@UnusedImport


class Extrapolation(extrapolation.Extrapolation):
    '''I(q) = B + Cp / q^4'''
    name = 'Porod'

    def __init__(self):
        '''set up things'''
        self.coefficients = {'Cp': 0, 'B': 0}

    def __str__(self):
        ''':return: a text string showing the functional form'''
        form = "Porod law: I(q) = " + str(self.coefficients['B'])
        form += " + (" + str(self.coefficients['Cp']) + ")"
        form += " / q^4"
        return form

    def calc(self, q):
        '''
        .. math::
        
            I(q) = B + C_p / q^4
        
        :param float q: magnitude of scattering vector
        :return: value of extrapolation function at *q*
        :rtype: float
        '''
        Cp = self.coefficients['Cp']
        B = self.coefficients['B']
        result = B + Cp / (q*q*q*q)
        return result

    def fit_add(self, reg, x, y, z):
        ''' 
        Add a data point to the statistics registers.
        Called from :meth:`fit_loop()`.
        
        :note: *might* override in subclass
        :param obj reg: statistics registers (created in 
                        :meth:`~jldesmear.api.extrapolation.Extrapolation.fit()`), instance of StatsRegClass
        :param float x: independent axis
        :param float y: dependent axis
        :param float z: estimated uncertainty of y
        '''
        #reg.AddWeighted(x, y, z)
        q4 = math.pow(x, 4)
        reg.Add(q4, q4 * y)

    def fit_result(self, reg):
        ''' 
        Determine the results of the fit and store them
        as the set of coefficients in the self.coefficients 
        dictionary.  Called from :meth:`fit()`.
        
        :note: *must* override in subclass otherwise :meth:`fit_result()` will throw an exception
        :param obj reg: statistics registers (created in :meth:`fit()`), instance of StatsRegClass
        '''
        (constant, slope) = reg.LinearRegression()
        self.coefficients['Cp']  = constant
        self.coefficients['B']  = slope


if __name__ == "__main__":
    '''show the various routines'''
    print("Testing $Id$")
    func = Extrapolation
    print("using default coefficients")
    fit = func()
    print(fit.show().strip())
    print("I(%g) = %g" % (0.001, fit.calc(0.001)))
    print("I(%g) = %g" % (0.02, fit.calc(0.02)))
    pprint.pprint(fit.GetCoefficients())
    print("#--------------------------")
    print("setting coefficients")
    fit.SetCoefficients({'B': 163724, 'Cp': 9.65e-10})
    print(fit.show().strip())
    print("I(%g) = %g" % (0.0004, fit.calc(0.0004)))
    print("I(%g) = %g" % (0.0005, fit.calc(0.0005)))
    pprint.pprint(fit.GetCoefficients())
    print("#--------------------------")
    print("fitting coefficients")
    fn = toolbox.GetTest1DataFilename('.smr')
    x, y, dy = toolbox.GetDat( fn )
    fit = func()
    fit.fit(x, y, dy)
    print(fit.show().strip())
    print("I(%g) = %g" % (x[0], fit.calc(x[0])))
    print("I(%g) = %g" % (x[-1], fit.calc(x[-1])))
    pprint.pprint(fit.GetCoefficients())
