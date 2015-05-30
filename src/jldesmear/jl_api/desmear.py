#!/usr/bin/env python

'''
Desmear SAS data

To desmear, apply the method of Jemian/Lake to 1-D SAS data *(q, I, dI)*.

Source Code Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
'''


import math
import pprint             #@UnusedImport
import os                 #@UnusedImport
import sys
import numpy
import smear
import textplots
import toolbox
import info


Weighting_Methods = {
    'constant':   'weight = 1.0',
    'ChiSqr':     'weight = CorrectedI / SmearedI',
    'fast':       'weight = 2*SQRT(ChiSqr(0) / ChiSqr(i))',
}


class Desmearing():
    ''' 
    desmear the 1-D SAS data *(q, I, dI)* by method of Jemian/Lake
    
    .. math::
    
        I_0 \\approx \\lim_{i \\rightarrow \\infty} I_{i+1} =  I_i \\times \\left({ \\tilde I_0 \\div \\tilde I_i}\\right)
    
    
    To start Lake's method, assume that the 0-th approximation 
    of the corrected intensity is the measured intensity.

    :param numpy.ndarray q: magnitude of scattering vector
    :param numpy.ndarray I: SAS data I(q) +/- dI(q)
    :param numpy.ndarray dI: estimated uncertainties of I(q)
    :param obj params: Info object with desmearing parameters
    
    .. note:: This equation shows the iterative feedback based 
       on the *fast* method (as described by Lake).
       Alternative feedback methods are available
       (see :func:`SetLakeWeighting`).
       It is suggested to **always** use the fast method.

    '''
    
    def __init__(self, q, I, dI, params):
        self.params = params
        self.q = q
        self.I = I
        self.dI = dI
        self.first_step()

    def first_step(self):
        '''
        the first step


        calculate the standardized residuals (:math:`z =` ``self.z`` )
        
        .. math::
        
          z = (\hat{y} - y) \sigma
        
        where ``y = S``, ``yHat = I``, and ``sigma = dI``
        


        calculate the chi-squared statistic (:math:`\chi^2 =` ``self.ChiSqr`` )
        
        .. math::
        
          \chi^2 = \sum z^2

        '''
        self.C = numpy.array(self.I)        # desmeared intensity after current iteration
        self.dC = numpy.array(self.dI)      # estimated uncertainty of C

        n = len(self.I)
        self.S = 1+numpy.zeros( (n,) )      # smeared intensity from most recent C +/- dC
        self.z = numpy.zeros( (n,) )        # standardized residuals
        self.ChiSqr = []                    # ChiSqr vs. iterations
        self._smear()
        self.z = (self.S - self.I) / self.dI
        self.ChiSqr.append( numpy.sum(self.z*self.z) )
        self.iteration_count = len(self.ChiSqr)-1

    def traditional(self):
        '''
        the traditional LAKE code algorithm
        
        This method is called from the class constructor.  
        If this method is called directly, it has the effect 
        of clearing any desmearing progress and resetting 
        back to start.  This technique is used here if
        the list of ChiSqr results is not empty.
        '''
        if len(self.ChiSqr) > 1:
            # clear it out and start again
            self.first_step()
        done = False

        while not done:
            self.iteration()
            quit_requested = False
            if self.params.callback != None:
                quit_requested = self.params.callback(self)
            more_steps = self.params.moreIterationsOk(self.iteration_count)
            done = quit_requested or not more_steps

    def iteration(self):
        '''
        Compute one iteration of the Lake algorithm.
        
        No need to call the callback routine, 
        the caller can take care of that directly.
        '''
        self._refine_desmeared()
        self._smear()
        self.z = (self.S - self.I) / self.dI
        self.ChiSqr.append( numpy.sum(self.z*self.z) )
        self.iteration_count = len(self.ChiSqr)-1

    def iterate_and_callback(self):
        '''
        Compute one iteration of the Lake algorithm
        and then call the supplied callback method.
        Use this method to run a desmearing operation in another thread.
        '''
        self.iteration()
        if self.params.callback != None:
            self.params.callback(self)

    def _smear(self):
        '''
        Compute the slit-smeared intensity (S) from current 
        iteration desmeared intensity (C +/- dC)
        
        Changes ``self.S``
        '''
        try:
            self.S, extrap = smear.Smear(
                self.q, self.C, self.dC, 
                self.params.extrapname, 
                self.params.sFinal, 
                self.params.slitlength, 
                self.params.quiet
            )
            # TODO: this interface looks inefficient now, unless extrap could change each iteration (?possible new feature?)
            self.SetExtrap(extrap)
        except:
            raise Exception, "Smearing failed: " + str(sys.exc_info())

    def _refine_desmeared(self):
        '''
        calculate the next desmeared intensity
        from the current desmeared and smeared intensities
        '''
        if self.params.LakeWeighting == "constant":
            weight = numpy.ones((len(self.C),))
        elif self.params.LakeWeighting == "ChiSqr":
            ratio = self.ChiSqr[0]/self.ChiSqr[-1]
            weight = 2*math.sqrt(ratio) * numpy.ones((len(self.C),))
        elif self.params.LakeWeighting == "fast":
            weight = self.C / self.S
        
        # apply the weight to get the corrected terms
        self.C += weight * (self.I - self.S)

    def SetExtrap(self, extrapolation_object = None):
        '''
        :param obj extrapolation_object: class used for extrapolation function
        '''
        self.params.extrap = extrapolation_object

    def SetLakeWeighting(self, LakeWeighting = 'fast'):
        '''
        :param str LakeWeighting: one of *constant*, *ChiSqr*, or *fast*
        
        :constant:   weight = 1.0
        :ChiSqr:     weight = CorrectedI / SmearedI
        :fast:       weight = 2*SQRT(ChiSqr(0) / ChiSqr(i))
        '''
        global Weighting_Methods
        choices = sorted(Weighting_Methods.keys())
        if LakeWeighting not in choices:
            msg = "LakeWeighting must be one of " + str(choices)
            msg += ", got "  + LakeWeighting
            raise( msg )
        self.params.LakeWeighting = LakeWeighting

    def SetQuiet(self, suppress_output = True):
        '''
        if True, then no printed output from this routine
        '''
        self.params.quiet = suppress_output


