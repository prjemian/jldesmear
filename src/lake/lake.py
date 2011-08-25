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
import pprint
import desmear
import textplots
import os


INFINITE_ITERATIONS = 10000


def GetInf(info):
    '''
    Get information about the desmearing parameters.
    This is designed to be independent of wavelength
    or radiation-type (i.e. neutrons, X rays, etc.)

    :param dict info: dictionary of input terms by keyword
    :return: info dictionary or None
    '''
    info["infile"] = toolbox.AskString (
                            "What is the input data file name? <''=Quit>", "")
    if len(info["infile"]) == 0:
        return None
    info["outfile"] = toolbox.AskString (
                            "What is the output data file name?", 
                            info["outfile"])
    info["slitlength"] = toolbox.AskDouble (
                            "What is the slit length (x-axis units)?", 
                            info["slitlength"])
    print (
          "Extrapolation forms to avoid truncation-error.\n"
        + "   constant = flat background, I(q) = B\n"
        + "   linear = linear, I(q) = b + q * m\n"
        + "   powerlaw = power law, I(q) = b * q^m\n"
        + "   Porod = Porod law, I(q) = Cp + Bkg / q^4\n"
    )
    info["extrapname"] = toolbox.AskString ("Which form?", info["extrapname"])
    info["sFinal"] = toolbox.AskDouble (
                        "What X to begin evaluating extrapolation (x-axis units)?", 
                        info["sFinal"]);
    info["NumItr"] = toolbox.AskInt ("How many iteration(s)? (10000 = infinite)", 
                        info["NumItr"])
    print (
          " Weighting methods for iterative corrections:\n"
        + " Correction = weight * (MeasuredI - SmearedI)\n"
        + "   constant: weight = 1.0\n"
        + "   fast: weight = CorrectedI / SmearedI\n"
        + "   ChiSqr: weight = 2*SQRT(ChiSqr(0) / ChiSqr(i))\n"
    )
    info["LakeWeighting"] = toolbox.AskString ("Which method?", info["LakeWeighting"])
    return info


