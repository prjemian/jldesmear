#!/usr/bin/env python

'''
superclass of functions for extrapolation of SAS data past available range
'''

import os
import importlib
import glob
import sys
import StatsReg


functions = None


def discover_extrapolations():
    '''
    return a dictionary of the available extrapolations
    
    Extrapolation functions must be in a file named 
    ``extrap_KEY.py``
    where ``KEY`` is the key name of the extrapolation function.
    The file is placed in the source code tree in the same directory
    as the module: :mod:`~jldesmear.api.extrapolation`.
    
    The :meth:`calc` method should be capable of handling
    ``q`` as a ``numpy.ndarray`` or as a ``float``.
    
    The file must contain:

    * *Extrapolation*: a subclass of :class:`~jldesmear.api.extrapolation.Extrapolation`
    
    '''
    # TODO: allow user to provide additional extrapolation plugins
    global functions
    if functions is None:
        functions = {}
        owd = os.getcwd()
        path = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, path)
        os.chdir(path)
        for item in glob.glob('extrap_*.py'):
            modulename = os.path.splitext(item)[0]
            mod = importlib.import_module(modulename)
            if mod.Extrapolation.name is None:
                raise ValueError, 'class Extrapolation in ' + item + ' must define value for "name"'
            if mod.Extrapolation.name in functions:
                raise RuntimeError, modulename + ' extrapolation previously defined'
            functions[mod.Extrapolation.name] = mod.__dict__['Extrapolation']
        os.chdir(owd)
        sys.path.pop(0)
    return functions



class Extrapolation(object):
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
    is known to introduce truncation errors, a model form for the last few 
    available data points is assumed.  Fitting coefficients are determined from
    the final data points (in the method :meth:`fit()`) and are used 
    subsequently to generate the extrapolation at a specific :math:`q` value
    (in the method :meth:`calc()`).
    
    .. rubric:: Examples:
    
    See the subclasses for examples implementations of extrapolations.
    
    * :mod:`~jldesmear.api.extrap_constant`
    * :mod:`~jldesmear.api.extrap_linear`
    * :mod:`~jldesmear.api.extrap_powerlaw`
    * :mod:`~jldesmear.api.extrap_Porod`
    
    .. rubric:: Example Linear Extrapolation:
    
    Here is an example linear extrapolation class::

        import extrapolation

        class Extrapolation(extrapolation.Extrapolation):
            name = 'linear'        # unique identifier for users 
        
            def __init__(self):    # initialize whatever is needed internally
                self.coefficients = {'B': 0, 'm': 0}
        
            def __str__(self):
                form = "linear: I(q) = " + str(self.coefficients['B'])
                form += " + q*(" + str(self.coefficients['m']) + ")"
                return form
        
            def calc(self, q):    # evaluate at given q
                return self.coefficients['B'] + self.coefficients['m'] * q
        
            def fit_result(self, reg):    # evaluate fitting parameters with regression object
                (constant, slope) = reg.LinearRegression()
                self.coefficients = dict(B=constant, m=slope)
    
    .. rubric:: Basics:
    
    Create an Extrapolation class which is a subclass of :mod:`extrapolation.Extrapolation`. 
    
        The basic methods to override are
        
        * :meth:`__str__()` : string representation
        * :meth:`calc()` : determines :math:`I(q)` from ``q`` and ``self.coefficients`` dictionary
        * :meth:`fit_result()` : assigns fit coefficients to ``self.coefficients`` dictionary
    
    By default, the base class Extrapolation uses the :mod:`jldesmear.api.StatsReg` 
    module to accumulate data and evaluate fitted parameters.  
    Override any or all of these methods to define your own handling:
    
    * :meth:`~fit`
    * :meth:`~fit_setup`
    * :meth:`~fit_loop`
    * :meth:`~fit_add`
    * :meth:`~fit_result`
    * :meth:`~calc`
    * :meth:`~show`
    * :meth:`~format_coefficient`
    
    See the source code of :mod:`~jldesmear.api.extrap_Porod.Extrapolation` for an example.
    
    .. rubric:: documentation from source code:
    '''

    name = None                              # subclass must define: will be used as keyname to identify this class

    def __init__(self):
        '''
        set things up
        
        :note: must override in subclass
        '''
        self.coefficients = {}  # dictionary of coefficients used in the function
        self.name = None        

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
        :param numpy.ndarray x: independent axis
        :param numpy.ndarray y: dependent axis
        :param numpy.ndarray z: estimated uncertainties of y
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


def main():
    func_dict = discover_extrapolations()
    for k, v in func_dict.items():
        print k + ': ', v.__doc__


if __name__ == "__main__":
    main()
