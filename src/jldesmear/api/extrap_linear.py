#!/usr/bin/env python

'''
Extrapolate as:  I(q) = B + m * q
'''


import extrapolation
import toolbox
import pprint
import os       #@UnusedImport
import numpy    #@UnusedImport


class Extrapolation(extrapolation.Extrapolation):
    '''I(q) = B + m*q'''
    name = 'linear'

    def __init__(self):
        '''set up things'''
        self.coefficients = {'B': 0, 'm': 0}

    def __str__(self):
        ''':return: a text string showing the functional form'''
        form = "linear: I(q) = " + str(self.coefficients['B'])
        form += " + q*(" + str(self.coefficients['m']) + ")"
        return form

    def calc(self, q):
        '''
        .. math::
        
            I(q) = B + m q
        
        :param float q: magnitude of scattering vector
        :return: value of extrapolation function at *q*
        :rtype: float
        '''
        B = self.coefficients['B']
        m = self.coefficients['m']
        result = B + m * q
        return result

    def fit_result(self, reg):
        ''' 
        Determine the results of the fit and store them
        as the set of coefficients in the self.coefficients 
        dictionary.  Called from :meth:`fit()`.
        
        :note: *must* override in subclass otherwise :meth:`fit_result()` will throw an exception
        :param reg: statistics registers (created in :meth:`fit()`)
        :type reg: StatsRegClass object
        '''
        (constant, slope) = reg.LinearRegression()
        self.coefficients['B']  = constant
        self.coefficients['m']  = slope


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
    fit.SetCoefficients({'B': 0.1, 'm': -1})
    print(fit.show().strip())
    print("I(%g) = %g" % (0.001, fit.calc(0.001)))
    print("I(%g) = %g" % (0.02, fit.calc(0.02)))
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
