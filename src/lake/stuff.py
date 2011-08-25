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


import lake
import math
import pprint
import smear
import StatsReg
import textplots
import toolbox
import info
import os


def Desmear (q, I, dI, info, callback, quiet = False):
    '''
    desmear the 1-D SAS data *(q, I, dI)* by method of Jemian/Lake
    
    .. math::
    
        I_0 \\approx \\lim_{i \\rightarrow \\infty}\\tilde I_{i+1} =  I_i \\times \\left({ \\tilde I_0 \\div \\tilde I_i}\\right)
    
    :param [float] q: magnitude of scattering vector
    :param [float] I: SAS data I(q) +/- dI(q)
    :param [float] dI: estimated uncertainties of I(q)
    :param dict info: dictionary of desmearing parameters
    :param object callback: function to call after each iteration
    :param bool quiet: if True, then no printed output from this routine
    :return: tuple of corrected/desmeared SAS (C, dC)
    :rtype: ([float], [float])
    '''
    NumPts = len(q)
    C, dC = [0]*NumPts, [0]*NumPts  # corrected intensity (results)
    #  To start Lake's method, assume that the 0-th approximation 
    #    of the corrected intensity is the measured intensity.
    for i in range(NumPts):
        C[i] = I[i]
        dC[i] = dI[i]
    extrapname = info["extrapname"]
    sFinal = info["sFinal"]
    slitlength = info["slitlength"]
    ChiSqr0 = None
    weighting = 1.0
    maximum_iterations = info["NumItr"]
    fixed_iterations = (maximum_iterations > 0)
    if maximum_iterations < 0:
        maximum_iterations = -maximum_iterations
    for iteration in range(maximum_iterations):
        # smear this iteration
        try:
            S, extrap = smear.Smear(q, C, dC, 
                        extrapname, sFinal, slitlength, quiet)
        except Exception, e:
            print("")
            raise Exception, "Smearing failed: " + str(e)
            #raise Exception, e
    
        ChiSqr = 0.0                        # find the ChiSqr
        for i in range(NumPts):
            ChiSqr += math.pow((S[i] - I[i])/dI[i], 2)
        if ChiSqr0 == None:
            ChiSq0 = ChiSqr                 # remember the first one

        if info["LakeWeighting"] == "constant":
            weighting = 1
        if info["LakeWeighting"] == "ChiSqr":
            weighting = 2*math.sqrt(ChiSq0/ChiSqr)
        for i in range(NumPts):
            if info["LakeWeighting"] == "fast":
                weighting = C[i] / S[i]
            C[i] += weighting * (I[i] - S[i])
        #dC = FixErr (q, I, dI, C);
        if fixed_iterations:
            # caller-supplied function
            if callback(q, I, dI, C, S, iteration, ChiSqr, info, extrap):
                break
    return C, dC


def FixErr(x, y, dy, z):
    '''
    Estimate the error on Z based on data point scatter and
    previous error values and smooth that estimate.
    
    :param [float] x: independent axis
    :param [float] y: dependent axis
    :param [float] dy: estimated uncertainties of y
    :param [float] z: adjusted dependent axis
    :return: dz, estimated uncertainties of z
    :rtype: [float]
    '''
    scatter = examine_scatter (x, y, dy, z)  # Add this to dz.

    #/* Error proportional to input error */
    dz = [0]*len(y)
    for i in range( len(y) ): 
        dz[i] = z[i] * dy[i] / y[i] 
        dz[i] += scatter[i]

    # Smooth the error by a 3-point moving average filter.
    # Apply the moving average filter 5 times.
    #
    # Smoothing is necessary to refine (and likely increase) the error estimate
    # for some grossly under-estimated errors.
    for count in range(5):
        dz = moving_average_filter(x, dz)
    return dz


def moving_average_filter (x, y):
    '''
    Smooth `y(x)` by a 3-point moving average filter.
    Do not smooth the end points.

    Weight the data points by distance^2 (as a penalty)
    using the function weight(u,v)= :math:`(1 - |1 - u/v|)^2`
    
    By its definition, weight(x0,x0) == 1.0.  
    
    I speed computation using this definition.

    :param [float] x: independent axis
    :param [float] y: dependent axis
    :return: smoothed version of ``y(x)``
    :rtype: [float]
    '''
    r = [0]*len(x)
    for i in range(1, len(x)-1):
        w1 = math.pow(1 - math.fabs(1 - x[i-1]/x[i]) ,2)
        w2 = math.pow(1 - math.fabs(1 - x[i+1]/x[i]) ,2)
        r[i] = (w1 * y[i-1] + y[i] + w2 * y[i+1]) / (w1 + 1.0 + w2)
    return r


