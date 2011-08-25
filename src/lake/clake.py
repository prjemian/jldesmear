#!/usr/bin/env python

'''
Summary

Direct translation of ``lake.c``.  
Deprecated version.
See :mod:`lake.lake` for the most-recent version.


Credits

:author: Pete R. Jemian
:organization: Late-Nite(tm) Software
:note: lake.py was derived from lake.c in 2009
:note: lake.c was derived from the FORTRAN program Lake.FOR
:note: Lake.FOR  25 May 1991
:see: P.R.Jemian,; Ph.D. thesis, Northwestern University (1990).
:see: J.A. Lake; ACTA CRYST 23 (1967) 191-194.

Overview

This program applies the iterative desmearing technique of Lake
to small-angle scattering data.  The way that the program works
is that the user selects a file of data *(x,y,dy)* to be desmeared.
If a file was not chosen, the program will end.  Otherwise the
user is then asked to specify the slit-length (in the units of the
x-axis); the *x* at which to begin fitting the last data points to a
power-law of *x*, the output file name, and the number of iterations
to be run.  Then the data file is opened, the data is read, and the
data file is closed.  The program begins iterating and shows an
indicator of progress on the screen in text format.

It is a mistake to run this program on data that has been desmeared
at least once (by this program) as you will see.  The problem is
that the program expects that the input data has been smeared, NOT
partially desmeared.  Lake's technique should be made to iterate
with the original, smeared data and subsequent trial solutions
of desmeared data.

The integration technique used by this program to smear the data
is the trapezoid-rule where the step-size is chosen by the
spacing of the data points themselves.  A linear
interpolation of the data is performed.  To avoid truncation
effects, a power-law extrapolation of the intensity
is made for all values beyond the range of available
data.  This region is also integrated by the trapezoid
rule.  The integration covers the region from ``l = 0``
up to ``l = lo``. (see routine :mod:`lake.smear`).
This technique allows the slit-length weighting function
to be changed without regard to the limits of integration
coded into this program.

Other deconvolution methods

* O. Glatter, ACTA CRYST 7 (1974) 147-153
* W.E. Blass & G.W.Halsey (1981).  
   "Deconvolution of Absorption Spectra."  
   New York City: Academic Press
* P.A. Jansson.  (1984) 
   "Deconvolution with Applications in Spectroscopy."  
   New York City: Academic Press.
* G.W.Halsey & W.E. Blass.
   "Deconvolution Examples"
   in "Deconvolution with Applications in Spectroscopy."
   Ed. P.A. Jansson.  (see above)

version control information::

 ########### SVN repository information ###################
 # $Date$
 # $Author$
 # $Revision$
 # $URL$
 # $Id$
 ########### SVN repository information ###################
'''


import copy
import math
import os
import pprint
import StatsReg
import string
import sys
import toolbox
import textplots


LakeUnit = 1
LakeFast = 2
LakeChi2 = 3


def DesmearData (OutFil, q, E, dE, sLengt, sFinal, mForm, NumItr, InfItr, LakeForm):
    #double ChiSqr, ChiSq0, weighting;
    #int i, j, iteration;
    #char reply[256], trimReply[256];

    NumPts = len(q)
    print("Number of points read: %d" % NumPts)
    print("Output file: %s" % OutFil)
    print("Slit length: %g (x-axis units)" % sLengt)
    print("Final form approx. will begin at: %g (x-axis units)" % sFinal)
    formNames = [
        "flat background, I(q) = B",
        "linear, I(h) = b + q * m",
        "power law, I = b * q^m",
        "Porod, I = Cp + B / q^4"
    ]
    print("Final form approximation: %s" % formNames[mForm-1])
    if NumItr < InfItr:
        print("Number of iterations: %d", NumItr)
    else:
        print("Infinite number of iterations")
    weightingNames = ["unity", "fast", "ChiSqr"]
    print("Iterative weighting: %s" % weightingNames[LakeForm])

    #/*
    # *  To start Lake's method, assume that the 0-th approximation
    # *    of the corrected intensity is the measured intensity.
    # */
    C = copy.deepcopy(E)
    dC = copy.deepcopy(dE)
    resid = [0]*NumPts
    print("\n Smearing to get first approximation...\n")
    S = Smear (q, C, dC, sLengt, mForm, sFinal)

    ChiSqr = 0.0                            #/* find the ChiSqr */
    for j in range(NumPts):
        ChiSqr += math.pow( (S[j] - E[j]) / dE[j], 2)
    ChiSq0 = ChiSqr                         #/* remember the first one */

    for iteration in range(NumItr):
        if NumItr < InfItr:
            print("\n Iteration #%d of %d iterations" % (iteration, NumItr))
        else:
            print("\n Iteration #%d" % iteration)
        print("\nApplying the iterative correction ...")
        sys.stdout.flush()
        if LakeForm == LakeUnit:
            weighting = 1.0
        elif LakeForm == LakeChi2:
            weighting = 2*math.sqrt(ChiSq0/ChiSqr)
        for j in range(NumPts):
            if LakeForm == LakeFast:
                weighting = C[j] / S[j]
            C[j] += weighting * (E[j] - S[j])

        print("Examining scatter to calculate the errors ...")
        sys.stdout.flush()
        dC = FixErr (q, E, dE, C)
        print("Smearing again ...")
        sys.stdout.flush()
        S = Smear (q, C, dC, sLengt, mForm, sFinal)
        ChiSqr = 0.0;
        for j in range(NumPts):
            resid[j] = (S[j] - E[j]) / dE[j]
            ChiSqr += math.pow(resid[j], 2)

        title = "\n Residuals plot for iteration #%d" % iteration
        textplots.Screen().residualsplot(resid, title)
        print("ChiSqr = %lg for #%d points" % (ChiSqr, NumPts))
        sys.stdout.flush()
        if NumItr >= InfItr:
            if toolbox.AskYesOrNo ("Save this data?", 'n') == 'y':
                OutFil = toolbox.AskString("What file name?", OutFil)
                if len(OutFil.strip()) > 0:
                    toolbox.SavDat (OutFil, q, C, dC)
            if toolbox.AskYesOrNo ("Continue iterating?", 'y') == 'n':
                iteration = InfItr
                break
            sys.stdout.flush()

    if NumItr < InfItr:
        toolbox.SavDat (OutFil, q, C, dC)
    sys.stdout.flush()
    lnq, lnC = [0]*NumPts, [0]*NumPts
    for i in range(NumPts):
        lnq[i] = math.log(q[i])
        lnC[i] = math.log (math.fabs (C[i]))
    #Plot (NumPts, q, C);
    title = "\nPlot of log(desmeared intensity) vs. q ..."
    textplots.Screen().xyplot(q, lnC, title)
    sys.stdout.flush()
    title = "\nPlot of log(desmeared intensity) vs. log(q) ..."
    textplots.Screen().xyplot(lnq, lnC, title)
    sys.stdout.flush()


