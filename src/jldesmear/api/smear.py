#!/usr/bin/env python

'''
Forward smearing

Smear *(q, I, dI)* data given to the routine :func:`~jldesmear.api.smear.Smear()`
using the slit-length weighting function :func:`~jldesmear.api.smear.Plengt()`.
The integration used below goes only over the slit length
(does not include either slit width or wavelength broadening).

For now, :func:`~jldesmear.api.smear.Plengt()` describes a rectangular slit
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


import math
import os                        #@UnusedImport
import sys
import toolbox
import extrapolation             #@UnusedImport
import extrap_linear             #@UnusedImport
import textplots
import pprint
import numpy
from scipy.interpolate import interp1d


def Plengt (l, slitlength):
    '''
    Slit-length weighting function, *P_l(l)*
    
    .. math::
    
        \int_{-\infty}^{\infty} P_l(l) dl = 1

    It is defined for a rectangular slit of length ``2*slitlength``
    (:math:`2l_o`)
    and probability ``1/(2*slitlength)`` (:math:`1/2l_o`).  
    It is zero elsewhere.::
    
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
    if isinstance(l, numpy.ndarray):
        n = len(l)
        zeroes = numpy.zeros((n,))
        p_l = 0.5 * numpy.ones((n,)) / slitlength
        result = numpy.where(numpy.abs(l) > slitlength, zeroes, p_l)
    elif math.fabs(l) > slitlength:
        result = 0
    else:
        result = 0.5 / slitlength
    return result


