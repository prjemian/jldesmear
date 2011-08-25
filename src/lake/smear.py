#!/usr/bin/env python

'''
$Id$

Smear *(q, I, dI)* data given to the routine :func:`lake.smear.Smear()`
using the slit-length weighting function :func:`lake.smear.Plengt()`.
The integration used below goes only over the slit length
(does not include either slit width or wavelength broadening).

For now, :func:`lake.smear.Plengt()` describes a rectangular slit
and the integration extends up to the length of the slit.
This could be changed if desired.

To complete the smearing for the last data points, extrapolation
is necessary from the given data.   The functional form may be 
only one of those provided (others could be added).  

For *q* values in between given data points, interpolation is 
used.  Log interpolation is tried first.  If this fails due 
to a ValueError Exception, linear interpolation is used.

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
import os
import sys
import toolbox
import extrap_constant
import extrap_linear
import extrap_power
import extrap_porod
import textplots
import pprint


def Plengt (l, slitlength):
    '''
    Slit-length weighting function, *P_l(l)*
    
    .. math::
    
        \int_{-\infty}^{\infty} P_l(l) dl = 1

    It is defined for a rectangular slit of length ``2*slitlength``
    and probability ``1/(2*slitlength)``.  It is zero elsewhere.::
    
                            P(l)
        /--------------------|--------------------\\
        |                    |                    |
        |                    |                    |
        |      *****************************      | 1/2l_o
        |      *             |             *      |
        |      *             |             *      |
        |      *             |             *      |
        \*******-------------|-------------*******/ 0
              -l_o           0            l_o
    
    :note: integral( P(l) dl ) = 1.0


    :note: If you change this to a different functional form ...
        It is not necessary to change the limit of the integration
        if the functional form here is changed.  You may, however,
        need more parameters.

    :param float l: lookup value
    :param float slitlength: slit length, *l_o,* as indicated above
    :return: P_l(l)
    :rtype: float
    '''
    if math.fabs(l) > slitlength:
        result = 0
    else:
        result = 0.5 / slitlength;
    return result


def FindIc (x, y, q, C, extrap):
    '''
    Determine the "corrected" intensity at *u = SQRT (x*x + y*y)*
    Note that only positive values of *u* will be searched!
    
    :param float x: l_now
    :param float y: q_now
    :param [float] q: magnitude of scattering vector
    :param [float] C: intensity values: I(q)
    :param extrap: (Extrapolation object) functional form of fit
    :return: I(x,y)
    :rtype: float
    '''
    u = math.sqrt(x*x + y*y)                    # circularly symmetric
    (result, iTest) = toolbox.BSearch (u, q)    # find index
    if not result:
        if iTest == -1:                 # u < q range
            # u < q[0]: cannot interpolate or extrapolate
            message = "FindIc(): u < q[0]: cannot interpolate or extrapolate"
            raise Exception, message
    #iLo = iTest - 1;        # why the offset?
    iLo = iTest;
    iHi = iLo + 1;
    if iTest < len(q)-1:                # u within q range
        if u == q[iLo]:
            value = C[iLo]              # exact value
        else:
            try:
                value = toolbox.log_interpolation(u, 
                            q[iLo],C[iLo], q[iHi],C[iHi])
            except ValueError:          # fallback (if negative intensities)
                value = toolbox.linear_interpolation(u, 
                            q[iLo],C[iLo], q[iHi],C[iHi])
    else:                               # u > q range
        value = extrap.calc(u)          # functional extrapolation
    return value


def prepare_extrapolation(q, C, dC, extrapname, sFinal):
    '''
    Pick the extrapolation function for smearing
    
    :param [float] q: magnitude of scattering vector
    :param [float] C: array (list) such that data is C(q) +/- dC(q)
    :param [float] dC: estimated uncertainties of C
    :param str extrapname: one of ``constant``, ``linear``, ``powerlaw``, or ``Porod``
    :param float sFinal: fit extrapolation to I(q) for q >= sFinal
    :return: function object of selected extrapolation
    :rtype: object
    '''
    if sFinal > q[-1]:
        raise Exception, "no data to fit extrapolation"
    for i in range(len(q)):
        start = i
        if q[i] > sFinal:
            break
    if len(q) - start < 2:
        raise Exception, "not enough data to fit"
    # identify extrapolation function
    functions = {
         "constant": extrap_constant.Constant,
         "linear": extrap_linear.Linear,
         "powerlaw": extrap_power.Power,
         "Porod": extrap_porod.Porod
    }
    if extrapname not in functions.keys():
        raise Exception, "did not identify extrapolation function"
    extrap = functions[extrapname]()
    extrap.fit(q[start:-1], C[start:-1], dC[start:-1])
    return extrap


def Smear(q, C, dC, extrapname, sFinal, slitlength, quiet = False):
    '''
    Smear the data of C(q) into S(q) using the slit-length
    weighting function :func:`lake.smear.Plengt()` and an extrapolation
    of the data to avoid truncation errors.  Assume that
    :func:`lake.smear.Plengt()` goes to zero for ``l > l_o`` (the slit length).
    
    Also assume that the slit length function is symmetrical
    about ``l = zero``.
    
    .. math::

        S(q) = 2 \int_0^{l_o} P_l(l) \ C(\sqrt{q^2+l^2}) \ dl
    
    This routine is written so that if :func:`lake.smear.Plengt()` is changed
    (for example) to a Gaussian, that no further modification
    is necessary to the integration procedure.  That is,
    this routine will integrate the data out to "slitlength" (``l_o``).
    
    :param [float] q: magnitude of scattering vector
    :param [float] C: unsmeared data is C(q) +/- dC(q)
    :param [float] dC: estimated uncertainties of C
    :param extrapname: one of ``constant | linear | powerlaw | Porod``
    :type extrapname: string
    :param float sFinal: fit extrapolation to I(q) for q >= sFinal
    :param float slitlength: l_o, same units as q
    :param bool quiet: if True, then no printed output from this routine
    :return: tuple of (S, extrap)
    :rtype: ([float], object)
    :var [float] S: smeared version of C
    '''
    # make the slit-length weighting function
    NumPts = len(q)
    x = [0.]*NumPts      # use "x" rather than "l" to avoid typos
    w = [0.]*NumPts      # w = P_l(l) or P_l(x)
    for i in range(NumPts):
        x[i] = slitlength * (q[i] - q[0])/(q[-1] - q[0])
        w[i] = Plengt(x[i], slitlength)

    # select and fit the extrapolation
    try:
        extrap = prepare_extrapolation(q, C, dC, extrapname, sFinal)
    except Exception:
        message = "prepare_extrapolation had a problem: " + str(sys.exc_info)
        raise Exception, message

    # calculate the slit-smearing
    S = [0.]*NumPts     # slit-smeared intensity (to be the result)
    Ic = [0.]*NumPts    # integrand for the smearing integral
    for i in range(NumPts):
        if not quiet:
            toolbox.Spinner(i)
        qNow = q[i]
        for k in range(NumPts):
            Ic[k] = w[k] * FindIc (qNow, x[k], q, C, extrap)
        S[i] = 2.0 * trapezoid_integration(x, Ic)   #x2: symmetrical about zero
    return S, extrap


def trapezoid_integration(x, y):
    '''
    integrate the area under the curve using trapezoid rule
    
    .. math::
    
        \sum_{i=2}^N (x_i - x_{i-1}) (y_i + y_{i-1})/2

    :param [float] x: abcissae
    :param [float] y: ordinates
    :return: area under the curve
    :rtype: float
    '''
    area = 0
    for i in range(1, len(x)):
        area += (x[i] - x[i-1]) * (y[i] + y[i-1])
    return area/2


def __test_FindIc():
    '''test FindIc()'''
    print("test of FindIc")
    q, C, dC = toolbox.GetDat(os.path.join('..', '..', 'data', 'test1.dsm'))
    start = toolbox.find_first_index(q, 0.08)
    print('q[%d:]=%s' % (start, q[start:-1]))
    extrap = extrap_linear.Linear()
    extrap.fit(q[start:-1], C[start:-1], dC[start:-1])
    num_tests = 200
    x, y = [0]*num_tests, [0]*num_tests
    i1 = 170
    i2 = i1+5
    print("qNow\tInow (test of FindIc())")
    for i in range(num_tests):
        qNow = q[i1] + i*(q[i2]-q[i1])/num_tests
        Inow = FindIc(0, qNow, q, C, extrap)
        print("%g\t%g" % (qNow, Inow))
        x[i] = qNow
        y[i] = Inow
    title = "\nplot of interpolated data, Ic(q), *=data, O=interpolates"
    xy = textplots.Screen()
    xy.addtrace(x, y, "O")
    xy.addtrace(q[i1:i2+1], C[i1:i2+1], "*")
    xy.SetTitle(title)
    xy.printplot()


def __test_integrate():
    '''test trapezoid_integration()'''
    print("Testing trapezoid_integration()")
    print("%g ?= %g" % (2.0, trapezoid_integration( (1,2,3,4), (0., 1., 1., 0.) )))
    print("%g ?= %g" % (1.0, trapezoid_integration( (1,2,3), (0., 1., 0.) )))


def __test_Smear():
    '''test Smear()'''
    print("Testing Smear()")
    q, C, dC = toolbox.GetDat(os.path.join('..', '..', 'data', 'test1.dsm'))

    title = "\nPorod plot, I * q^4 vs q: C=input data"
    NumPts = len(q)
    q4, q4I = [0]*NumPts, [0]*NumPts
    for i in range(NumPts):
        q4[i] = math.pow(q[i],4)
        q4I[i] = C[i]*q4[i]
    textplots.Screen().xyplot(q, q4I, title)

    try:
        # S, extrap = Smear(q, C, dC, "Porod", .01, .04)
        S, extrap = Smear(q, C, dC, "constant", .08, .08)
    except Exception, e:
        print("")
        raise Exception, "Smearing failed: " + e
    print(" Done.")

    # Could show a plot of extrapolation fitted to data

    coeff = extrap.GetCoefficients()
    pprint.pprint(coeff)
    B = 0
    if 'B' in coeff.keys():
        B = coeff['B']
    qS4I = [0]*NumPts
    print("%s\t%s\t%s\t%s\t%s" % ("q", "C", "dC", "S", "dS"))
    for i in range(NumPts):
        q4I[i] = (C[i] - B)*q4[i]
        qS4I[i] = (S[i] - B)*q4[i]
        print("%g\t%g\t%g\t%g\t%g" % (q[i], C[i], dC[i], S[i], dC[i]*S[i]/C[i]))
    plot = textplots.Screen()
    title = "Porod plot, I * q^4 vs q: C=input (background subtracted)"
    plot.addtrace(q, q4I, "C")

    plot.SetTitle(title)
    plot.printplot()
    plot.addtrace(q, qS4I, "S")

    title = "Porod plot, I * q^4 vs q: C=input, S=smeared (background subtracted)"
    plot.SetTitle(title)
    plot.printplot()

    names = {
    	"B": "B (constant background)",
    	"m": "m (linear slope)",
    	"A": "A (power law scale factor)",
    	"p": "p (power law exponent)",
    	"Cp": "Cp (Porod constant)"
    }
    for key in names.keys():
        if key in coeff.keys():
            print("coefficient: %s = %s" % (names[key], coeff[key]))

    # plot the data on log vs log
    powerplot = textplots.Screen()
    title = "\npower law plot, ln(I) vs ln(q): C=input, S=smeared"
    lnq, lnC, lnS = [0]*NumPts, [0]*NumPts, [0]*NumPts
    for i in range(NumPts):
        lnq[i] = math.log(q[i])
        lnC[i] = math.log(C[i])
        lnS[i] = math.log(S[i])
    powerplot.addtrace(lnq, lnC, "C")
    powerplot.addtrace(lnq, lnS, "S")
    powerplot.SetTitle(title)
    powerplot.printplot()

    KratkyPlot = textplots.Screen()
    title = "\nKratky plot, I * q^2 vs q: S=smeared"
    q2C, q2S = [0]*NumPts, [0]*NumPts
    for i in range(NumPts):
        q2C[i] = q[i]*q[i]*(C[i] - B)
        q2S[i] = q[i]*q[i]*(S[i] - B)
    KratkyPlot.SetTitle(title)
    KratkyPlot.addtrace(lnq, q2S, "S")
    KratkyPlot.printplot()
    title = "\nKratky plot, I * q^2 vs q: C=input, S=smeared"
    KratkyPlot.SetTitle(title)
    KratkyPlot.addtrace(lnq, q2C, "C")
    KratkyPlot.printplot()


def __test_Plengt():
    '''test Plengt()'''
    print("Plengt %s" % Plengt(-0.1, .5))
    print("Plengt %s" % Plengt(0, .5))
    print("Plengt %s" % Plengt(1.1, .5))
    print("Plengt %s" % Plengt(0.1, 3))
    print("Plengt %s" % Plengt(0.1, 3.))


def __demo():
    '''show the various routines'''
    print("Testing $Id$")
    __test_Plengt()
    __test_FindIc()
    __test_integrate()
    __test_Smear()


if __name__ == "__main__":
    __demo()