def Smear(q, C, dC, sLengt, mForm, sFinal):
    '''
    Smear the data of C(q) into S using the slit-length
    weighting function "Plengt" and a power-law extrapolation
    of the data to avoid truncation errors.  Assume that
    Plengt goes to zero for l > lo (the slit length).
    
    Also assume that the slit length  function is symmetrical
    about l = zero.
    
    This routine is written so that if "Plengt" is changed
    (for example) to a Gaussian, that no further modification
    is necessary to the integration procedure.  That is,
    this routine will integrate the data out to "lo".
     '''
    NumPts = len(q)
    x, w = [0]*NumPts, [0]*NumPts

    fIntercept, fSlope = Prep(q, C, dC, mForm, sFinal)            #/* get coefficients */
    if mForm == 1:
        print("%25s fit: I = %g\n" % ("constant background", fIntercept))
    elif mForm == 2:
        print("%25s fit: I = (%g) + q*(%g)\n" % ("linear", fIntercept, fSlope))
    elif mForm == 3:
        print("%25s fit: I = (%g) * q^(%g)\n" % ("Power law", fIntercept, fSlope))
    elif mForm == 4:
        print("%25s fit: I = (%g) + (%g)/q^4\n" % ("Power law", fIntercept, fSlope))

    hLo = q[0]
    ratio = sLengt / (q[-1] - hLo)
    for i in range(NumPts):
        x[i] = ratio * (q[i] - hLo)     #/* values for "l" */
        w[i] = Plengt(x[i], sLengt)     #/* probability at "l" */

    w[0] *= x[1] - x[0]
    for i in range(1, NumPts-1):
        w[i] *= x[i+1] - x[i-1]         #/* step sizes */
    w[-1] = x[-1] - x[-2]

    S = [0]*NumPts
    for i in range(NumPts):             #/* evaluate each integral ... */
        toolbox.Spinner(i)
        hNow = q[i]                     #/* ... using trapezoid rule */
        sum = w[0] * FindIc (hNow, x[0], q, C, mForm, fIntercept, fSlope)
        for k in range(1, NumPts-1):
            sum += w[k] * FindIc (hNow, x[k], q, C, mForm, fIntercept, fSlope)
        S[i] = sum + w[-1] * FindIc(hNow, x[-1], q, C, mForm, fIntercept, fSlope)
    return S


def FindIc (x, y, q, C, mForm, fIntercept, fSlope):
    '''
    Determine the "corrected" intensity at u = SQRT (x*x + y*y)
    Note that only positive values of "u" will be searched!
    '''
    NumPts = len(q)
    u = math.hypot(x, y)            #/* circularly symmetric */
    iLo = toolbox.BSearch(u, q)[1]     #/* find index */
    iHi = iLo + 1
    if iLo < 0:
        raise Exception, "Bad value of u or q[] in FindIc()"
    if iLo < NumPts:
        if u == q[iLo]:
            value = C[iLo]          #/* exactly! */
        else:                       #/* linear interpolation */
            value = LinearInterpolation(u, q[iLo],C[iLo], q[iHi],C[iHi])
    else:                           #/* functional extrapolation */
        if mForm == 1:
            value = fIntercept
        elif mForm == 1:
            value = fIntercept + fSlope * u;
        elif mForm == 2:
            value = math.exp(fIntercept + fSlope * math.log(u))
        elif mForm == 3:
            value = fIntercept + fSlope * math.pow(u, -4)
    return value