def prepare_extrapolation(q, C, dC, extrapname, sFinal):
    '''
    Pick the extrapolation function for smearing
    
    :param numpy.ndarray q: magnitude of scattering vector
    :param numpy.ndarray C: array (list) such that data is C(q) +/- dC(q)
    :param numpy.ndarray dC: estimated uncertainties of C
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

    functions = extrapolation.discover_extrapolation_functions()
    if extrapname not in functions.keys():
        msg = "did not identify extrapolation function: " + extrapname
        raise RuntimeError, msg
    extrap = functions[extrapname]()
    extrap.fit(q[start:-1], C[start:-1], dC[start:-1])
    return extrap


def Smear(q, C, dC, extrapname, sFinal, slitlength, quiet = False):
    '''
    Smear the data of C(q) into S(q) using the slit-length
    weighting function :func:`~jldesmear.api.smear.Plengt()` and an extrapolation
    of the data to avoid truncation errors.  Assume that
    :func:`~jldesmear.api.smear.Plengt()` goes to zero for ``l > l_o`` (the slit length).
    
    Also assume that the slit length function is symmetrical
    about ``l = zero``.
    
    .. math::

        S(q) = 2 \int_0^{l_o} P_l(l) \ C(\sqrt{q^2+l^2}) \ dl
    
    This routine is written so that if :func:`~jldesmear.api.smear.Plengt()` is changed
    (for example) to a Gaussian, that no further modification
    is necessary to the integration procedure.  That is,
    this routine will integrate the data out to "slitlength" (``l_o``).
    
    :param numpy.ndarray q: magnitude of scattering vector
    :param numpy.ndarray C: unsmeared data is C(q) +/- dC(q)
    :param numpy.ndarray dC: estimated uncertainties of C
    :param extrapname: one of ``constant | linear | powerlaw | Porod``
    :type extrapname: string
    :param float sFinal: fit extrapolation to I(q) for q >= sFinal
    :param float slitlength: l_o, same units as q
    :param bool quiet: if True, then no printed output from this routine
    :return: tuple of (S, extrap)
    :rtype: (numpy.ndarray, object)
    :var numpy.ndarray S: smeared version of C
    '''
    # make the slit-length weighting function
    NumPts = len(q)
    q0 = q[0]
    qMax = q[-1]
    qRange = qMax - q0
    x = slitlength * (q - q0) / qRange      # use "x" rather than "l" to avoid typos
    w = Plengt(x, slitlength)               # w = P_l(l) or P_l(x)

    # prepare for interpolation of existing data, log(I)
    interp = interp1d(q, numpy.log(C))

    # select and fit the extrapolation
    try:
        extrap = prepare_extrapolation(q, C, dC, extrapname, sFinal)
    except Exception:
        message = "prepare_extrapolation had a problem: " + str(sys.exc_info)
        raise Exception, message

    S = numpy.ndarray((NumPts,))     # slit-smeared intensity (to be the result)

    for i, qNow in enumerate(q):
        if not quiet: toolbox.Spinner(i)
        u = numpy.sqrt(qNow*qNow + x*x) # circular-symmetric

        # divide integrand into u<=qMax and u>qMax
        # interpolate from existing data
        u_in = numpy.array([uNow for uNow in u if uNow <= qMax])
        Ic_in = numpy.exp(interp(u_in))
        
        # extrapolate from model beyond range of available data
        u_ex = numpy.array([uNow for uNow in u if uNow > qMax])
        # TODO: let extrapolations support ndarrays
        Ic_ex = [extrap.calc(uNow) for uNow in u_ex]
        
        # join the two parts of the integrand
        Ic = w * numpy.concatenate((Ic_in, Ic_ex))
        
        S[i] = 2.0 * trapezoid_integration(x, Ic)   #x2: symmetrical about zero
    return S, extrap


def trapezoid_integration(x, y):
    '''
    integrate the area under the curve using trapezoid rule (from :meth:`numpy.trapz`)

    :param numpy.ndarray x: abcissae
    :param numpy.ndarray y: ordinates
    :return: area under the curve
    :rtype: float
    '''
    return numpy.trapz(y, x)


def __test_integrate():
    '''test trapezoid_integration()'''
    print("Testing trapezoid_integration()")
    print("%g ?= %g" % (2.0, trapezoid_integration( (1,2,3,4), (0., 1., 1., 0.) )))
    print("%g ?= %g" % (1.0, trapezoid_integration( (1,2,3), (0., 1., 0.) )))


def __test_Smear():
    '''test Smear()'''
    print("Testing Smear()")
    fn = toolbox.GetTest1DataFilename('.dsm')
    q, C, dC = toolbox.GetDat(fn)

    title = "\nPorod plot, I * q^4 vs q: C=input data"
    q4 = q*q*q*q
    q4I = q4 * C
    textplots.Screen().xyplot(q, q4I, title)

    try:
        S, extrap = Smear(q, C, dC, "constant", .08, .08, quiet=True)
    except Exception:
        print("Smearing failed")
        raise
    print(" Done.")

    # Could show a plot of extrapolation fitted to data

    coeff = extrap.GetCoefficients()
    pprint.pprint(coeff)
    B = coeff.get('B', 0.)
    q4I = q4 * (C - B)
    qS4I = q4 * (S - B)
    print("%s\t%s\t%s\t%s\t%s" % ("q", "C", "dC", "S", "dS"))
    NumPts = len(q)
    for i in range(NumPts):
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
    for key in sorted(coeff.keys()):
        if key in names.keys():
            print("coefficient: %s = %s" % (names[key], coeff[key]))

    # plot the data on log vs log
    powerplot = textplots.Screen()
    title = "\npower law plot, ln(I) vs ln(q): C=input, S=smeared"
    lnq = numpy.log(q)
    powerplot.addtrace(lnq, numpy.log(C), "C")
    powerplot.addtrace(lnq, numpy.log(S), "S")
    powerplot.SetTitle(title)
    powerplot.printplot()

    KratkyPlot = textplots.Screen()
    title = "\nKratky plot, I * q^2 vs q: S=smeared"

    KratkyPlot.SetTitle(title)
    KratkyPlot.addtrace(lnq, q*q*(S - B), "S")
    KratkyPlot.printplot()
    title = "\nKratky plot, I * q^2 vs q: C=input, S=smeared"
    KratkyPlot.SetTitle(title)
    KratkyPlot.addtrace(lnq, q*q*(C - B), "C")
    KratkyPlot.printplot()


def __test_Plengt():
    '''test Plengt()'''
    print("Plengt %s" % Plengt(-0.1, .5))
    print("Plengt %s" % Plengt(0, .5))
    print("Plengt %s" % Plengt(1.1, .5))
    print("Plengt %s" % Plengt(0.1, 3))
    print("Plengt %s" % Plengt(0.1, 3.))
    print("Plengt %s" % Plengt(numpy.array([0.01, 0.1, 0.2]), .1))


def __demo():
    '''show the various routines'''
    print("Testing $Id$")
    __test_Plengt()
    __test_integrate()
    __test_Smear()


if __name__ == "__main__":
    __demo()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
