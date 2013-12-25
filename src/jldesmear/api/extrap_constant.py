#!/usr/bin/env python

'''
Extrapolate as:  I(q) = B
'''


import extrapolation
import toolbox
import pprint
import os


class Constant(extrapolation.Extrapolation):
    '''I(q) = B'''

    def __init__(self):
        '''set up things'''
        self.coefficients = {'B': 0}

    def __str__(self):
        ''':return: a text string showing the functional form'''
        form = "constant: I(q) = " + str(self.coefficients['B'])
        return form

    def calc(self, q):
        ''' 
        .. math::
        
            I(q) = B
        
        :param float q: magnitude of scattering vector
        :return: value of extrapolation function at *q*
        :rtype: float
        '''
        return self.coefficients['B']

    def fit_result(self, reg):
        ''' 
        Determine the results of the fit and store them
        as the set of coefficients in the self.coefficients 
        dictionary.  Called from :meth:`fit()`.
        
        :note: *must* override in subclass otherwise :meth:`fit_result()` will throw an exception
        :param reg: statistics registers (created in :meth:`fit()`)
        :type reg: StatsRegClass object
        '''
        self.coefficients['B']  = reg.Mean()[1]


extrapolation_class = Constant


if __name__ == "__main__":
    '''show the various routines'''
    print("Testing $Id$")
    func = Constant
    print("using default coefficients")
    fit = func()
    print(fit.show().strip())
    print("I(%g) = %g" % (0.001, fit.calc(0.001)))
    print("I(%g) = %g" % (0.02, fit.calc(0.02)))
    pprint.pprint(fit.GetCoefficients())
    print("#--------------------------")
    print("setting coefficients")
    fit.SetCoefficients({'B': 0.1})
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


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