def callback (q, I, dI, C, S, iteration, ChiSqr, info, extrap):
    '''
    this function is called after every desmearing iteration
    from :func:`lake.desmear.Desmear()`

    :param [float] q: magnitude of scattering vector
    :param [float] I: SAS data I(q) +/- dI(q)
    :param [float] dI: estimated uncertainties of I(q)
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
    title = "\nstandardized residuals, ChiSqr = %g, iteration=%d" % (ChiSqr, iteration)
    textplots.Screen().residualsplot(z, title)
    reply = "y"
    if info["NumItr"] < 0:
        reply = toolbox.AskYesOrNo ("Continue?", reply)
        print("reply: <%s>" % reply)
    return reply == 'n'


def no_plotting_callback (q, I, dI, C, S, iteration, ChiSqr, info, extrap):
    '''
    this function is called after every desmearing iteration
    from :func:`lake.desmear.Desmear()`

    :param [float] q: magnitude of scattering vector
    :param [float] I: SAS data I(q) +/- dI(q)
    :param [float] dI: estimated uncertainties of I(q)
    :param [float] S: array (list) of smeared intensity
    :param [float] C: array (list) of corrected intensity
    :param int iteration: iteration number
    :param float ChiSqr: Chi-Squared value
    :param dict info: dictionary of input parameters
    :param object extrap: extrapolation function structure
    :return: should desmearing stop?
    :rtype: bool
    '''
    print "#%d  ChiSqr=%g  %s" % (iteration+1, ChiSqr, str(extrap))
    return iteration+1 == info["NumItr"]


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


def print_results (q, E, dE, C, dC):
    '''
    print the results of the desmearing
    
    :param [float] q: magnitude of scattering vector
    :param [float] E: experimental (smeared) data
    :param [float] dE: estimated uncertainties of *E*
    :param [float] C: corrected (desmeared) data
    :param [float] dC: estimated uncertainties of *C*
    '''
    print "%s\t%s\t%s\t%s\t%s" % ( 
            "Qsas",
            "Isas",
            "Idev",
            "Idsm",
            "IdsmDev"
    )
    for i in range(len(q)):
        print "%g\t%g\t%g\t%g\t%g" % (
                q[i],
                C[i],
                dC[i],
                E[i],
                dE[i]
        )


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

    info = {                # set the defaults
        "infile": "", 
        "outfile": "",
        "slitlength": 1.0,              # s: slit length, as defined by Lake
        "sFinal": 1.0,                  # fit extrapolation constants for q>=sFinal
        "NumItr": INFINITE_ITERATIONS,  # number of desmearing iterations
        "extrapname": "constant",       # model final data as a constant
        "LakeWeighting": "fast",        # shows the fastest convergence most times
    }

    info = GetInf(info)

    if info == None:
        return          # no input file so quit the program
    if (info["NumItr"] == 0):
        info["NumItr"] = INFINITE_ITERATIONS;
    print("Input file: %s" % info["infile"])
    q, E, dE = toolbox.GetDat(info["infile"])
    if (len(q) == 0):
        raise Exception, "no data points!"
    if (info["sFinal"] > q[-1]):
        raise Exception, "Fit range out of data range"
    C, dC = desmear.Desmear(q, E, dE, info, callback, False)
    toolbox.SavDat(info["outfile"], q, C, dC)
    plot_results(q, E, C)


def developmental_commandline_interface ():
    '''
    SAS data desmearing, by Pete R. Jemian
    Based on the iterative technique of JA Lake and PR Jemian.
    P.R.Jemian,; Ph.D. thesis, Northwestern University (1990).
    J.A. Lake; ACTA CRYST 23 (1967) 191-194.
    
    $Id$
    desmear using the interface from the developmental Java version
    
    :note: This interface is not ready for production yet.
    '''
    # log output to "Lake.log"
    print(developmental_commandline_interface.__doc__)

    # TODO: must pass this info to this method.
    info = {                # set the defaults
        "infile": os.path.join('..', '..', 'data', 'test1.smr'), 
        "outfile": "test1.dsm",
        "slitlength": 0.08,             # s: slit length, as defined by Lake
        "sFinal": 0.08,                 # fit extrapolation constants for q>=sFinal
        "NumItr": 10,                   # number of desmearing iterations
        "extrapname": "constant",       # model final data as a constant
        "LakeWeighting": "fast",        # shows the fastest convergence most times
    }

    # TODO: implement GetInf() method and remove info = {...} definition above
    #info = GetInf(info)

    if info == None:
        return          # no input file so quit the program
    if (info["NumItr"] == 0):
        info["NumItr"] = INFINITE_ITERATIONS;
    print("Input file: %s" % info["infile"])
    q, E, dE = toolbox.GetDat(info["infile"])
    if (len(q) == 0):
        raise Exception, "no data points!"
    if (info["sFinal"] > q[-1]):
        raise Exception, "Fit range out of data range"
    print "Input data accepted.  Parameters are:"
    pprint.pprint( info )
    print "Desmearing..."
    # no_plotting_callback | callback
    C, dC = desmear.Desmear(q, E, dE, info, no_plotting_callback, True)
    print "Desmearing complete"
    print "Saving desmeared data to: %s" % info["outfile"]
    toolbox.SavDat(info["outfile"], q, C, dC)
    print "Plotting results..."
    plot_results(q, E, C)
    print "Printing results..."
    print_results (q, E, dE, C, dC)
    print "the end."


if __name__ == '__main__':
    traditional_command_line_interface()
    #developmental_commandline_interface()
    # gnuplot command
    #  plot "test.dsm" using 1:2, "../../data/test1.dsm" using 1:2, "../../data/test1.smr" using 1:2