def FixErr(x, y, dy, z):
    '''
    Estimate the error on Z based on data point scatter and
    previous error values and smooth that estimate.
    '''

    #/* Error proportional to input error */
    n = len(x)
    dz = [0]*n
    for i in range(n): 
        dz[i] = z[i] * dy[i] / y[i]

    #/*
    # *  Error based on scatter of desmeared data points.
    # *    Determine this by fitting a line to the points
    # *    i-1, i, i+1 and take the difference.  Add this to dz.
    # */
    sr = StatsReg.StatsRegClass()
    sr.Add(x[0], z[0])
    sr.Add(x[1], z[1])
    sr.Add(x[2], z[2])
    slope, intercept = sr.LinearRegression()
    dz[0] += math.fabs(intercept + slope*x[0] - z[0])
    dz[1] += math.fabs(intercept + slope*x[1] - z[1])
    for i in range(2, n-1):
        sr.Clear()
        sr.Add(x[i-1], z[i-1])
        sr.Add(x[i],   z[i])
        sr.Add(x[i+1], z[i+1])
        slope, intercept = sr.LinearRegression()
        zNew = intercept + slope * x[i]
        dz[i] += math.fabs(zNew - z[i])
    dz[-1] += math.fabs(intercept + slope*x[-1] - z[-1])

    #/*
    # *  Smooth the error by a 3-point moving average filter.
    # *    Do this 5 times.  Don't smooth the end points.
    # *    Weight the data points by distance^2 (as a penalty)
    # *    using the function weight(u,v)=(1 - |1 - u/v|)**2
    # *    By its definition, weight(x0,x0) == 1.0.  I speed
    # *    computation using this definition.  Why I can't use
    # *    this definition of weight as a statement function
    # *    with some compilers is beyond me!
    # *  Smoothing is necessary to increase the error estimate
    # *    for some grossly under-estimated errors.
    # */
    for count in range(5):
        for i in range(1, n-1):
            w1 = math.pow(1 - math.fabs(1 - x[i-1]/x[i]) ,2)
            w2 = math.pow(1 - math.fabs(1 - x[i+1]/x[i]) ,2)
            dz[i] = (w1 * dz[i-1] + dz[i] + w2 * dz[i+1]) / (w1 + 1.0 + w2)
    return dz


def LinearInterpolation(x,x1,y1,x2,y2):
    ''':return: linear interpolation of y(x) from (x1,y1) and (x2,y2)'''
    return  (y1 + (y2-y1) * (x-x1) / (x2-x1))


def Plengt (x, slitlength):
    '''
    Here is the definition of the slit-length weighting function.
    It is defined for a rectangular slit of length 2*sLengt
    and probability 1/(2*sLengt).  It is zero elsewhere.
    
    It is not necessary to change the limit of the integration
    if the functional form here is changed.  You may, however,
    need to ask the user for more parameters.  Pass these
    around to the various routines through the use of the
    /PrepCm/ COMMON block.
    '''
    if math.fabs(x) > slitlength:
        value = 0
    else:
        value = 0.5 / slitlength
    return value


def Prep (x, y, dy, mForm, sFinal):
    '''
    Calculate the constants for an extrapolation fit
    from all the data that satisfy x(i) >= sFinal.
    '''
    NumPts = len(x)
    sr = StatsReg.StatsRegClass()
    for i in range(NumPts):
        if x[i] >= sFinal:
            if mForm == 1:
                sr.AddWeighted(x[i], y[i], dy[i])
            elif mForm == 1:
                sr.Add(x[i], y[i])
            elif mForm == 2:
                sr.Add(math.log(x[i]), math.log(y[i]))
            elif mForm == 3:
                h4 = math.pow(x[i], 4)
                sr.AddWeighted(h4, y[i]*h4, dy[i]*h4)
    if mForm == 1:
        fIntercept = sr.Mean()[0]
        fSlope = 0.0
    else:
        fIntercept, fSlope = sr.LinearRegression()
    return fIntercept, fSlope


def __main ():
    print(__doc__)

    InFile = os.path.join('..', '..', 'data', 'test1.smr')
    OutFil = 'test.dsm'
    sLengt = 0.08
    sFinal = 0.08
    NumItr = 10
    InfItr = 10000
    mForm = 2
    LakeForm = 2
    if len(InFile.strip()) == 0: return          # no file name given, so exit
    if (NumItr == 0): NumItr = InfItr;
    print("Input file: %s" % InFile)
    q, E, dE = toolbox.GetDat(InFile)
    NumPts = len(q)
    if NumPts == 0: raise Exception, "no data points"
    if sFinal > q[NumPts-1]: raise Exception, "sFinal > q[max]"
    #C, dC = [0]*NumPts, [0]*NumPts
    #S = DesmearData (OutFil, q, E, dE, sLengt, sFinal, mForm, NumItr, InfItr, LakeForm)
    DesmearData (OutFil, q, E, dE, sLengt, sFinal, mForm, NumItr, InfItr, LakeForm)


if __name__ == '__main__':
    __main()
