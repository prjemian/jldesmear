#!/usr/bin/env python

'''
superclass of functions for extrapolation of SAS data past available range
'''

########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

import StatsReg


__metaclass__ = type # new style classes


class Extrapolation:
    '''
    superclass of functions for extrapolation of SAS data past available range
    
    The general case to (forward) slit-smear small-angle scattering involves
    integration at :math:`q` values past any measurable range.  
    
    .. math::
    
        \\int_{-\\infty}^{\\infty} P_l(q_l) I(q,q_l) dq_l.
    
    Due to symmetry, the integral is usually folded around zero,thus becoming 
    
    .. math::
    
        2 \\int_0^{\\infty} P_l(q_l) I(q,q_l) dq_l.
    
    Even when the upper limit is reduced due to finite slit dimension (the 
    so-called slit-length, :math:`l_0`), 
    
    .. math::
    
        2 l_0^{-1} \int_0^{\l_0} I(\sqrt{q^2+q_l^2}) dq_l,
    
    it is still necessary to evaluate :math:`I(\sqrt{q^2+q_l^2})` beyond
    the last measured data point, just to evaluate the integral.
    
    An extrapolation function is used to describe the :math:`I(q)` beyond the measured data.
    In the most trivial case, zero would be returned.  Since this simplification
    is known to introduce truncation errors, an model form for the last few 
    available data points is assumed.  Fitting coefficients are determined from
    the final data points (in the method :meth:`fit()`) and are used 
    subsequently to generate the extrapolation at a specific :math:`q` value
    (in the method :meth:`calc()`).
    
    Examples:
    
    See the subclasses for examples how to implement a new extrapolation function.
    
    * :mod:`lake.extrap_constant`
    * :mod:`lake.extrap_linear`
    * :mod:`lake.extrap_power`
    * :mod:`lake.extrap_porod`
    
    Basics:
    
    The basic methods to override are
    
    * :meth:`__str__()` : string representation
    * :meth:`calc()` : determines :math:`I(q)` from ``q`` and ``self.coefficients`` dictionary
    * :meth:`fit_result()` : assigns fit coefficients to ``self.coefficients`` dictionary
    '''

    def __init__(self):
        '''
        set things up
        
        :note: must override in subclass
        '''
        self.coefficients = {}  # dictionary of coefficients used in the function

    def __str__(self):
        '''
        return a text string showing the functional form, such as::
        
            def __str__(self):
                return "I(q) = zero"
        
        :note: **must** override in subclass
        
        :return: string
        '''
        raise("__str__(self) must be defined for each subclass")

    def calc(self, q):
        '''
        evaluate the extrapolation function at the given q

        :note: **must** override in subclass
        
        :param float q: magnitude of scattering vector
        :return: value of extrapolation function at *q*
        :rtype: float
        '''
        raise("calc(self, q) must be defined for each subclass")

    def fit(self, q, I, dI):
        '''
        fit the function coefficients to the data
        
        :note: *might* override in subclass

        :param float q: magnitude of scattering vector
        :param float I: intensity or cross-section
        :param float dI: estimated uncertainty of intensity or cross-section
        '''
        reg = self.fit_setup()
        self.fit_loop(reg, q, I, dI)
        self.fit_result(reg)

    def fit_setup(self):
        '''
        Create a set of statistics registers to evaluate 
        the coefficients of the curve fit.  Called from :meth:`fit()`.
        
        :note: *might* override in subclass
        :return: statistics registers
        :rtype: StatsRegClass object
        '''
        return StatsReg.StatsRegClass()

    def fit_loop(self, reg, x, y, z):
        ''' 
        Add a dataset to the statistics registers 
        for use in curve fitting.  Called from :meth:`fit()`.
        
        :note: *might* override in subclass

        :param reg: statistics registers (created in fit())
        :type reg: StatsRegClass object
        :param [float] x: independent axis
        :param [float] y: dependent axis
        :param [float] z: estimated uncertainties of y
        '''
        for i in range(len(x)):
            self.fit_add(reg, x[i], y[i], z[i])

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
        reg.Add(x, y)

    def fit_result(self, reg):
        '''
        Determine the results of the fit and store them
        as the set of coefficients in the self.coefficients 
        dictionary.  Called from :meth:`fit()`.
        
        Example::

            def fit_result(self, reg):
                (constant, slope) = reg.LinearRegression()
                self.coefficients['B']  = constant
                self.coefficients['m']  = slope
        
        :note: *must* override in subclass otherwise :meth:`fit_result()` will raise an exception
        :param reg: statistics registers (created in :meth:`fit()`)
        :type reg: StatsRegClass object
        '''
        # example: self.coefficients['B']  = constant
        raise("fit_result() must be defined for each subclass")

    def show(self):
        ''' 
        print the function and fit coefficients
        
        :note: *might* override in subclass
        '''
        reply = str(self) + "\n"
        for key, value in self.coefficients.items():
            reply += self.format_coefficient(key, value)
        return reply

    def format_coefficient(self, key, value):
        ''' 
        Format a specific coefficient.
        Called from :meth:`show()`.
        
        :note: *might* override in subclass

        :param str key: name of coefficient (must exist in self.coefficients dictionary)
        :param value: usually value of self.coefficients[key]
        :type value: usually float
        '''
        return "coefficient: %s = %g\n" % (key, value)

    def GetCoefficients(self):
        '''return the function coefficients'''
        return self.coefficients

    def SetCoefficients(self, coefficients):
        '''define the function coefficients
        
        :param dict coefficients: named terms used in evaluating the extrapolation
        '''
        self.coefficients = coefficients
