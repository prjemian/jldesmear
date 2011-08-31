#!/usr/bin/env python

'''
$Id$

Credits
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:author: Pete R. Jemian
:organization: Late-Nite(tm) Software
:note: lake.py was derived from lake.c in 2009
:note: lake.c was derived from the FORTRAN program Lake.FOR
:note: Lake.FOR  25 May 1991
:see: P.R.Jemian,; Ph.D. thesis, Northwestern University (1990).
:see: J.A. Lake; ACTA CRYST 23 (1967) 191-194.

Overview
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

:caution:
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
up to ``l = lo``. (see module :mod:`lake.smear`).
This technique allows the slit-length weighting function
to be changed without regard to the limits of integration
coded into this program.

Other deconvolution methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These authors have presented desmearing/deconvolution methods 
that were considered or reviewed in the development of this work.

* O. Glatter.
  ACTA CRYST 7 (1974) 147-153.
* W.E. Blass & G.W.Halsey. (1981) 
  "Deconvolution of Absorption Spectra."
  New York City: Academic Press
* P.A. Jansson.
  (1984) "Deconvolution with Applications in Spectroscopy."
  New York City: Academic Press.
* G.W.Halsey & W.E. Blass.
  (1984)  "Deconvolution Examples" in 
  "Deconvolution with Applications in Spectroscopy."
  Ed. P.A. Jansson.  (see above)

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
import toolbox
import info
import desmear
import textplots
import os


INFINITE_ITERATIONS = 0


def GetInf(params):
    '''
    Get information about the desmearing parameters.
    This is designed to be independent of wavelength
    or radiation-type (i.e. neutrons, X rays, etc.)

    :param obj params: Desmearing parameters object
    :return: params or None
    '''
    params.infile = toolbox.AskString (
                            "What is the input data file name? <''=Quit>", params.infile)
    params.outfile = toolbox.AskString (
                            "What is the output data file name?", 
                            params.outfile)
    params.slitlength = toolbox.AskDouble (
                            "What is the slit length (x-axis units)?", 
                            params.slitlength)
    print (
          "Extrapolation forms to avoid truncation-error.\n"
        + "   constant = flat background, I(q) = B\n"
        + "   linear = linear, I(q) = b + q * m\n"
        + "   powerlaw = power law, I(q) = b * q^m\n"
        + "   Porod = Porod law, I(q) = Cp + Bkg / q^4\n"
    )
    params.extrapname = toolbox.AskString ("Which form?", params.extrapname)
    params.sFinal = toolbox.AskDouble (
                        "What X to begin evaluating extrapolation (x-axis units)?", 
                        params.sFinal);
    params.NumItr = abs(toolbox.AskInt ("How many iteration(s)? (0 = infinite)", 
                        params.NumItr))
    print (
          " Weighting methods for iterative corrections:\n"
        + " Correction = weight * (MeasuredI - SmearedI)\n"
        + "   constant: weight = 1.0\n"
        + "   fast: weight = CorrectedI / SmearedI\n"
        + "   ChiSqr: weight = 2*SQRT(ChiSqr(0) / ChiSqr(i))\n"
    )
    params.LakeWeighting = toolbox.AskString ("Which method?", params.LakeWeighting)
    return params


def callback (dsm):
    '''
    this function is called after every desmearing iteration
    from :func:`lake.desmear.Desmearing.traditional()`

    :param obj dsm: Desmearing object
    :return: should desmearing stop?
    :rtype: bool
    '''
    title = "\nstandardized residuals, ChiSqr = %g, iteration=%d" % (dsm.ChiSqr[-1], dsm.iteration_count)
    textplots.Screen().residualsplot(dsm.z, title)
    reply = "y"
    if dsm.params.NumItr == info.INFINITE_ITERATIONS:
        reply = toolbox.AskYesOrNo ("Continue?", reply)
        print("reply: <%s>" % reply)
    return reply == 'n'


def no_plotting_callback (dsm):
    '''
    this function is called after every desmearing iteration
    from :func:`lake.desmear.Desmearing.traditional()`

    :param obj dsm: Desmearing object
    :return: should desmearing stop?
    :rtype: bool
    '''
    print "#%d  ChiSqr=%g  %s" % (dsm.iteration_count, dsm.ChiSqr[-1], str(dsm.params.extrap))
    quit_requested = False
    if dsm.params.NumItr == info.INFINITE_ITERATIONS:
        reply = toolbox.AskYesOrNo ("Continue?", "y")
        print("reply: <%s>" % reply)
        quit_requested = reply.lower() == 'n'
    more_steps = dsm.params.moreIterationsOk(dsm.iteration_count)
    return quit_requested or not more_steps


def plot_results (q, E, C):
    '''
    plot the results of the desmearing
    
    :param [float] q: magnitude of scattering vector
    :param [float] E: experimental (smeared) data
    :param [float] C: corrected (desmeared) data
    '''
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


def traditional_command_line_interface ():
    '''
    SAS data desmearing, by Pete R. Jemian
    Based on the iterative technique of JA Lake and PR Jemian.
    P.R.Jemian,; Ph.D. thesis, Northwestern University (1990).
    J.A. Lake; ACTA CRYST 23 (1967) 191-194.
    
    ::
    
        $Id$
        desmear using the same FORTRAN & C command line interface
    '''
    # log output to "Lake.log"
    print(traditional_command_line_interface.__doc__)

    params = info.Info()
    if params == None:
        return          # no input file so quit the program

    params.infile = os.path.join('..', '..', 'data', 'test1.smr')
    params.outfile = "test.dsm"
    params.slitlength = 0.08
    params.sFinal = 0.08
    params.NumItr = 10
    params.extrapname = "linear"

    params = GetInf(params)
    if params == None:
        return          # no input file so quit the program

    if (params.NumItr == 0):
        params.NumItr = info.INFINITE_ITERATIONS;
    print("Input file: %s" % params.infile)
    q, E, dE = toolbox.GetDat(params.infile)
    if (len(q) == 0):
        raise Exception, "no data points!"
    if (params.sFinal > q[-1]):
        raise Exception, "Fit range out of data range"

    reply = toolbox.AskYesOrNo ("Plot intermediate residuals?", "y")
    choices = {True: callback, False: no_plotting_callback}
    params.callback = choices[ reply.lower() == "y" ]

    dsm = desmear.Desmearing(q, E, dE, params)
    
    if params.NumItr == info.INFINITE_ITERATIONS:
        dsm.traditional()
    else:
        for i in range(params.NumItr):
            dsm.iteration()
            params.callback(dsm)
    toolbox.SavDat(params.outfile, q, dsm.C, dsm.dC)
    plot_results(q, E, dsm.C)


if __name__ == '__main__':
    traditional_command_line_interface()
