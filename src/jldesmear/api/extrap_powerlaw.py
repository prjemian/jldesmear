#!/usr/bin/env python

'''
Extrapolate as:  I(q) = A * q^p
'''


import extrapolation
import toolbox
import math
import pprint
import os       #@UnusedImport
import numpy    #@UnusedImport


class Extrapolation(extrapolation.Extrapolation):
    '''I(q) = A * q^p'''
    name = 'powerlaw'

    def __init__(self):
        '''set up things'''
        self.coefficients = {'A': 0, 'p': 0}

    def __str__(self):
        ''':return: a text string showing the functional form'''
        #return "power law: I(q) = A * q^p"
        form = "power law: I(q) = " + str(self.coefficients['A'])
        form += " * q^(" + str(self.coefficients['p']) + ")"
        return form

    def calc(self, q):
        '''
        .. math::
        
            I(q) = A \ q^p

        :param float q: magnitude of scattering vector
        :return: value of extrapolation function at *q*
        :rtype: float
        '''
        A = self.coefficients['A']
        p = self.coefficients['p']
        if isinstance(q, numpy.ndarray):
            expo = p * numpy.ones_like(q)
            basis = numpy.power(q, expo)
        else:
            basis = math.pow(q, p)
        result = A * basis
        return result

    def fit_add(self, reg, x, y, z):
        ''' 
        Add a data point to the statistics registers.
        Called from :meth:`fit_loop()`.
        
        :note: *might* override in subclass
        :param reg: statistics registers (created in :meth:`fit()`)
        :type reg: StatsRegClass object
        :param float x: independent axis
        :param float y: dependent axis
        :param float z: estimated uncertainty of y
        '''
        #reg.AddWeighted(x, y, z)
        reg.Add(math.log(x), math.log(y))

    def fit_result(self, reg):
        ''' 
        Determine the results of the fit and store them
        as the set of coefficients in the self.coefficients 
        dictionary.  Called from :meth:`fit()`.
        
        :note: *must* override in subclass otherwise :meth:`fit_result()` will throw an exception
        :param reg: statistics registers (created in :meth:`fit()`)
        :type reg: StatsRegClass object
        '''
        (lnA, p) = reg.LinearRegression()
        self.coefficients['A']  = math.exp(lnA)
        self.coefficients['p']  = p


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
    fit.SetCoefficients({'A': 2650, 'p': -.55})
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