def __callback (dsm):
    '''
    this function is called after every desmearing iteration
    
    :param obj dsm: Desmearing object
    :return: should desmearing stop?
    :rtype: bool
    '''
    title = "standardized residuals, ChiSqr = %g, iteration %d" % (dsm.ChiSqr[-1], dsm.iteration_count)
    textplots.Screen().residualsplot(dsm.z, title)
    reply = 'y'
    if dsm.params.NumItr == info.INFINITE_ITERATIONS:
        reply = toolbox.AskYesOrNo ("Continue?", reply)
        print("reply: <%s>" % reply)
    return reply.lower() == 'n'


def __demo():
    '''show the various routines'''
    print("Testing $Id$")

    params = info.Info()
    if params == None:
        return          # no input file so quit the program

    # define the parameters for the test data
    params.infile = toolbox.GetTest1DataFilename('.smr')
    params.outfile = "test.dsm"
    params.slitlength = 0.08           # s: slit length, as defined by Lake
    params.sFinal = 0.08               # fit extrapolation constants for q>=sFinal
    params.NumItr = 20                 # *only* 20 iterations
    params.extrapname = "linear"       # better for the test1.smr data set
    params.callback = __callback       # use our local callback function

    print str(params)

    q, E, dE = toolbox.GetDat(params.infile)
    if (len(q) == 0):
        raise ("no data points!")
    if (params.sFinal > q[-1]):
        raise( "Fit range out of data range" )
    
    dsm = Desmearing(q, E, dE, params)
    dsm.traditional()

    toolbox.SavDat(params.outfile, dsm.q, dsm.C, dsm.dC)

    lnq = numpy.log(q)
    lnE = numpy.log(E)
    lnC = numpy.log(dsm.C)
    plot = textplots.Screen()
    plot.addtrace(lnq, lnE, "S")
    plot.addtrace(lnq, lnC, "D")
    plot.SetTitle("\nSAS log-log plot, final, S=input, D=desmeared")
    plot.printplot()


if __name__ == "__main__":
    __demo()
