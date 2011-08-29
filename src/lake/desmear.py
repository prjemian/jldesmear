#!/usr/bin/env python

'''
$Id$

To desmear, apply the method of Jemian/Lake to 1-D SAS data *(q, I, dI)*.

Source Code Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
'''


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################


import math
import pprint
import smear
import textplots
import toolbox
import info
import os
import sys


class Desmearing():
    ''' 
    desmear the 1-D SAS data *(q, I, dI)* by method of Jemian/Lake
    
    .. math::
    
        I_0 \\approx \\lim_{i \\rightarrow \\infty}\\tilde I_{i+1} =  I_i \\times \\left({ \\tilde I_0 \\div \\tilde I_i}\\right)
    
    
    To start Lake's method, assume that the 0-th approximation 
    of the corrected intensity is the measured intensity.

    :param [float] q: magnitude of scattering vector
    :param [float] I: SAS data I(q) +/- dI(q)
    :param [float] dI: estimated uncertainties of I(q)
    :param obj params: Info object with desmearing parameters
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
        '''
        self.C = list(self.I)       # desmeared intensity after current iteration
        self.dC = list(self.dI)     # estimated uncertainty of C

        self.S = [1.0]*len(self.I)  # smeared intensity from most recent C +/- dC
        self.z = [0.0]*len(self.I)  # standardized residuals
        self._smear()
        self.ChiSqr = []
        self.ChiSqr.append( self._calc_ChiSqr() )
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
        compute one iteration of the Lake algorithm
        
        no need to call the callback routine, 
        the caller can take care of that directly
        '''
        self._refine_desmeared()
        self._smear()
        self.ChiSqr.append( self._calc_ChiSqr() )
        self.iteration_count = len(self.ChiSqr)-1

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
            weighting = 1
        elif self.params.LakeWeighting == "ChiSqr":
            weighting = 2*math.sqrt(self.ChiSqr[0]/self.ChiSqr[-1])

        # apply the weight to get the corrected terms
        for i in range(len(self.I)):
            if self.params.LakeWeighting == "fast":
                weighting = self.C[i] / self.S[i]
            self.C[i] += weighting * (self.I[i] - self.S[i])

    def _calc_ChiSqr(self):
        '''
        calculate the chi-squared statistic
        
        .. math::
        
          \chi^2 = \sum z^2
        
        where ``z`` is the [float] of standardized residuals
        
        :return: ChiSqr
        :rtype: float
        '''
        self._calc_residuals()
        result = 0.0
        for z in self.z:
            result += z*z
        return result

    def _calc_residuals(self):
        '''
        calculate the standardized residuals ( ``self.z`` )
        
        .. math::
        
          z = (\hat{y} - y) \sigma
        
        where ``y = S``, ``yHat = I``, and ``sigma = dI``
        
        calculates a new ``self.z``
        '''
        for i in range(len(self.I)):
            self.z[i] = (self.S[i] - self.I[i]) / self.dI[i]

    def SetExtrap(self, extrapolation_object = None):
        '''
        :param obj extrapolation_object: class used for extrapolation function
        '''
        self.params.extrap = extrapolation_object

    def SetLakeWeighting(self, LakeWeighting = 'fast'):
        '''
        :param str LakeWeighting: one of ``constant``,  ``ChiSqr``, or ``fast``
        '''
        choices = ('constant', 'ChiSqr', 'fast')
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

    # override default constants for code development
    params.infile = os.path.join('..', '..', 'data', 'test1.smr')
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
    n = len(q)
    lnq, lnE, lnC = [0]*n, [0]*n, [0]*n
    for i in range(n):
        lnq[i] = math.log(q[i])
        lnE[i] = math.log(E[i])
        lnC[i] = math.log(dsm.C[i])
    plot = textplots.Screen()
    plot.addtrace(lnq, lnE, "S")
    plot.addtrace(lnq, lnC, "D")
    plot.SetTitle("\nSAS log-log plot, final, S=input, D=desmeared")
    plot.printplot()


if __name__ == "__main__":
    __demo()