def examine_scatter (x, y, dy, z):
    '''
    Error based on scatter of desmeared data points.
    Determine this by fitting a line to the points
    i-1, i, i+1 and take the difference.  Add this to dz.

    :param [float] x: independent axis
    :param [float] y: dependent axis
    :param [float] dy: estimated uncertainties of ``y``
    :param [float] z: adjusted dependent axis
    :return: estimated uncertainties of ``z``
    :rtype: [float]
    '''
    dz = [0]*len(y)
    sr = StatsReg.StatsRegClass()
    for i in (0, 1, 2):
        sr.Add(x[i], z[i])
    for i in (0, 1):
        dz[i] = math.fabs( sr.LinearEval(x[i]) - z[i])
    for i in range(2, len(y)-1):
        sr.Subtract(x[i-2], z[i-2])
        sr.Add(x[i+1], z[i+1])
        zNew = sr.LinearEval(x[i])
        dz[i] = math.fabs(zNew - z[i])
    dz[-1] = math.fabs( sr.LinearEval(x[-1]) - z[-1])
    return dz


def __callback (q, I, dI, C, S, iteration, ChiSqr, info=None, extrap=None):
    '''
    this function is called after every desmearing iteration
    
    :param [float] q: array (list)
    :param [float] I: array (list) of SAS data I(q) +/- dI(q)
    :param [float] dI: array (list)
    :param [float] S: array (list) of smeared intensity
    :param [float] C: array (list) of corrected intensity
    :param int iteration: iteration number
    :param float ChiSqr: Chi-Squared value
    :param dict info: dictionary of input parameters
    :param object extrap: extrapolation function structure
    :return: should desmearing stop?
    :rtype: bool
    '''
    n = len(q)
    z = [0]*n
    for i in range(n):
        z[i] = (S[i] - I[i]) / dI[i]
    title = "standardized residuals, ChiSqr = %g, iteration %d" % (ChiSqr, iteration)
    textplots.Screen().residualsplot(z, title)
    reply = toolbox.AskYesOrNo ("Continue?", "y")
    print("reply: <%s>" % reply)
    return reply == 'n'


def __demo():
    '''show the various routines'''
    print("Testing $Id$")
    info = {                # set the defaults
        "infile": "", 
        "outfile": "",
        "slitlength": 1.0,              # s: slit length, as defined by Lake
        "sFinal": 1.0,                  # fit extrapolation constants for q>=sFinal
        "NumItr": 10000,                # number of desmearing iterations
        "extrapname": "constant",       # model final data as a constant
        "LakeWeighting": "fast",        # shows the fastest convergence most times
    }
    # override default constants for code development
    info["infile"] = os.path.join('..', '..', 'data', 'test1.smr')
    info["outfile"] = "test.dsm"
    info["slitlength"] = 0.08           # s: slit length, as defined by Lake
    info["sFinal"] = 0.08               # fit extrapolation constants for q>=sFinal
    info["NumItr"] = 10                 # *only* 20 iterations

    pprint.pprint(info)

    if info == None:
        return          # no input file so quit the program
    if (info["NumItr"] == 0):
        info["NumItr"] = lake.INFINITE_ITERATIONS;
    print("Input file: " + info["infile"])
    q, E, dE = toolbox.GetDat(info["infile"])
    if (len(q) == 0):
        raise Exception, "no data points!"
    if (info["sFinal"] > q[-1]):
        raise Exception, "Fit range out of data range"
    C, dC = Desmear(q, E, dE, info, __callback)
    toolbox.SavDat(info["outfile"], q, C, dC)
    n = len(q)
    lnq, lnE, lnC = [0]*n, [0]*n, [0]*n
    for i in range(n):
        lnq[i] = math.log(q[i])
        lnE[i] = math.log(E[i])
        lnC[i] = math.log(C[i])
    plot = textplots.Screen()
    plot.addtrace(lnq, lnE, "S")
    plot.addtrace(lnq, lnC, "D")
    plot.SetTitle("\nSAS log-log plot, final, S=input, D=desmeared")
    plot.printplot()


if __name__ == "__main__":
    __demo()
